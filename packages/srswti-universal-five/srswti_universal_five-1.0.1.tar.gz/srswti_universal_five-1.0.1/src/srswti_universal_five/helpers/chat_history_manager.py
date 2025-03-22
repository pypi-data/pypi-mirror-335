import logging
from supabase import create_client, Client
from typing import List, Dict, Optional, Tuple
import os
from openai import AsyncOpenAI
from functools import lru_cache
import asyncio
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OptimizedChatHistoryManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL", "https://api.srswti.com"),
            os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxeWR5cHp1bW1qeWhxanVra21yIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxMjE0NjgzOCwiZXhwIjoyMDI3NzIyODM4fQ.lJj1gOldqUQ41f7xubhUUpb8-Wbs69LydDfjLdgu4kM")
        )
        self.openai_client = openai_client
        
        # Configuration
        self.max_tokens = 5000
        self.token_buffer = 2000
        
        # Cache settings
        self._chat_cache = {}
        self._last_update = defaultdict(float)
        self._cache_ttl = 300  # 5 minutes
        self._max_cache_size = 1000
        
        # Batch update settings
        self._message_buffer = defaultdict(list)
        self._buffer_size_limit = 5
        self._last_flush = 0
        self._flush_interval = 5
        
        # Background task flags
        self._flush_task = None
        self._cleanup_task = None
        self._is_running = False

    async def _save_to_db(self, canvas_id: str, user_id: str, messages: List[Dict]) -> None:
        """Save messages to database, letting Supabase handle timestamps"""
        try:
            # First check if record exists
            result = self.supabase.table('canvas_chat_history')\
                .select('messages')\
                .eq('canvas_id', canvas_id)\
                .eq('user_id', user_id)\
                .execute()

            if result.data:
                # Update existing record
                data = self.supabase.table('canvas_chat_history')\
                    .update({'messages': messages})\
                    .eq('canvas_id', canvas_id)\
                    .eq('user_id', user_id)\
                    .execute()
            else:
                # Insert new record
                data = self.supabase.table('canvas_chat_history')\
                    .insert({
                        'canvas_id': canvas_id,
                        'user_id': user_id,
                        'messages': messages
                    })\
                    .execute()

            if not data.data:
                raise Exception("Failed to save chat history")
                
            logger.debug(f"Saved chat history for canvas: {canvas_id}, user: {user_id}")
            
        except Exception as e:
            logger.error(f"Database save error for canvas: {canvas_id}, user: {user_id}: {str(e)}")
            raise

    async def get_chat_history(self, canvas_id: str, user_id: str) -> List[Dict]:
        """Get chat history with simple message structure"""
        cache_key = f"{canvas_id}:{user_id}"
        current_time = time.time()

        # Check cache first
        if cache_key in self._chat_cache:
            if current_time - self._last_update[cache_key] < self._cache_ttl:
                return self._chat_cache[cache_key]

        try:
            result = self.supabase.table('canvas_chat_history')\
                .select('messages')\
                .eq('canvas_id', canvas_id)\
                .eq('user_id', user_id)\
                .execute()
            
            if result.data and len(result.data) > 0:
                # Handle the response properly
                messages = result.data[0]['messages'] if isinstance(result.data[0], dict) else []
                self._chat_cache[cache_key] = messages
                self._last_update[cache_key] = current_time
                return messages
            
            # If no existing messages, initialize with empty list
            initial_messages = []
            await self._save_to_db(canvas_id, user_id, initial_messages)
            self._chat_cache[cache_key] = initial_messages
            self._last_update[cache_key] = current_time
            return initial_messages
                
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return self._chat_cache.get(cache_key, [])
        
    async def manage_chat_history(self, canvas_id: str, user_id: str, new_message: Dict, critical: bool = False) -> List[Dict]:
        """Enhanced manage_chat_history that maintains natural conversation flow."""
        cache_key = f"{canvas_id}:{user_id}"
        try:
            messages = self._chat_cache.get(cache_key)
            current_time = time.time()
            
            if messages is None or (current_time - self._last_update.get(cache_key, 0) > self._cache_ttl):
                messages = await self.get_chat_history(canvas_id, user_id)

            if not isinstance(new_message, dict) or 'role' not in new_message or 'content' not in new_message:
                raise ValueError("Invalid message format")

            clean_message = {
                'role': new_message['role'],
                'content': new_message['content'],
                'timestamp': current_time
            }
            messages.append(clean_message)

            if len(new_message.get('content', '')) > 1000:
                current_tokens = self.count_messages_tokens(messages)
                if current_tokens > (self.max_tokens - self.token_buffer):
                    messages = await self._process_token_limit(messages)
            
            self._chat_cache[cache_key] = messages
            self._last_update[cache_key] = current_time

            if critical or self._should_force_save(messages):
                await self._save_to_db(canvas_id, user_id, messages)  # Add await here
            else:
                self._message_buffer[(canvas_id, user_id)] = messages
                if len(self._message_buffer) >= self._buffer_size_limit:
                    await self._flush_message_buffer(force=True)

            return messages

        except Exception as e:
            logger.error(f"Error in manage_chat_history: {e}")
            await self._handle_error(canvas_id, user_id, clean_message)
            return [clean_message]


    # async def manage_chat_history(self, canvas_id: str, user_id: str, new_message: Dict, 
    #                             critical: bool = False) -> List[Dict]:
    #     """
    #     Enhanced manage_chat_history that maintains natural conversation flow
    #     Stores only the essential conversational elements
    #     """
    #     cache_key = f"{canvas_id}:{user_id}"
        
    #     try:
    #         messages = self._chat_cache.get(cache_key)
    #         current_time = time.time()
            
    #         if messages is None or (current_time - self._last_update.get(cache_key, 0) > self._cache_ttl):
    #             messages = await self.get_chat_history(canvas_id, user_id)

    #         # Validate and clean message format
    #         if not isinstance(new_message, dict) or 'role' not in new_message or 'content' not in new_message:
    #             raise ValueError("Invalid message format")

    #         # Store only essential conversational content
    #         clean_message = {
    #             'role': new_message['role'],
    #             'content': new_message['content'],
    #             'timestamp': current_time
    #         }

    #         messages.append(clean_message)

    #         # Token management
    #         if len(new_message.get('content', '')) > 1000:
    #             current_tokens = self.count_messages_tokens(messages)
    #             if current_tokens > (self.max_tokens - self.token_buffer):
    #                 messages = await self._process_token_limit(messages)
            
    #         # Update cache
    #         self._chat_cache[cache_key] = messages
    #         self._last_update[cache_key] = current_time

    #         # Smart save strategy
    #         if critical or self._should_force_save(messages):
    #             self._save_to_db(canvas_id, user_id, messages)
    #         else:
    #             self._message_buffer[(canvas_id, user_id)] = messages
    #             if len(self._message_buffer) >= self._buffer_size_limit:
    #                 await self._flush_message_buffer(force=True)

    #         return messages

        except Exception as e:
            logger.error(f"Error in manage_chat_history: {e}")
            await self._handle_error(canvas_id, user_id, clean_message)
            return [clean_message]

    async def _flush_message_buffer(self, force: bool = False) -> None:
        """Flush message buffer with batch upserts"""
        current_time = time.time()
        if not force and current_time - self._last_flush < self._flush_interval:
            return

        if not self._message_buffer:
            return

        try:
            for (canvas_id, user_id), messages in self._message_buffer.items():
                try:
                    # First try to update existing record
                    result = self.supabase.table('canvas_chat_history')\
                        .update({'messages': messages})\
                        .eq('canvas_id', canvas_id)\
                        .eq('user_id', user_id)\
                        .execute()
                    
                    # If no rows were updated (record doesn't exist), then insert
                    if not result.data:
                        self.supabase.table('canvas_chat_history')\
                            .insert({
                                'canvas_id': canvas_id,
                                'user_id': user_id,
                                'messages': messages
                            })\
                            .execute()
                
                except Exception as e:
                    logger.error(f"Error updating/inserting chat history for canvas: {canvas_id}, user: {user_id}: {str(e)}")
                    continue

            self._message_buffer.clear()
            self._last_flush = current_time
            logger.info(f"Successfully flushed message buffer")

        except Exception as e:
            logger.error(f"Error in batch flush: {e}")
            raise

    async def _process_token_limit(self, messages: List[Dict]) -> List[Dict]:
        """Process token limit while maintaining conversation coherence"""
        if len(messages) <= 2:
            return messages[-1:]

        try:
            # Keep last few messages for immediate context
            if len(messages) > 10:
                # Summarize older messages
                to_summarize = messages[:-10]
                summary = await self.summarize_messages(to_summarize)
                return [summary] + messages[-10:]
            return messages
            
        except Exception as e:
            logger.error(f"Error in token limit processing: {e}")
            return messages[-2:]

    def _should_force_save(self, messages: List[Dict]) -> bool:
        """Smart decision for forcing immediate save"""
        if not messages:
            return False
            
        last_message = messages[-1]
        
        # Force save for important messages
        important_keywords = {'error', 'critical', 'urgent', 'important'}
        if any(word in last_message.get('content', '').lower() for word in important_keywords):
            return True
            
        # Force save for long message chains
        if len(messages) > 50:
            return True
        
        return False

    def count_tokens(self, text: str) -> int:
        """Fast token counting"""
        return int(len(text.split()) * 0.75)

    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """Optimized token counting"""
        return sum(self.count_tokens(str(msg.get('content', ''))) for msg in messages)

    async def summarize_messages(self, messages: List[Dict]) -> Dict:
        """Natural message summarization"""
        try:
            messages_text = "\n".join(
                f"{m['role']}: {m['content']}" 
                for m in messages[-10:]
            )
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "system",
                    "content": """You are an advanced AI conversation summarizer. Your comprehensive task is to create a meticulously structured summary of the entire multi-turn conversation, capturing every nuanced aspect:

CONVERSATION ANALYSIS FRAMEWORK:

I. CONVERSATION OVERVIEW
1. Conversation Purpose/Initial Context
2. Total Number of Turns
3. Participants Involved (User and Assistant Roles)

II. THEMATIC PROGRESSION
1. Primary Themes Discussed
   - Chronological breakdown of topic transitions
   - Key sub-topics within each theme
2. Contextual Evolution
   - How conversation topics interconnected
   - Logical flow and progression of dialogue

III. INTERACTION DYNAMICS
1. Communication Style
   - User's communication approach
   - Assistant's response strategy
2. Emotional Landscape
   - Underlying emotional tones
   - Implicit and explicit emotional cues
3. Interaction Patterns
   - Question-answer sequences
   - Depth of engagement
   - Complexity of exchanges

IV. CRITICAL CONTENT ANALYSIS
1. Key Information Exchanged
   - Significant facts, insights, or revelations
   - Precise quotes or statements of importance
2. Decision Points
   - Explicit or implicit decisions made
   - Reasoning behind key conclusions

V. KNOWLEDGE AND LEARNING OUTCOMES
1. New Information Introduced
2. Learning Trajectories
3. Potential Knowledge Gaps

VI. FUTURE IMPLICATIONS
1. Potential Follow-up Actions
2. Unresolved Questions
3. Suggested Next Steps

SUMMARY GUIDELINES:
- Maintain objectivity
- Be concise yet comprehensive
- Preserve conversation's authentic essence
- Use clear, structured narrative format
- Highlight most significant interaction elements"""
                }, {
                    "role": "user",
                    "content": messages_text
                }]
            )
            
            return {
                "role": "assistant",
                "content": f"[Earlier Conversation Summary: {response.choices[0].message.content}]",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error summarizing messages: {e}")
            return {
                "role": "assistant",
                "content": "[Comprehensive Earlier Conversation Summary Unavailable]",
                "timestamp": time.time()
            }

    async def initialize(self):
        """Initialize background tasks"""
        if not self._is_running:
            self._is_running = True
            self._flush_task = asyncio.create_task(self._periodic_flush())
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            logger.info("Chat history manager initialized with background tasks")

    async def shutdown(self):
        """Graceful shutdown"""
        self._is_running = False
        if self._flush_task:
            await self._flush_message_buffer(force=True)
            self._flush_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("Chat history manager shut down gracefully")

    async def _periodic_flush(self):
        """Periodic message buffer flush"""
        while self._is_running:
            try:
                await asyncio.sleep(self._flush_interval)
                await self._flush_message_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")

    async def _periodic_cleanup(self):
        """Periodic cache cleanup"""
        while self._is_running:
            try:
                await asyncio.sleep(60)
                await self._cleanup_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def _cleanup_cache(self):
        """Clean up old cache entries"""
        current_time = time.time()
        
        try:
            # Remove expired entries
            expired_keys = [
                key for key, last_update in self._last_update.items()
                if current_time - last_update > self._cache_ttl
            ]
            
            # Batch save expired entries before removing
            for key in expired_keys:
                if key in self._chat_cache:
                    canvas_id, user_id = key.split(':')
                    await self._save_to_db(canvas_id, user_id, self._chat_cache[key])
                    
            # Clear expired entries
            for key in expired_keys:
                self._chat_cache.pop(key, None)
                self._last_update.pop(key, None)

            # Handle memory pressure
            if len(self._chat_cache) > self._max_cache_size:
                sorted_entries = sorted(
                    self._last_update.items(),
                    key=lambda x: x[1]
                )
                
                to_remove = len(self._chat_cache) - self._max_cache_size
                for key, _ in sorted_entries[:to_remove]:
                    if key in self._chat_cache:
                        canvas_id, user_id = key.split(':')
                        await self._save_to_db(canvas_id, user_id, self._chat_cache[key])
                        self._chat_cache.pop(key)
                        self._last_update.pop(key)
                        
        except Exception as e:
            logger.error(f"Error in cache cleanup: {e}")

    async def _handle_error(self, canvas_id: str, user_id: str, message: Dict):
        """Handle errors in chat history management"""
        logger.error(f"Error handling message for canvas {canvas_id}, user {user_id}")
        try:
            await self._save_to_db(canvas_id, user_id, [message])
        except Exception as e:
            logger.error(f"Failed to save error message: {e}")

