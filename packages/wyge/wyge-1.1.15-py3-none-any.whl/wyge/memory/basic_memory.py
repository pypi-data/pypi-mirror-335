import json
import time
import asyncio
from typing import Dict, Any, List, Callable, Optional

from wyge.tools.base_tool import ToolCall
from wyge.common.logger import logger

class MemoryManager:
    """Enhanced memory manager for chat conversations with advanced features"""
    
    def __init__(self, max_size: int = 20, summarize_threshold: int = 15, 
                 default_system_message: str = "You are a helpful assistant."):
        self.max_size = max_size
        self.summarize_threshold = summarize_threshold
        self.default_system_message = default_system_message
        self.messages: List[Dict[str, Any]] = [{'role': 'system', 'content': default_system_message}]
        self.summarization_in_progress = False
        self._metadata = {
            "last_summarized": 0,
            "total_tokens_used": 0,
            "creation_time": time.time()
        }
        
    def add_message(self, role: str, content: str, **kwargs) -> bool:
        """Add a message to memory with optional metadata"""
        message = {'role': role, 'content': content, **kwargs}
        
        # Check if we need to optimize memory
        if len(self.messages) >= self.max_size:
            self._optimize_memory()
        
        self.messages.append(message)
        
        # Check if we should summarize after adding
        if (not self.summarization_in_progress and 
            len(self.messages) > self.summarize_threshold):
            return True  # Signal that summarization is recommended
        return False
        
    def add_tool_message(self, tool_call: ToolCall) -> None:
        """Add a tool call result to memory"""
        self.messages.append({
            'role': 'tool', 
            'content': json.dumps(tool_call.to_dict()), 
            'tool_call_id': tool_call.id
        })
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Return the full conversation history"""
        return self.messages
    
    def clear(self, preserve_system: bool = True) -> None:
        """Clear memory, optionally preserving system message"""
        if preserve_system and self.messages and self.messages[0]['role'] == 'system':
            self.messages = [self.messages[0]]
        else:
            self.messages = [{'role': 'system', 'content': self.default_system_message}]
        
        self._metadata["last_summarized"] = 0
    
    def update_system_message(self, content: str) -> None:
        """Update or create the system message"""
        if self.messages and self.messages[0]['role'] == 'system':
            self.messages[0]['content'] = content
        else:
            self.messages.insert(0, {'role': 'system', 'content': content})
    
    def search(self, query: str, exact_match: bool = False) -> List[Dict[str, Any]]:
        """Search for messages containing the query"""
        if exact_match:
            return [msg for msg in self.messages if query in msg.get('content', '')]
        return [msg for msg in self.messages if query.lower() in msg.get('content', '').lower()]
    
    def get_last_n_messages(self, n: int = 1) -> List[Dict[str, Any]]:
        """Get the last n messages"""
        return self.messages[-n:] if n <= len(self.messages) else self.messages
    
    async def summarize(self, summarizer: Callable[[List[Dict[str, Any]]], str]) -> None:
        """Summarize the conversation using the provided summarizer function"""
        if len(self.messages) <= self.summarize_threshold:
            return
            
        self.summarization_in_progress = True
        
        # Get all messages except system and the most recent ones
        to_summarize = self.messages[1:-2] if len(self.messages) > 3 else []
        
        if not to_summarize:
            self.summarization_in_progress = False
            return
            
        try:
            summary = await asyncio.to_thread(summarizer, to_summarize)
            
            # Replace the summarized messages with a summary
            system_message = self.messages[0] if self.messages[0]['role'] == 'system' else None
            recent_messages = self.messages[-2:] if len(self.messages) > 2 else self.messages[-1:]
            
            new_messages = []
            if system_message:
                new_messages.append(system_message)
                
            new_messages.append({'role': 'assistant', 'content': f"[SUMMARY] {summary}"})
            new_messages.extend(recent_messages)
            
            self.messages = new_messages
            self._metadata["last_summarized"] = time.time()
        except Exception as e:
            logger.error(f"Failed to summarize memory: {str(e)}")
        finally:
            self.summarization_in_progress = False
    
    def _optimize_memory(self) -> None:
        """Remove oldest non-system messages when memory limit is reached"""
        if len(self.messages) <= 1:
            return
            
        # Keep system message, summary message (if exists) and recent messages
        system_message = self.messages[0] if self.messages[0]['role'] == 'system' else None
        
        # Find a summary message if it exists
        summary_index = -1
        for i, msg in enumerate(self.messages):
            if msg.get('role') == 'assistant' and '[SUMMARY]' in msg.get('content', ''):
                summary_index = i
                break
                
        summary_message = self.messages[summary_index] if summary_index > 0 else None
        
        # Calculate how many recent messages to keep
        keep_count = max(3, int(self.max_size * 0.3))
        recent_messages = self.messages[-keep_count:]
        
        # Rebuild the messages list
        new_messages = []
        if system_message:
            new_messages.append(system_message)
        if summary_message:
            new_messages.append(summary_message)
        new_messages.extend(recent_messages)
        
        self.messages = new_messages
