
import os
import asyncio
import httpx
import time
import logging
import multiprocessing
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from concurrent.futures import ProcessPoolExecutor
from lxml import html

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('brave_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Retrieve Brave API key
brave_api_key = os.getenv("BRAVE_API_KEY")

class QuickResponseGenerator:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_KEY")
        if not self.openai_api_key:
            raise ValueError("API key is required. Set environment variable.")
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)

    def _prepare_search_payload(self, user_query: str, search_results: List[Dict]) -> str:
        payload = f"# User Query: {user_query}\n\n"
        for i, result in enumerate(search_results, 1):
            payload += f"## Result {i}\n"
            payload += f"### Title: {result.get('title', 'N/A')}\n"
            payload += f"### URL: {result.get('url', 'N/A')}\n"
            payload += f"### Description: {result.get('description', 'N/A')}\n"
            content = result.get('site_content') or result.get('description', 'No detailed content available')
            payload += f"### Content:\n{content}\n\n"
        return payload

    async def quick_llm_response(
        self, 
        user_query: str, 
        search_results: List[Dict], 
        system_prompt: Optional[str] = None,
        max_tokens: int = 150
    ) -> str:
        payload = self._prepare_search_payload(user_query, search_results)
        default_system_prompt = (
            "You are an expert research assistant. Given the user's original query "
            "and a set of search results, provide a comprehensive, super concise, and "
            "accurate response that directly addresses the user's information needs. "
            "Synthesize information from multiple sources, highlight key insights, "
            "and present the most relevant information in a clear, structured manner. "
            "Never use bullet points, only sentences."
        )
        messages = [
            {"role": "system", "content": system_prompt or default_system_prompt},
            {"role": "user", "content": f"User's Original Query: {user_query}\n\nSearch Results Payload:\n{payload}"}
        ]
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.5,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return "I apologize, but I couldn't generate a comprehensive response at this time."

    async def comprehensive_url_summary(self, url: str, content: str, query: str) -> Dict:
        """
        Generate a comprehensive summary for a single URL's content.
        """
        system_prompt = (
            "You are an expert summarizer. Given the content from a URL and the user's query, "
            "connect the dots by providing a detailed summary of the content, "
            "focusing on aspects relevant to the query. Include key details, insights, and nuances, "
            "ensuring the summary is thorough and informative."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {query}\n\nContent: {content}"}
        ]
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.5,
                max_tokens=150
            )
            return {
                "url": url,
                "summary": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"Error summarizing URL {url}: {e}")
            return {"url": url, "summary": "Unable to summarize due to an error."}

def clean_html_content(html_content: str) -> str:
    try:
        doc = html.fromstring(html_content)
        for elem in doc.xpath('//script|//style|//nav|//header|//footer|//menu'):
            elem.getparent().remove(elem)
        text = doc.text_content()
        text = ' '.join(text.split())
        return text  # Keep limit for quick mode, adjust for comprehensive if needed
    except Exception as e:
        logger.error(f"Error cleaning HTML content: {e}")
        return ""

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Maximum number of results to return")
    country: str = Field("US", description="Search country")
    safesearch: str = Field("moderate", description="Safe search setting: off, moderate, strict")

class BraveSearchClient:
    def __init__(self, api_key: Optional[str] = None, max_connections: int = None):
        self.api_key = api_key or brave_api_key
        max_connections = max_connections or (multiprocessing.cpu_count() * 2)
        self.http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=max_connections,
                max_connections=max_connections
            ),
            timeout=httpx.Timeout(10.0),
            follow_redirects=True
        )
        self.process_pool = ProcessPoolExecutor(max_workers=max_connections)

    async def scrape_url(self, url: str, timeout: float = 3.0) -> Optional[str]:
        start_time = time.time()
        try:
            response = await self.http_client.get(
                url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                },
                timeout=timeout
            )
            response.raise_for_status()
            http_time = time.time() - start_time
            logger.info(f"HTTP Request Time for {url}: {http_time:.4f} seconds")

            loop = asyncio.get_running_loop()
            cleaned_content = await loop.run_in_executor(
                self.process_pool,
                clean_html_content,
                response.text
            )
            total_scrape_time = time.time() - start_time
            logger.info(f"Total Scrape Time for {url}: {total_scrape_time:.4f} seconds")
            return cleaned_content
        except Exception as e:
            logger.error(f"Scrape error for {url}: {e}")
            return None

    async def text_search(self, input: SearchInput) -> List[Dict]:
        start_time = time.time()
        try:
            response = await self.http_client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={
                    "q": input.query,
                    "country": input.country,
                    "safesearch": input.safesearch,
                    "count": input.max_results
                },
                headers={"X-Subscription-Token": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("web", {}).get("results", [])

            sem = asyncio.Semaphore(10)
            async def safe_scrape(url):
                async with sem:
                    return await self.scrape_url(url)

            site_contents = await asyncio.gather(
                *[safe_scrape(result.get('url', '')) for result in results],
                return_exceptions=True
            )
            for i, content in enumerate(site_contents):
                if not isinstance(content, Exception) and content:
                    results[i]['site_content'] = content

            total_time = time.time() - start_time
            logger.info(f"Total Search Time: {total_time:.4f} seconds")
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def close(self):
        await self.http_client.aclose()
        self.process_pool.shutdown(wait=True)

class SRSWTIQuickOne:
    def __init__(self, max_results: int = 5):
        self.brave_client = BraveSearchClient()
        self.response_generator = QuickResponseGenerator()
        self.max_results = max_results

    async def __call__(self, query: str) -> str:
        search_input = SearchInput(
            query=query, 
            max_results=self.max_results,
            country="US",
            safesearch="moderate"
        )
        search_results = await self.brave_client.text_search(search_input)

        if self.max_results > 15:
            # Comprehensive mode: Generate detailed summaries for each URL
            summary_tasks = [
                self.response_generator.comprehensive_url_summary(
                    result.get('url', 'N/A'),
                    result.get('site_content', result.get('description', 'No content')),
                    query
                )
                for result in search_results
            ]
            detailed_summaries = await asyncio.gather(*summary_tasks)
            
            # Prepare comprehensive payload
            comprehensive_results = [
                {
                    "title": result.get('title', 'N/A'),
                    "url": result.get('url', 'N/A'),
                    "description": result.get('description', 'N/A'),
                    "site_content": summary.get('summary', 'No detailed summary available')
                }
                for result, summary in zip(search_results, detailed_summaries)
            ]
            
            # Use a comprehensive system prompt
            comprehensive_prompt = (
                "Alright, picture yourself as a top-notch research assistant, ready to dive deep into the details. "
                "You've got the user's query and these rich summaries from various search results. Your job? "
                "Weave them into a narrative that really connects the dots. Take your time, pause, and think about "
                "the in-depth insights, key details, and how they compare across sources. Provide an analysis that "
                "captures the essence of the topic. Make sure your response is well-structured, covering all relevant "
                "aspects with precision and depth. It's all about sentences, no bullet points, just a seamless story."
            )
            response = await self.response_generator.quick_llm_response(
                user_query=query,
                search_results=comprehensive_results,
                system_prompt=comprehensive_prompt,
                max_tokens=300  # Increased for comprehensive summary
            )
        else:
            # Standard quick mode
            response = await self.response_generator.quick_llm_response(
                user_query=query,
                search_results=search_results
            )
        
        return response

async def main():
    # Test with max_results > 15 for comprehensive mode
    # quick_one_deep = SRSWTIQuickOne(max_results=20)
    # result_deep = await quick_one_deep("how many h20s and h800s were smuggled from singapore to china for aklged deepseek model trianing")
    # print("Deep Search Result (max_results=20):")
    # print(result_deep)
    
    # Test with max_results <= 15 for quick mode
    quick_one_quick = SRSWTIQuickOne(max_results=3)
    result_quick = await quick_one_quick("how many h20s and h800s were smuggled from singapore to china for aklged deepseek model trianing")
    print("\nQuick Search Result (max_results=3):")
    print(result_quick)

if __name__ == "__main__":
    asyncio.run(main())




# import os
# import asyncio
# import httpx
# import time
# import logging
# import multiprocessing
# from openai import AsyncOpenAI
# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional
# from concurrent.futures import ProcessPoolExecutor
# from lxml import html

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO, 
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('brave_search.log'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# # Retrieve Brave API key
# brave_api_key = os.getenv("BRAVE_API_KEY")

# class QuickResponseGenerator:
#     def __init__(self, openai_api_key: Optional[str] = None):
#         self.openai_api_key = openai_api_key or os.getenv("OPENAI_KEY")
#         if not self.openai_api_key:
#             raise ValueError("API key is required. Set environment variable.")
#         self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)

#     def _prepare_search_payload(self, user_query: str, search_results: List[Dict]) -> str:
#         payload = f"# User Query: {user_query}\n\n"
#         for i, result in enumerate(search_results, 1):
#             payload += f"## Result {i}\n"
#             payload += f"### Title: {result.get('title', 'N/A')}\n"
#             payload += f"### URL: {result.get('url', 'N/A')}\n"
#             payload += f"### Description: {result.get('description', 'N/A')}\n"
#             content = result.get('site_content') or result.get('description', 'No detailed content available')
#             payload += f"### Content:\n{content}\n\n"
#         return payload

#     async def quick_llm_response(
#         self, 
#         user_query: str, 
#         search_results: List[Dict], 
#         system_prompt: Optional[str] = None
#     ) -> str:
#         payload = self._prepare_search_payload(user_query, search_results)
#         default_system_prompt = (
#             "You are an expert research assistant. Given the user's original query "
#             "and a set of search results, provide a comprehensive, super concise, and "
#             "accurate response that directly addresses the user's information needs. "
#             "Synthesize information from multiple sources, highlight key insights, "
#             "and present the most relevant information in a clear, structured manner. "
#             "Never use bullet points, only sentences."
#         )
#         messages = [
#             {"role": "system", "content": system_prompt or default_system_prompt},
#             {"role": "user", "content": f"User's Original Query: {user_query}\n\nSearch Results Payload:\n{payload}"}
#         ]
#         try:
#             response = await self.openai_client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=messages,
#                 temperature=0.5,
#                 max_tokens=150
#             )
#             return response.choices[0].message.content
#         except Exception as e:
#             print(f"Error generating LLM response: {e}")
#             return "I apologize, but I couldn't generate a comprehensive response at this time."

# def clean_html_content(html_content: str) -> str:
#     try:
#         doc = html.fromstring(html_content)
#         for elem in doc.xpath('//script|//style|//nav|//header|//footer|//menu'):
#             elem.getparent().remove(elem)
#         text = doc.text_content()
#         text = ' '.join(text.split())
#         return text[:800]
#     except Exception as e:
#         logger.error(f"Error cleaning HTML content: {e}")
#         return ""

# class SearchInput(BaseModel):
#     query: str = Field(..., description="Search query")
#     max_results: int = Field(10, description="Maximum number of results to return")
#     country: str = Field("US", description="Search country")
#     safesearch: str = Field("moderate", description="Safe search setting: off, moderate, strict")

# class BraveSearchClient:
#     def __init__(self, api_key: Optional[str] = None, max_connections: int = None):
#         self.api_key = api_key or brave_api_key
#         max_connections = max_connections or (multiprocessing.cpu_count() * 2)
#         self.http_client = httpx.AsyncClient(
#             limits=httpx.Limits(
#                 max_keepalive_connections=max_connections,
#                 max_connections=max_connections
#             ),
#             timeout=httpx.Timeout(10.0),
#             follow_redirects=True
#         )
#         self.process_pool = ProcessPoolExecutor(max_workers=max_connections)

#     async def scrape_url(self, url: str, timeout: float = 3.0) -> Optional[str]:
#         start_time = time.time()
#         try:
#             http_start_time = time.time()
#             response = await self.http_client.get(
#                 url, 
#                 headers={
#                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
#                 },
#                 timeout=timeout
#             )
#             response.raise_for_status()
#             http_time = time.time() - http_start_time
#             logger.info(f"HTTP Request Time for {url}: {http_time:.4f} seconds")

#             loop = asyncio.get_running_loop()
#             clean_start_time = time.time()
#             cleaned_content = await loop.run_in_executor(
#                 self.process_pool,
#                 clean_html_content,
#                 response.text
#             )
#             clean_time = time.time() - clean_start_time
#             logger.info(f"Content Cleaning Time for {url}: {clean_time:.4f} seconds")

#             total_scrape_time = time.time() - start_time
#             logger.info(f"Total Scrape Time for {url}: {total_scrape_time:.4f} seconds")
#             return cleaned_content
#         except Exception as e:
#             logger.error(f"Scrape error for {url}: {e}")
#             return None

#     async def text_search(self, input: SearchInput) -> List[Dict]:
#         start_time = time.time()
#         try:
#             api_start_time = time.time()
#             response = await self.http_client.get(
#                 "https://api.search.brave.com/res/v1/web/search",
#                 params={
#                     "q": input.query,
#                     "country": input.country,
#                     "safesearch": input.safesearch,
#                     "count": input.max_results
#                 },
#                 headers={"X-Subscription-Token": self.api_key}
#             )
#             response.raise_for_status()
#             api_time = time.time() - api_start_time
#             logger.info(f"API Call Time: {api_time:.4f} seconds")

#             data = response.json()
#             results = data.get("web", {}).get("results", [])

#             sem = asyncio.Semaphore(10)
#             async def safe_scrape(url):
#                 async with sem:
#                     return await self.scrape_url(url)

#             scrape_start_time = time.time()
#             site_contents = await asyncio.gather(
#                 *[safe_scrape(result.get('url', '')) for result in results],
#                 return_exceptions=True
#             )
#             scrape_time = time.time() - scrape_start_time
#             logger.info(f"Total Scrape Time: {scrape_time:.4f} seconds")

#             for i, content in enumerate(site_contents):
#                 if not isinstance(content, Exception) and content:
#                     results[i]['site_content'] = content

#             total_time = time.time() - start_time
#             logger.info(f"Total Search Time: {total_time:.4f} seconds")
#             return results
#         except Exception as e:
#             logger.error(f"Search error: {e}")
#             return []

#     async def close(self):
#         await self.http_client.aclose()
#         self.process_pool.shutdown(wait=True)

# class SRSWTIQuickOne:
#     def __init__(self, max_results: int = 5):
#         self.brave_client = BraveSearchClient()
#         self.response_generator = QuickResponseGenerator()
#         self.max_results = max_results

#     async def __call__(self, query: str) -> str:
#         search_input = SearchInput(
#             query=query, 
#             max_results=self.max_results,
#             country="US",
#             safesearch="moderate"
#         )
#         search_results = await self.brave_client.text_search(search_input)
#         response = await self.response_generator.quick_llm_response(
#             user_query=query, 
#             search_results=search_results
#         )
#         return response

# async def main():
#     quick_one = SRSWTIQuickOne(max_results=20)
#     result = await quick_one("what is the PE RATIO of netscout")
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())