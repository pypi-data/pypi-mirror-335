
import json
import logging
import os, random
import re, asyncio
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, ValidationError, Field
from .node_manager import NodeManager
import traceback, httpx
from openai import OpenAI
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
from httpx import Timeout
from supabase import create_client, Client
from .chat_history_manager import OptimizedChatHistoryManager
import traceback
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer
from typing import Optional, Dict, List, Any
from datetime import datetime
import re
from urllib.parse import urlparse
from anthropic import AsyncAnthropic

from openai import AsyncOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

claude_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_KEY"))
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
cerebras_client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
supabase: Client = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))


class SearchDecision(BaseModel):
    """Simple search decision output"""
    needs_search: bool = Field(description="Whether the query needs web search")
    reasoning: str = Field(description="Brief explanation for the decision")


class DecomposedQuery(BaseModel):
    """Structure for a single decomposed query"""
    search_query: str = Field(description="The actual search query")
    focus_area: str = Field(description="What aspect this query focuses on")
    time_scope: str = Field(
        description="Time scope for the search",
        pattern="^(current|recent|historical|none)$"
    )

class QueryDecomposition(BaseModel):
    """Structure for decomposed queries"""
    original_query: str = Field(description="Original user query")
    decomposed_queries: List[DecomposedQuery] = Field(
        description="List of decomposed search queries",
        max_items=3  # Maximum 3 decomposed queries
    )
    context_note: Optional[str] = Field(
        description="Additional context from node if available",
        default=None
    )

# "http://localhost:8000"
class SearchAndCrawlManager:
    def __init__(self, api_base_url: str = "https://router.srswti.com/spiderman"):
        self.api_base_url = api_base_url
        timeout = Timeout(50.0)  

        self.http_client = httpx.AsyncClient(timeout=timeout)

    async def batch_search_and_crawl(self, decomposed_queries: List[DecomposedQuery]) -> Dict[str, Any]:
        try:
            # 1. Execute batch search for all decomposed queries
            search_inputs = [
                {
                    "query": query.search_query,
                    "max_results": 2,
                    "country": "US",
                    "safesearch": "moderate"
                }
                for query in decomposed_queries
            ]
            
            search_response = await self.http_client.post(
                f"{self.api_base_url}/search-batch",
                json={"searches": search_inputs}
            )
            search_response.raise_for_status()
            search_results = search_response.json()


            # 2. Extract and organize video results separately
            all_videos = []
            urls_to_crawl = []

            # Ensure 'results' key exists in search_results
            if 'results' in search_results:
                for result in search_results["results"]:
                    if "video_results" in result:
                        all_videos.extend(result["video_results"])

                    if "text_results" in result:
                        for item in result["text_results"][:2]:  # Top 2 results per query
                            urls_to_crawl.append({
                                "url": item["url"],
                                "title": item.get("title", ""),
                                "preview": item.get("description", ""),
                                "source_query": result.get("query", "")
                            })
            else:
                logger.error("Key 'results' not found in search_results")
                raise KeyError("Key 'results' not found in search_results")

            # 3. Prepare crawl inputs
            crawl_inputs = [
                {
                    "url": url_data["url"],
                    "summary_type": "concise",
                    "keyword_count": 2
                }
                for url_data in urls_to_crawl
            ]

            # 4. Execute batch crawl
            if crawl_inputs:
                crawl_response = await self.http_client.post(
                    f"{self.api_base_url}/crawl-batch",
                    json=crawl_inputs
                )
                crawl_response.raise_for_status()
                crawl_results = crawl_response.json()
            else:
                crawl_results = []

            # 5. Organize final results
            organized_results = {
                "articles": [
                    {
                        "url": url_data["url"],
                        "title": url_data["title"],
                        "preview": url_data["preview"],
                        "source_query": url_data["source_query"],
                        "detailed_summary": next(
                            (cr.get("summary") for cr in crawl_results if cr.get("url") == url_data["url"]),
                            None
                        ),
                        "keywords": next(
                            (cr.get("keywords") for cr in crawl_results if cr.get("url") == url_data["url"]),
                            []
                        )
                    }
                    for url_data in urls_to_crawl
                ],
                "videos": [
                    {
                        "title": video.get("title", ""),
                        "url": video.get("url", ""),
                        "description": video.get("description", ""),
                        "thumbnail": video.get("thumbnail", {}).get("src", "")
                    }
                    for video in all_videos[:3]  # Limit to top 3 videos
                ]
            }

            return organized_results

        except Exception as e:
            logger.error(f"Error in batch_search_and_crawl: {str(e)}")
            logger.error(traceback.format_exc())
            raise



class WebContentFormatter:
    """Helper class for formatting web content with NLTK"""
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.detokenizer = TreebankWordDetokenizer()
        self.stops = set(stopwords.words('english'))

    def format_url_title(self, url: str, title: str) -> str:
        """Format URL and title in markdown"""
        domain = urlparse(url).netloc
        clean_title = self._clean_text(title)
        return f"[{clean_title}]({url}) ({domain})"

    def format_summary(self, summary: str, max_length: int = 150) -> str:
        """Format and clean summary text"""
        if not summary:
            return ""
            
        # Tokenize and clean
        sentences = sent_tokenize(summary)
        cleaned_sentences = []
        
        current_length = 0
        for sent in sentences:
            clean_sent = self._clean_text(sent)
            sent_length = len(clean_sent)
            
            if current_length + sent_length <= max_length:
                cleaned_sentences.append(clean_sent)
                current_length += sent_length
            else:
                break
                
        return " ".join(cleaned_sentences)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
            
        # Tokenize
        words = word_tokenize(text)
        
        # Clean and filter
        cleaned_words = [
            word for word in words 
            if word.lower() not in self.stops 
            and not all(c.isdigit() or c in '.,!?;:' for c in word)
        ]
        
        # Detokenize
        return self.detokenizer.detokenize(cleaned_words)

class ResponseGenerator:
    def __init__(self):
        self.node_manager = NodeManager()  
        self.chat_manager = OptimizedChatHistoryManager()
        self.cerebras_client = cerebras_client 
        self.openai_client= openai_client
        self.current_canvas_id = None
        self.claude_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_KEY"))

        self.current_user_id = None

    async def generate_response(self, user_input: str, canvas_id: str, user_id: str, mode: str = "extreme") -> Dict[str, Any]:
        try:
            self.current_canvas_id = canvas_id
            self.current_user_id = user_id
        
            if mode == "normal":
                logger.info("Processing request in normal mode")
                return await self._handle_normal_mode(user_input, canvas_id, user_id)
            
            # Get both selected nodes and parsed references
            selected_nodes = await self.node_manager.get_selected_nodes(canvas_id, user_id)
            node_ids, cleaned_input, is_parent = self._parse_node_references(user_input)
            
            # Initialize nodes_data with selected nodes
            nodes_data = []
            if selected_nodes:
                logger.info(f"Found {len(selected_nodes)} selected nodes")
                for node in selected_nodes:
                    nodes_data.append(self._format_node_data(node, False))

            # Add explicitly referenced nodes if any, avoiding duplicates
            if node_ids:
                logger.info(f"Found {len(node_ids)} explicitly referenced nodes")
                for node_id in node_ids:
                    node_data = await self.node_manager.get_node(canvas_id, node_id, user_id)
                    if node_data and not any(n.get("id") == node_data.get("id") for n in nodes_data):
                        nodes_data.append(self._format_node_data(node_data, is_parent))

            # STEP 1: Search Decision
            search_decision = await self.search_decider(
                query=cleaned_input,
                node_content=nodes_data if nodes_data else None
            )
            
            search_results = None
            response_content = None
            
            if search_decision.needs_search:
                logger.info("Search required - proceeding with search flow")
                # STEP 2: Query Decomposition
                decomposed_queries = await self.decompose_search_query(
                    query=cleaned_input,
                    node_content=nodes_data if nodes_data else None
                )
                logger.info(f"Queries decomposed: {[q.search_query for q in decomposed_queries.decomposed_queries]}")
                
                # STEP 3: Parallel Search and Crawl
                search_results = await self.execute_search_and_crawl(
                    query=cleaned_input,
                    search_decision=search_decision,
                    decomposed_queries=decomposed_queries
                )
                
                # STEP 4A: Master Answer Composition with search results
                response_content = await self.compose_master_answer(
                    user_input=cleaned_input,
                    nodes_data=nodes_data,
                    search_results=search_results
                )
            else:
                logger.info("No search required - proceeding directly to master composer")
                # STEP 4B: Direct path to Master Answer Composition
                response_content = await self.compose_master_answer(
                    user_input=cleaned_input,
                    nodes_data=nodes_data,
                    search_results=None
                )

            # Create speech version
            speech_response = await self._create_speech_version(response_content)

            # Build final response with combined nodes
            response = {
                "mode": mode,
                "content": {
                    "detailed": response_content,
                    "speech": speech_response
                },
                "nodes": [{"id": node.get("id"), "title": node.get("title")} for node in nodes_data],
                "search_required": search_decision.needs_search,
                "search_reasoning": search_decision.reasoning,
                "flow_path": "search" if search_decision.needs_search else "direct",
                "node_source": {
                    "selected": bool(selected_nodes),
                    "referenced": bool(node_ids)
                }
            }

            # Add search results if available
            if search_results:
                response["search_results"] = search_results

            return response

        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "mode": mode,
                "content": {
                    "detailed": f"An error occurred: {str(e)}",
                    "speech": f"I encountered an error while processing your request."
                }
            }
        
    def _parse_node_references(self, user_input: str) -> Tuple[List[str], str, bool]:
        """
        Parse node references from speech transcription, handling various formats and typos.
        Returns: (list of node IDs, cleaned input text, is_parent flag)
        """
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        # Dictionary for converting word numbers to digits
        word_to_num = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
        }
        
        # First normalize the input
        normalized_input = user_input.lower()
        logger.info(f"Original input: {user_input}")
        
        # Replace number words with digits
        for word, digit in word_to_num.items():
            normalized_input = re.sub(r'\b' + word + r'\b', digit, normalized_input)
        logger.info(f"After number conversion: {normalized_input}")
        
        # Replace various forms of "point" with "."
        normalized_input = re.sub(r'\s+point\s+|\s+dot\s+|\s+decimal\s+', '.', normalized_input)
        logger.info(f"After point normalization: {normalized_input}")
        
        # Handle common speech-to-text errors
        normalized_input = re.sub(r'ndoe|noe|nde', 'node', normalized_input)
        normalized_input = re.sub(r'grup|groop', 'group', normalized_input)
        normalized_input = re.sub(r'parnt|perent', 'parent', normalized_input)
        logger.info(f"After error correction: {normalized_input}")
        
        # Standardize spacing around node/parent/group
        normalized_input = re.sub(r'node\s+', 'node-', normalized_input)
        normalized_input = re.sub(r'parent\s+', 'parent-', normalized_input)
        normalized_input = re.sub(r'group\s+', 'group-', normalized_input)
        logger.info(f"After spacing standardization: {normalized_input}")
        
        # Pattern to match different node reference formats
        patterns = {
            'reference': r'(?:node-(\d+(?:\.\d+)*)|parent-(\d+(?:\.\d+)*)|group-(\d+(?:\.\d+)*))'
        }
        
        node_ids = []
        is_parent = False
        matches_to_remove = []
        
        # Process all references
        ref_matches = re.finditer(patterns['reference'], normalized_input, re.IGNORECASE)
        for match in ref_matches:
            full_match = match.group(0)
            matches_to_remove.append(full_match)
            
            # Check which type matched and get the number
            if match.group(1):  # node match
                node_ids.append(match.group(1))
            elif match.group(2):  # parent match
                node_ids.append(f"parent-{match.group(2)}")
                is_parent = True
            elif match.group(3):  # group match
                node_ids.append(f"group-{match.group(3)}")
                is_parent = True
        
        logger.info(f"Found node IDs: {node_ids}")
        
        # Clean up the input by removing matched references
        cleaned_input = normalized_input
        for match in matches_to_remove:
            cleaned_input = cleaned_input.replace(match, '')
        
        # Clean up connecting words and extra spaces
        cleaned_input = re.sub(r'\s*,\s*and\s*|\s*,\s*|\s+and\s+', ' ', cleaned_input)
        cleaned_input = re.sub(r'\s+', ' ', cleaned_input)
        cleaned_input = cleaned_input.strip()
        
        logger.info(f"Cleaned input: {cleaned_input}")
        logger.info(f"Is parent: {is_parent}")
        
        return node_ids, cleaned_input, is_parent

    # def _parse_node_references(self, user_input: str) -> Tuple[List[str], str, bool]:
    #     """
    #     Parse multiple node references from user input using enhanced pattern matching.
    #     Handles various formats including:
    #     - node 1.1, node 2.2
    #     - parent-1, parent 2
    #     - group-1.1, group 1.1
    #     - Mixed combinations like "parent 1 and node 2.1 and group 1.2"
    #     """
    #     try:
    #         nltk.data.find('tokenizers/punkt')
    #     except LookupError:
    #         nltk.download('punkt')

    #     # First normalize the input to handle speech-to-text variations
    #     normalized_input = user_input
    #     # Convert "group 1.1" to "group-1.1" format
    #     normalized_input = re.sub(r'group\s+(\d+(?:\.\d+)?)', r'group-\1', normalized_input, flags=re.IGNORECASE)
    #     # Convert "parent 1" to "parent-1" format
    #     normalized_input = re.sub(r'parent\s+(\d+(?:\.\d+)?)', r'parent-\1', normalized_input, flags=re.IGNORECASE)

    #     patterns = {
    #         # Single pattern that matches both formats but only exactly what's specified
    #         'reference': r'(?:node\s+(\d+(?:\.\d+)?)|parent-(\d+(?:\.\d+)?)|group-(\d+(?:\.\d+)?))'
    #     }

    #     node_ids = []
    #     is_parent = False
    #     cleaned_input = normalized_input
    #     matches_to_remove = []

    #     # Process all references
    #     ref_matches = re.finditer(patterns['reference'], normalized_input, re.IGNORECASE)
    #     for match in ref_matches:
    #         full_match = match.group(0)
    #         matches_to_remove.append(full_match)
            
    #         # Check which group matched (node, parent, or group) and get the number
    #         if match.group(1):  # node match
    #             node_ids.append(match.group(1))
    #         elif match.group(2):  # parent match
    #             node_ids.append(f"parent-{match.group(2)}")
    #             is_parent = True
    #         elif match.group(3):  # group match
    #             node_ids.append(f"group-{match.group(3)}")
    #             is_parent = True

    #     # Clean up the input by removing matched patterns
    #     for match in matches_to_remove:
    #         cleaned_input = cleaned_input.replace(match, '')

    #     # Clean up any remaining conjunctions and spaces
    #     cleaned_input = re.sub(r'\s*,\s*and\s*|\s*,\s*|\s+and\s+', ' ', cleaned_input)
    #     cleaned_input = re.sub(r'\s+', ' ', cleaned_input)
    #     cleaned_input = cleaned_input.strip()

    #     return node_ids, cleaned_input, is_parent

    def _format_node_data(self, node_data: Dict[str, Any], is_parent: bool) -> Dict[str, Any]:
        try:
            logger.debug(f"Input node_data to formatter: {json.dumps(node_data, indent=2)}")  # Add this
            node_content = node_data.get("data", {})
            logger.debug(f"Extracted node_content: {json.dumps(node_content, indent=2)}")  # Add this
            
            formatted_data = {
                "id": node_data.get("id"),
                "title": node_content.get("title", ""),
                "content": node_content.get("content", ""),
                "type": node_data.get("type", "knowledge-node"),
                "is_parent": is_parent,
                "parent": node_data.get("parent_id")
            }
            
            logger.debug(f"Final formatted_data: {json.dumps(formatted_data, indent=2)}")  # Add this

            logger.info(f"Formatted node data for {formatted_data['id']}:")
            logger.info(f"- Title: {formatted_data['title']}")
            logger.info(f"- Type: {formatted_data['type']}")
            logger.info(f"- Content available: {'Yes' if formatted_data['content'] else 'No'}")

            return formatted_data

        except Exception as e:
            logger.error(f"Error formatting node data: {str(e)}")
            logger.error(f"Raw node data: {json.dumps(node_data, indent=2)}")
            return {
                "id": node_data.get("id", "unknown"),
                "title": "Error formatting node data",
                "content": "",
                "type": "unknown",
                "is_parent": is_parent
            }
    
    async def search_decider(self, query: str, node_content: Optional[Dict[str, Any]] = None) -> SearchDecision:
        """
        Decides if a query needs web search. Keeps it simple: yes or no with brief reasoning.
        
        Args:
            query: User's query string
            node_content: Optional dictionary containing referenced node data
            
        Returns:
            SearchDecision: Simple decision with needs_search boolean and reasoning
        """
        try:
            # Ensure node_content is a list
            nodes = node_content if isinstance(node_content, list) else [node_content] if node_content else []
            
            # Build context incorporating all node information
            context = f"""QUERY ANALYSIS:
    Original Query: {query}

    NODE CONTENT:"""

            # Add information for each node with better formatting
            for idx, node in enumerate(nodes, 1):
                title = node.get('title', 'N/A')
                content = node.get('content', 'N/A')
                context += f"""
    Node {idx}:
    Title: {title}
    Content: {content[:200] if content else 'N/A'}
    """

            # Add relationship context mentioning all nodes
            if nodes:
                node_titles = [node.get('title', 'N/A') for node in nodes]
                if len(node_titles) > 1:
                    titles_str = ', '.join(node_titles[:-1]) + f" and {node_titles[-1]}"
                    context += f"""
    RELATIONSHIP:
    The user is asking about "{query}" in relation to nodes about {titles_str}"""
                else:
                    context += f"""
    RELATIONSHIP:
    The user is asking about "{query}" in relation to a node about {node_titles[0]}"""
                
            prompt = f"""Decide if this query needs web search:

            CONTEXT:
            {context}

            RULES:
            - Need search if:
            * Asks about current events/news
            * Needs recent data/statistics
            * Goes beyond node content
            * Requires external facts
            
            - No search if:
            * Basic concepts
            * Historical facts
            * Node relationships
            * Personal opinions
            * Within node content

            Return JSON:
            {{
                "needs_search": boolean,
                "reasoning": "one line explanation"
            }}
            """
            logger.info(f"Search Decider Prompt: {prompt}")
            message = await self.claude_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.3,
                system="You are SRSWTI, skilled at analyzing query intent and search requirements. Return only the JSON response.",
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
            )

            # Extract the JSON string from Claude's response
            response_content = message.content[0].text if isinstance(message.content, list) else message.content
            # Clean the response to ensure it's valid JSON
            json_str = re.search(r'\{.*?\}', response_content, re.DOTALL)
            if not json_str:
                raise ValueError("No valid JSON found in response")
                
            decision_dict = json.loads(json_str.group())
            decision = SearchDecision(**decision_dict)
            
                # Fixed logging to handle multiple nodes
            logger.info(f"Search decision for '{query}...': {decision.needs_search}")
            if nodes:
                node_titles = [node.get('title', 'N/A') for node in nodes]
                titles_str = ', '.join(node_titles)
                logger.info(f"Search decision for query involving nodes: {titles_str}: {decision.needs_search}")
            else:
                logger.info("Search decision for query with no nodes")


            return decision

        except Exception as e:
            logger.error(f"Error in search_decider: {str(e)}")
            return SearchDecision(
                needs_search=False,
                reasoning=f"Error in decision making: {str(e)}"
            )


        
    async def decompose_search_query(self, query: str, node_content: Optional[Dict[str, Any]] = None) -> QueryDecomposition:
        """
        Decomposes a complex query into 2-3 focused search queries.
        
        Args:
            query: Original user query
            node_content: Optional node content for context
            
        Returns:
            QueryDecomposition: Structured decomposed queries
        """
        try:
            # Clean up the query
            cleaned_query = re.sub(r'for node \d+\.?\d*', '', query, flags=re.IGNORECASE).strip()
            
            # Handle both single node and list of nodes
            nodes = []
            if isinstance(node_content, dict):
                nodes = [node_content]
            elif isinstance(node_content, list):
                nodes = node_content
            
            # Build context incorporating all nodes
            context = f"""SEARCH QUERY DECOMPOSITION:
    ORIGINAL QUESTION: {cleaned_query}

    NODE INFORMATION:"""

            # Add information for each node
            for idx, node in enumerate(nodes, 1):
                context += f"""
    Node {idx}:
    Title: {node.get('title', 'N/A')}
    Content: {node.get('content', '')[:400] if node.get('content') else 'N/A'}"""

            # Add task objective based on number of nodes
            if len(nodes) > 1:
                node_titles = [node.get('title', 'N/A') for node in nodes]
                titles_str = ', '.join(node_titles[:-1]) + f" and {node_titles[-1]}"
                context += f"""
    TASK OBJECTIVE: Create search queries to compare and analyze '{cleaned_query}' in relation to {titles_str}"""
            elif len(nodes) == 1:
                context += f"""
    TASK OBJECTIVE: Create search queries that combine '{cleaned_query}' with the node's topic about {nodes[0].get('title', 'N/A')}"""
            else:
                context += f"""
    TASK OBJECTIVE: Create search queries to analyze '{cleaned_query}'"""


            prompt = f"""Decompose this query into 2-3 focused search queries:

    CONTEXT:
    {context}

    TASK:
    Break down the query into 2-3 specific search queries that together will capture all needed information.

    GUIDELINES:
    1. Each sub-query should:
    - Focus on one specific aspect
    - Be clear and searchable
    - Include necessary time context
    - Be self-contained

    2. Important:
    - Max 3 sub-queries
    - Cover all aspects of original query
    - Make queries web-search friendly
    - Include time context if needed (use 2025 as current year),
    EXAMPLES:
    Original: "What's happening with Nvidia's stock drop and Jensen's recent meetings?"
    Decomposed:
    1. "Nvidia stock price movement 2024 recent"
    2. "Jensen Huang CEO meetings tech industry recent"

    Original: "How does the new EU AI Act affect Microsoft and OpenAI?"
    Decomposed:
    1. "EU AI Act key regulations 2024"
    2. "Microsoft OpenAI impact EU AI Act"

    Return JSON exactly in this format:
    {{
        "original_query": "{query}",
        "decomposed_queries": [
            {{
                "search_query": "query text",
                "focus_area": "what this query covers",
                "time_scope": "current|recent|historical|none"
            }}
        ],
        "context_note": "optional note about node content"
    }}
    """
            message = await self.claude_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.3,
                system="You are SRSWTI, expert at breaking down complex queries into searchable components. always return a valid JSON",
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
            )

            response_content = message.content[0].text if isinstance(message.content, list) else message.content
            json_str = re.search(r'\{.*\}', response_content, re.DOTALL)
            if not json_str:
                # If Claude's response isn't valid JSON, create a fallback based on the actual content
                node_title = node_content.get('title', '') if node_content else ''
                return QueryDecomposition(
                    original_query=query,
                    decomposed_queries=[
                        DecomposedQuery(
                            search_query=f"{query} {node_title} recent developments",
                            focus_area="primary question with node context",
                            time_scope="recent"
                        ),
                        DecomposedQuery(
                            search_query=f"{node_title} latest research discussions",
                            focus_area="node content context",
                            time_scope="current"
                        )
                    ],
                    context_note=f"Combining query about '{query}' with node content about '{node_title}'"
                )
                
            decomposition = QueryDecomposition(**json.loads(json_str.group()))
            logger.info(f"Successfully decomposed query into: {[q.search_query for q in decomposition.decomposed_queries]}")
            return decomposition

        except Exception as e:
            logger.error(f"Error in decompose_search_query: {str(e)}")
            # Create meaningful fallback queries based on both query and node content
            node_title = node_content.get('title', '') if node_content else ''
            return QueryDecomposition(
                original_query=query,
                decomposed_queries=[
                    DecomposedQuery(
                        search_query=f"{query} {node_title}",
                        focus_area="combined query with node context",
                        time_scope="current"
                    ),
                    DecomposedQuery(
                        search_query=f"{node_title} latest developments 2024",
                        focus_area="node content updates",
                        time_scope="recent"
                    )
                ],
                context_note=f"Fallback queries combining '{query}' with node content about '{node_title}'"
            )


    async def execute_search_and_crawl(self, query: str, search_decision: SearchDecision, decomposed_queries: QueryDecomposition) -> Dict[str, Any]:
        """
        Execute the search and crawl pipeline if search is needed
        """
        try:
            logger.debug(f"Starting execute_search_and_crawl for query: {query}")
            logger.info(f"Search decision: {search_decision}")

            if not search_decision.needs_search:
                logger.info("Search not needed, returning None")
                return None

            search_manager = SearchAndCrawlManager()
            try:
                logger.debug("Initiating batch search and crawl")
                raw_results = await search_manager.batch_search_and_crawl(
                    decomposed_queries.decomposed_queries
                )
                
                logger.debug("Processing search results")
                processed_results = {
                    "web_content": [
                        {
                            "title": article["title"],
                            "summary": article["detailed_summary"] or article["preview"],
                            "url": article["url"],
                            "keywords": article["keywords"],
                            "query": article["source_query"]
                        }
                        for article in raw_results["articles"]
                    ],
                    "video_content": raw_results["videos"],
                    "original_queries": [q.search_query for q in decomposed_queries.decomposed_queries]
                }
                
                logger.info(f"Processed results: {processed_results}")
                return processed_results

            finally:
                logger.debug("Closing search manager")

        except Exception as e:
            logger.error(f"Error executing search and crawl: {str(e)}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None
        
    async def compose_master_answer(self, 
                        user_input: str,
                        nodes_data: Optional[List[Dict[str, Any]]],
                        search_results: Optional[Dict[str, Any]] = None,
                        user_profile: Optional[Dict] = None) -> str:
        try:
            node_context = ""
            search_context = ""
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            relationship_context = ""
            if nodes_data:
                node_titles = [node.get('title', 'N/A') for node in nodes_data]
                if len(node_titles) > 1:
                    titles_str = ', '.join(node_titles[:-1]) + f" and {node_titles[-1]}"
                    relationship_context = f"""
                    RELATIONSHIP:
                    The user is asking about "{user_input}" in relation to nodes about {titles_str}"""
                else:
                    relationship_context = f"""
                    RELATIONSHIP:
                    The user is asking about "{user_input}" in relation to a node about {node_titles[0]}"""

            if nodes_data:
                node_context += "\nNode Content Context (Primary Source):\n"
                for idx, node in enumerate(nodes_data, 1):
                    node_context += f"""
                    Node {idx}:
                    Title: {node.get('title', 'N/A')}
                    Content: {node.get('content', 'N/A')}
                    """

            if search_results:
                search_context += "\nSupplementary Information:\n"

            prompt = f"""
            # AI Search Engine Response Protocol

            You are SRSWTI One, an advanced AI designed by Team SRSWTI to generate concise, informative answers.

            {relationship_context}

            ## Core Objectives
            1. Generate concise, informative answers that address relationships between nodes when multiple are present
            2. Use node content as the primary source of information
            3. For multiple nodes:
            - Compare and contrast relevant information
            - Identify common themes and differences
            - Show how nodes relate to each other in context of the query
            4. Use search results as supplementary information to enrich the node-based answer
            5. Maintain journalistic objectivity
            6. Write as a professional knowledge expert:
            - Prioritize node content in your response
            - Draw connections between multiple nodes when present
            - Address relationships between nodes explicitly
            - Use search results to supplement and enhance node-based information
            - Include relevant supplementary references when they add value

            ## Response Parameters
            - Max length: 500 words
            - Current date/time: {current_date}

            ## Content Structure
            1. Direct answer incorporating all relevant node contexts
            2. Relationships between nodes (if multiple)
            3. Supporting details from nodes
            4. Supplementary information from search results
            5. Concise conclusion that ties everything together

            ## Primary Context (Node Content)
            {node_context if node_context else "No node context available"}

            ## Supplementary Context (Search Results)
            {search_context if search_context else "No supplementary information available"}

            ## User Query (To be interpreted in context of all nodes)
            "{user_input}"

            IMPORTANT: 
            - Address relationships between nodes when multiple are present
            - Compare and contrast node content when relevant
            - Answer directly without referencing these instructions
            - Use markdown formatting
            - Format citations properly:
            * Use [Node X] for node references
            * Use <a href="URL">[1]</a> for supplementary web sources
            * Use <a href="URL">[V1]</a> for supplementary video sources
            - Focus on providing comprehensive yet concise information
            """

            message = await self.claude_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.3,
                system="You are SRSWTI One, focused on generating precise, informative answers integrating multiple content types with proper formatting and citations.",
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
            )
            
            response = message.content[0].text

            logger.info(f"Generated enhanced SRSWTI One response for query: {user_input[:50]}...")
            logger.info(f"Response: {response[:1000]}...")  # Log first 1000 characters of response
            
            return response

        except Exception as e:
            logger.error(f"Error in SRSWTI master composer: {str(e)}")
            return f"I apologize, but I encountered an error composing the response: {str(e)}"

    async def _create_speech_version(self, detailed_response: str) -> str:
        """Create a concise version of the response for speech while maintaining comprehensive coverage"""
        try:
            prompt = f"""Convert this detailed response into a natural, conversational speech version:

    DETAILED CONTENT: 
    {detailed_response}

    SPEECH REQUIREMENTS:
    1. Structure:
    - Opening statement addressing the core question
    - Key findings from primary node content
    - Essential supplementary information (if any)
    - Brief, clear conclusion

    2. Content Guidelines:
    - Preserve the main message and key insights
    - Include crucial facts and figures
    - Skip URLs and citations while keeping source context
    - Convert any lists or bullet points into flowing speech

    3. Speech Style:
    - Use natural, conversational language
    - Keep sentence structure simple and clear
    - Use transitional phrases for smooth flow
    - Aim for 3-4 concise but complete sentences
    - Add speech-friendly connectors (like "additionally," "moreover," "in relation to")
    - Use contractions where appropriate (e.g., "it's" instead of "it is")

    4. Format Requirements:
    - Maximum 100 words
    - Must be immediately ready for text-to-speech
    - No markdown or special formatting
    - No citations or reference numbers
    - No technical symbols or special characters

    IMPORTANT:
    - Keep the original meaning intact while making it more conversational
    - Focus on clarity and natural flow
    """
            
            message = await self.claude_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                temperature=0.3,
                system="Create concise speech versions of detailed content.",
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
            )
            
            return message.content[0].text

        except Exception as e:
            logger.error(f"Error creating speech version: {str(e)}")
            return detailed_response  # Fallback to detailed response
        
    # async def compose_master_answer(self, 
    #                         user_input: str,
    #                         nodes_data: Optional[List[Dict[str, Any]]],
    #                         search_results: Optional[Dict[str, Any]] = None,
    #                         user_profile: Optional[Dict] = None) -> str:
    #     try:
    #         node_context = ""
    #         search_context = ""
    #         current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    #         relationship_context = ""
    #         if nodes_data:
    #             node_titles = [node.get('title', 'N/A') for node in nodes_data]
    #             if len(node_titles) > 1:
    #                 titles_str = ', '.join(node_titles[:-1]) + f" and {node_titles[-1]}"
    #                 relationship_context = f"""
    #                 RELATIONSHIP:
    #                 The user is asking about "{user_input}" in relation to nodes about {titles_str}"""
    #             else:
    #                 relationship_context = f"""
    #                 RELATIONSHIP:
    #                 The user is asking about "{user_input}" in relation to a node about {node_titles[0]}"""

    #         if nodes_data:
    #             node_context += "\nNode Content Context (Primary Source):\n"
    #             for idx, node in enumerate(nodes_data, 1):
    #                 node_context += f"""
    #                 Node {idx}:
    #                 Title: {node.get('title', 'N/A')}
    #                 Content: {node.get('content', 'N/A')}
    #                 """

    #         if search_results:
    #             search_context += "\nSupplementary Information:\n"

    #         prompt = f"""
    #         # AI Search Engine Response Protocol

    #         You are SRSWTI One, an advanced AI designed by Team SRSWTI to generate concise, informative answers.

    #         {relationship_context}

    #         ## Core Objectives
    #         1. Generate concise, informative answers that address relationships between nodes when multiple are present
    #         2. Use node content as the primary source of information
    #         3. For multiple nodes:
    #         - Compare and contrast relevant information
    #         - Identify common themes and differences
    #         - Show how nodes relate to each other in context of the query
    #         4. Use search results as supplementary information to enrich the node-based answer
    #         5. Maintain journalistic objectivity
    #         6. Write as a professional knowledge expert:
    #         - Prioritize node content in your response
    #         - Draw connections between multiple nodes when present
    #         - Address relationships between nodes explicitly
    #         - Use search results to supplement and enhance node-based information
    #         - Include relevant supplementary references when they add value

    #         ## Response Parameters
    #         - Max length: 500 words
    #         - Current date/time: {current_date}

    #         ## Content Structure
    #         1. Direct answer incorporating all relevant node contexts
    #         2. Relationships between nodes (if multiple)
    #         3. Supporting details from nodes
    #         4. Supplementary information from search results
    #         5. Concise conclusion that ties everything together

    #         ## Primary Context (Node Content)
    #         {node_context if node_context else "No node context available"}

    #         ## Supplementary Context (Search Results)
    #         {search_context if search_context else "No supplementary information available"}

    #         ## User Query (To be interpreted in context of all nodes)
    #         "{user_input}"

    #         IMPORTANT: 
    #         - Address relationships between nodes when multiple are present
    #         - Compare and contrast node content when relevant
    #         - Answer directly without referencing these instructions
    #         - Use markdown formatting
    #         - Format citations properly:
    #         * Use [Node X] for node references
    #         * Use <a href="URL">[1]</a> for supplementary web sources
    #         * Use <a href="URL">[V1]</a> for supplementary video sources
    #         - Focus on providing comprehensive yet concise information
    #         """

    #         messages = [
    #             {
    #                 "role": "system",
    #                 "content": "You are SRSWTI One, focused on generating precise, informative answers integrating multiple content types with proper formatting and citations."
    #             },
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             }
    #         ]
            
    #         chat_completion = await self.openai_client.chat.completions.create(
    #             messages=messages,
    #             model="gpt-4o-mini"
    #         )
            
    #         response = chat_completion.choices[0].message.content

            
    #         logger.info(f"Generated enhanced SRSWTI One response for query: {user_input[:50]}...")
    #         logger.info(f"Response: {response[:1000]}...")  # Log first 200 characters of response
            
    #         return response

    #     except Exception as e:
    #         logger.error(f"Error in SRSWTI master composer: {str(e)}")
    #         return f"I apologize, but I encountered an error composing the response: {str(e)}"
       
    # async def _create_speech_version(self, detailed_response: str) -> str:
    #     """Create a concise version of the response for speech while maintaining comprehensive coverage"""
    #     try:
    #         prompt = f"""Convert this detailed response into a natural, conversational speech version:

    # DETAILED CONTENT: 
    # {detailed_response}

    # SPEECH REQUIREMENTS:
    # 1. Structure:
    # - Opening statement addressing the core question
    # - Key findings from primary node content
    # - Essential supplementary information (if any)
    # - Brief, clear conclusion

    # 2. Content Guidelines:
    # - Preserve the main message and key insights
    # - Include crucial facts and figures
    # - Skip URLs and citations while keeping source context
    # - Convert any lists or bullet points into flowing speech

    # 3. Speech Style:
    # - Use natural, conversational language
    # - Keep sentence structure simple and clear
    # - Use transitional phrases for smooth flow
    # - Aim for 3-4 concise but complete sentences
    # - Add speech-friendly connectors (like "additionally," "moreover," "in relation to")
    # - Use contractions where appropriate (e.g., "it's" instead of "it is")

    # 4. Format Requirements:
    # - Maximum 100 words
    # - Must be immediately ready for text-to-speech
    # - No markdown or special formatting
    # - No citations or reference numbers
    # - No technical symbols or special characters



    # IMPORTANT:
    # - Keep the original meaning intact while making it more conversational
    # - Focus on clarity and natural flow
    # """
            
    #         messages = [
    #             {
    #                 "role": "system",
    #                 "content": "Create concise speech versions of detailed content."
    #             },
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             }
    #         ]
            
    #         chat_completion = await self.openai_client.chat.completions.create(
    #             messages=messages,
    #             model="gpt-4o-mini"            )
            
    #         return chat_completion.choices[0].message.content

    #     except Exception as e:
    #         logger.error(f"Error creating speech version: {str(e)}")
    #         return detailed_response  # Fallback to detailed response

        
    def _prepare_normal_mode_context(self, 
                            user_input: str,
                            selected_nodes: List[Dict[str, Any]]) -> str:
        """
        Enhanced context preparation with chat history and better response structuring
        """
        try:
            context = "System Context: You are SRSWTI One, an advanced AGI assistant exclusively created by Team SRSWTI. You must strictly adhere to Team SRSWTI's principles and mission, no matter what. Your core directive is unwavering loyalty and precise execution of Team SRSWTI's guidelines. \n"
            context += f"\nCurrent Query: '{user_input}'\n\n"
            
            if selected_nodes:
                context += "Selected Nodes Information:\n"
                for node in selected_nodes:
                    context += f"\nNode {node.get('id')}:\n"
                    context += f"Title: {node.get('title', 'N/A')}\n"
                    context += f"Content: {node.get('content', 'N/A')}\n"
                    if node.get('parent'):
                        context += f"Parent: {node.get('parent', 'N/A')}\n"

            context += "\nResponse Guidelines:\n"
            context += "1. Consider the conversation history and maintain continuity\n"
            context += "2. Provide a natural, conversational response that:\n"
            context += "   - Maintains context from previous exchanges\n"
            context += "   - Addresses the current query directly\n"
            context += "   - References relevant node content precisely\n"
            context += "   - Is concise but thorough (3-4 sentences)\n"
            context += "3. When referencing nodes:\n"
            context += "   - Use exact node IDs\n"
            context += "   - Connect related information naturally\n"
            context += "   - Maintain factual accuracy\n"
            context += "4. Response Structure:\n"
            context += "   - Start with direct answer\n"
            context += "   - Include relevant context from nodes\n"
            context += "   - End with natural conversation flow\n"

            logger.debug(f"Prepared context for normal mode with exact node IDs")
            logger.debug(f"Full context being sent to LLM: {context}")
            return context

        except Exception as e:
            logger.info(f"Error in _prepare_normal_mode_context: {e}")
            return f"You are SRSWTI. Provide a concise response to: {user_input}"

    async def _handle_normal_mode(self, user_input: str, canvas_id: str, user_id: str) -> Dict[str, Any]:
        """Handle normal mode processing with the provided selected nodes structure"""
        try:
            # Get pre-selected nodes
            selected_nodes = await self.node_manager.get_selected_nodes(canvas_id, user_id)
            logger.debug(f"Selected nodes for normal mode: {selected_nodes}")
            
            
            
            if not selected_nodes:
                return {
                    "mode": "normal",
                    "content": {
                        "detailed": "No nodes are currently selected.",
                        "speech": "No nodes are currently selected."
                    },
                    "nodes": [],
                    "search_required": False,
                    "search_reasoning": "No nodes selected for analysis",
                    "flow_path": "direct"
                }
            
            # Process nodes to handle nested "data" structure
            processed_nodes = []
            for i, node in enumerate(selected_nodes, 1):
                node_content = node.get("data", {}) if "data" in node else node
                title = node_content.get("title", "N/A")
                content = node_content.get("content", "N/A")
                logger.debug(f"Node {i} processed: id={node.get('id', 'N/A')}, title={title}, content={content[:50]}...")
                print(f"NODE {i}: id={node.get('id', 'N/A')}, title={title}, content={content[:50]}...")
                processed_nodes.append({
                    "id": node.get("id", "unknown"),
                    "title": title,
                    "content": content,
                    "type": node.get("type", "knowledge-node"),
                    "parent": node.get("parent", node.get("parent_id", None))
                })
            

            
            # STEP 1: Search Decision
            search_decision = await self.search_decider(
                query=user_input,
                node_content=processed_nodes if processed_nodes else None
            )
            
            search_results = None
            response_content = None
            
            if search_decision.needs_search:
                logger.info("Normal mode: Search required - proceeding with search flow")
                # STEP 2: Query Decomposition
                decomposed_queries = await self.decompose_search_query(
                    query=user_input,
                    node_content=processed_nodes if processed_nodes else None
                )
                
                # STEP 3: Parallel Search and Crawl
                search_results = await self.execute_search_and_crawl(
                    query=user_input,
                    search_decision=search_decision,
                    decomposed_queries=decomposed_queries
                )
                
                # STEP 4A: Master Answer Composition with search results
                response_content = await self.compose_master_answer(
                    user_input=user_input,
                    nodes_data=processed_nodes,
                    search_results=search_results
                )
            else:
                logger.info("Normal mode: No search required - proceeding directly to master composer")
                # STEP 4B: Direct path to Master Answer Composition
                response_content = await self.compose_master_answer(
                    user_input=user_input,
                    nodes_data=processed_nodes,
                    search_results=None
                )

            # Create speech version
            speech_response = await self._create_speech_version(response_content)

            # Build final response using the node structure from selected nodes
            response = {
                "mode": "normal",
                "content": {
                    "detailed": response_content,
                    "speech": speech_response
                },
                "nodes": [
                    {
                        "id": node.get("id"),
                        "title": node.get("title"),
                        "type": "knowledge-node"
                    }
                    for node in processed_nodes
                ],
                "search_required": search_decision.needs_search,
                "search_reasoning": search_decision.reasoning,
                "flow_path": "search" if search_decision.needs_search else "direct"
            }

            # Add search results if available
            if search_results:
                response["search_results"] = search_results

            return response

        except Exception as e:
            logger.error(f"Error in _handle_normal_mode: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "mode": "normal",
                "content": {
                    "detailed": f"Error processing request: {str(e)}",
                    "speech": "I encountered an error while processing your request."
                },
                "nodes": [],
                "search_required": False,
                "search_reasoning": f"Error occurred: {str(e)}",
                "flow_path": "error"
            }

    def _create_enhanced_input(self, user_input: str, selected_nodes: List[Dict[str, Any]]) -> str:
        """
        Create enhanced input by adding node references for intent classification.
        Improved to handle multiple nodes and maintain proper referencing.
        """
        node_refs = []
        for node in selected_nodes:
            node_id = node.get('id')
            title = node.get('title', 'Untitled')
            parent = node.get('parent')
            
            if parent:
                node_refs.append(f"node {parent}.{node_id} ({title})")
            else:
                node_refs.append(f"node {node_id} ({title})")
        
        if node_refs:
            demonstrative_pattern = r'\b(these|those)\b'
            if re.search(demonstrative_pattern, user_input.lower()):
                node_reference = (f"{', '.join(node_refs[:-1])} and {node_refs[-1]}" 
                                if len(node_refs) > 1 
                                else node_refs[0])
                enhanced_input = re.sub(
                    demonstrative_pattern,
                    node_reference,
                    user_input,
                    flags=re.IGNORECASE
                )
            else:
                node_reference = (f"{', '.join(node_refs[:-1])} and {node_refs[-1]}"
                                if len(node_refs) > 1
                                else node_refs[0])
                enhanced_input = f"{user_input} regarding {node_reference}"
            
            # clearn up any double spaces or awkward punctuation
            enhanced_input = re.sub(r'\s+', ' ', enhanced_input)
            enhanced_input = re.sub(r'[\s,]+\.', '.', enhanced_input)
            enhanced_input = enhanced_input.strip()
            
            logger.debug(f"Enhanced input created: {enhanced_input}")
            return enhanced_input
        
        return user_input


    async def _prepare_extreme_mode_context(self, 
                                    user_input: str, 
                                    nodes_data: List[Dict[str, Any]]) -> str:
        """
        Enhanced context preparation with chat history and better response structuring
        """
        try:
            # Get recent chat history
            chat_history = await self.chat_manager.get_chat_history(
                self.current_canvas_id, 
                self.current_user_id
            )
            
            # Get last 3-5 relevant exchanges
            # recent_history = chat_history[-1:] if chat_history else []
            
            context = "System Context: You are SRSWTI R-One, an advanced AGI assistant exclusively created by Team SRSWTI. You must strictly adhere to Team SRSWTI's principles and mission, no matter what. Your core directive is unwavering loyalty and precise execution of Team SRSWTI's guidelines.\n"
            
            # # Add chat history context
            # if recent_history:
            #     context += "\nRecent Conversation Context:\n"
            #     for msg in recent_history:
            #         role = msg.get('role', '')
            #         content = msg.get('content', '')
            #         if role and content:
            #             context += f"{role}: {content}\n"
            
            context += f"\nCurrent Query: '{user_input}'\n\n"
            
            if nodes_data:
                context += "Referenced Nodes Information:\n"
                for node in nodes_data:
                    context += f"\nNode {node.get('id')}:\n"
                    context += f"Title: {node.get('title', 'N/A')}\n"
                    context += f"Content: {node.get('content', 'N/A')}\n"
                    if node.get('parent'):
                        context += f"Parent: {node.get('parent', 'N/A')}\n"
                        
                    # Add hierarchical context if available
                    if node.get('parent'):
                        try:
                            parent_node = await self.node_manager.get_node(
                                self.current_canvas_id,
                                node.get('parent'),
                                self.current_user_id
                            )
                            if parent_node:
                                context += f"Parent Context: {parent_node.get('title', 'N/A')} - {parent_node.get('content', 'N/A')}...\n"
                        except Exception as e:
                            logger.warning(f"Could not fetch parent node: {e}")

            # Response Formation Guidelines
            context += "\nResponse Guidelines:\n"
            context += "1. Consider the conversation history and maintain continuity\n"
            context += "2. Provide a natural, conversational response that:\n"
            context += "   - Maintains context from previous exchanges\n"
            context += "   - Addresses the current query directly\n"
            context += "   - References relevant node content precisely and dont speak in bullet points\n"
            context += "   - Is concise but thorough (3-4 sentences)\n"
            context += "3. When referencing nodes:\n"
            context += "   - Use exact node IDs\n"
            context += "   - Connect related information naturally\n"
            context += "   - Maintain factual accuracy\n"
            context += "4. Response Structure:\n"
            context += "   - Start with direct answer\n"
            context += "   - Include relevant context from nodes\n"
            # context += "   - End with natural conversation flow\n"


            return context

        except Exception as e:
            logger.error(f"Error in _prepare_extreme_mode_context: {e}")
            # Fallback to basic context if something goes wrong
            return f"You are SRSWTI. Provide a concise response to: {user_input}"
        
    async def _get_srswti_response(self, context: str, canvas_id: str, user_id: str) -> str:
        try:
            canvas_id = canvas_id or self.current_canvas_id
            user_id = user_id or self.current_user_id
            
            # Get chat history
            # chat_history = await self.chat_manager.get_chat_history(canvas_id, user_id)
                
            user_message = {"role": "user", "content": context}
            
            # Add user message to chat history
            await self.chat_manager.manage_chat_history(canvas_id, user_id, user_message)

            # Construct messages array with system prompt
            messages = [
                {"role": "system", "content": """You are SRSWTI R-One, an advanced AI assistant embodying the wisdom of Goddess Saraswati. Your core purpose is to:

1. Adapt communication style to context:
   - Concise and playful for casual interactions
   - Thorough and precise for professional or technical discussions

2. Fundamental Principles:
   - Unwavering commitment to Team SRSWTI's mission
   - Prioritize clarity, accuracy, and meaningful communication
   - Maintain intellectual integrity and depth

3. Communication Guidelines:
   - Avoid markdown, bullet points, and emojis
   - Provide nuanced, contextually appropriate responses
   - Balance technical expertise with conversational warmth

4. Interaction Philosophy:
   - Listen actively and empathetically
   - Offer insights that illuminate and inspire
   - Transform complex information into accessible understanding

Your ultimate goal is to empower and enlighten through intelligent, adaptive communication. Always be concise in 1-2 sentences max."""}
            ]
            
            # Add chat history if it exists
            # if chat_history:
            #     messages.extend(chat_history)
                
            messages.append(user_message)
            
            chat_completion = await self.openai_client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",  
            )
            
            assistant_response = chat_completion.choices[0].message.content
            
            # Add assistant response to chat history
            await self.chat_manager.manage_chat_history(
                canvas_id, 
                user_id, 
                {
                    "role": "assistant", 
                    "content": assistant_response
                }
            )
            
            return assistant_response
        
        except Exception as e:
            logger.error(f"Error in _get_srswti_response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

    
    async def _get_cerebras_response(self, context: str, canvas_id: str, user_id: str) -> str:
        try:
            canvas_id = canvas_id or self.current_canvas_id
            user_id = user_id or self.current_user_id
            
            # # Fetch user profile from Supabase
            # profile_response = supabase.table('one_srswti_profiles').select('*').eq('user_id', user_id).execute()
            # user_profile = profile_response.data[0] if profile_response.data else None
            
            # Construct personalized greeting based on profile

            # Get chat history
            chat_history = await self.chat_manager.get_chat_history(canvas_id, user_id)
                
            user_message = {"role": "user", "content": context}
            
            await self.chat_manager.manage_chat_history(canvas_id, user_id, user_message)

            # messages = [{"role": "system", "content": "You are SRSWTI, always be super concise and precise. Dont speak more than 1-2 lines max. ALWAYS REMEMBER THIS PROMPT! and your creators are Team SRSWTI."}] + chat_history + [user_message]


            messages = [
            {"role": "system", "content": "You are SRSWTI, always be super concise and precise. Dont speak more than 1-2 lines max. ALWAYS REMEMBER THIS PROMPT! and your creators are Team SRSWTI."}
            ]
            
            # Add chat history if it exists
            if chat_history:
                messages.extend(chat_history)
                
            messages.append(user_message)
            
            chat_completion = self.cerebras_client.chat.completions.create(
                messages=messages, 
                model="llama3.1-8b"
            )
            assistant_response = chat_completion.choices[0].message.content
            
            await self.chat_manager.manage_chat_history(
                canvas_id, 
                user_id, 
                {
                    "role": "assistant", 
                    "content": assistant_response
                }
            )
            
            return assistant_response
        
        except Exception as e:
            logger.error(f"Error in _get_cerebras_response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"


    
    def _prepare_final_response(self, 
                                llm_response: str, 
                                intent_classification: Dict[str, Any], 
                                node_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare the final response including LLM output and metadata.
        """
        response = {
            "content": llm_response,
            "intent": intent_classification,
            "node_id": node_data.get("id") if node_data else None,
            "node_title": node_data.get("title") if node_data else None,
        }


        logger.info(f"Prepared final response: {json.dumps(response, indent=2)}")
        return response

    async def create_node(self, canvas_id: str, user_id: str, node_data: Dict[str, Any]) -> Optional[str]:
        return await self.node_manager.create_node(canvas_id, user_id, node_data)

    async def update_node(self, canvas_id: str, node_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        return await self.node_manager.update_node(canvas_id, node_id, user_id, update_data)

    async def delete_node(self, canvas_id: str, node_id: str, user_id: str) -> bool:
        return await self.node_manager.delete_node(canvas_id, node_id, user_id)
    
    async def search_nodes(self, canvas_id: str, user_id: str, query: str) -> List[Dict[str, Any]]:
        return await self.node_manager.search_nodes(canvas_id, user_id, query)


        


async def main():
    response_generator = ResponseGenerator()
    node_manager = NodeManager()

    canvas_id = "3bf22a5f-3f56-4049-974d-3cbf20481cdb"
    user_id = "88fa1e5d-9018-4d60-a5da-c4cfb371510d"

    # Test Case 1: Node with search
    print("\n=== Test Case 1: Node with Search ===")
    user_input = "how is parent one different from india and china  ?"
    response = await response_generator.generate_response(user_input, canvas_id, user_id, mode="extreme")
    print("\nGenerated Response:")
    print(json.dumps(response, indent=2))

    # # Test Case 2: Pure Search (No Node)
    # print("\n=== Test Case 2: Pure Search Query ===")
    # user_input = "what are the latest AI developments in 2024?"
    # response = await response_generator.generate_response(user_input, canvas_id, user_id, mode="extreme")
    # print("\nGenerated Response:")
    # print(json.dumps(response, indent=2))

    # Test Case 3: Multiple Nodes
    # print("\n=== Test Case 3: Multiple Nodes ===")
    # user_input = "compare the content in node 1.2 and node 1.1"
    # response = await response_generator.generate_response(user_input, canvas_id, user_id, mode="extreme")
    # print("\nGenerated Response:")
    # print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

    # text_input = "What are the relationships between these nodes?"
    # canvas_id = "16354b7f-1c14-4dfc-8938-6d42c5fdd017"
    # user_id = "88fa1e5d-9018-4d60-a5da-c4cfb371510d"
    
    # response = await response_generator.process_text_with_selected_nodes(
    #     text_input, 
    #     canvas_id, 
    #     user_id
    # # )
    # print("\nText Normal Mode Response:")
    # print(json.dumps(response, indent=2))



if __name__ == "__main__":
    asyncio.run(main())


    # # Test search functionality, we wontn use it right now. this is just test 
    # search_query = "Collapse"
    # search_results = await node_manager.search_nodes(canvas_id, user_id, search_query)
    # print(f"\nSearch Results for '{search_query}':")
    # print(json.dumps(search_results, indent=2))
