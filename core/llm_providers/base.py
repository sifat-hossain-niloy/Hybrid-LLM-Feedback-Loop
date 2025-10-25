"""
Base LLM Provider Interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class ChatMessage:
    """Standardized chat message format"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class ChatContext:
    """Persistent chat context for a session"""
    session_id: str
    messages: List[ChatMessage]
    model_name: str
    provider_name: str
    created_at: float
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = time.time()
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the context"""
        self.messages.append(ChatMessage(role=role, content=content))
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Convert messages to API format"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self._contexts: Dict[str, ChatContext] = {}
    
    @abstractmethod
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make the actual API call to the provider"""
        pass
    
    def create_context(self, session_id: str, system_message: Optional[str] = None) -> ChatContext:
        """Create a new chat context"""
        context = ChatContext(
            session_id=session_id,
            messages=[],
            model_name=self.model_name,
            provider_name=self.provider_name,
            created_at=time.time()
        )
        
        if system_message:
            context.add_message("system", system_message)
        
        self._contexts[session_id] = context
        return context
    
    def get_context(self, session_id: str) -> Optional[ChatContext]:
        """Get existing chat context"""
        return self._contexts.get(session_id)
    
    def chat(self, session_id: str, user_message: str, **kwargs) -> str:
        """Send a message and get response, maintaining context"""
        context = self.get_context(session_id)
        if not context:
            raise ValueError(f"No context found for session {session_id}. Create context first.")
        
        # Add user message to context
        context.add_message("user", user_message)
        
        # Make API call
        response = self._make_api_call(context.get_messages_for_api(), **kwargs)
        
        # Add assistant response to context
        context.add_message("assistant", response)
        
        return response
    
    def clear_context(self, session_id: str) -> None:
        """Clear a specific context"""
        if session_id in self._contexts:
            del self._contexts[session_id]
    
    def clear_all_contexts(self) -> None:
        """Clear all contexts"""
        self._contexts.clear()
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of context"""
        context = self.get_context(session_id)
        if not context:
            return {}
        
        return {
            "session_id": session_id,
            "provider": self.provider_name,
            "model": self.model_name,
            "message_count": len(context.messages),
            "created_at": context.created_at,
            "last_message_time": context.messages[-1].timestamp if context.messages else None
        }
