"""
DeepSeek Provider
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from .base import BaseLLMProvider

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek provider with persistent context"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "deepseek-reasoner"):
        api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        
        super().__init__(api_key, model_name)
        self._conversation_contexts = {}  # Initialize conversation contexts dictionary
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> tuple[str, str]:
        """Make DeepSeek API call
        
        Note: DeepSeek-Reasoner returns both reasoning_content (CoT) and content (final answer).
        Returns: (combined_response, final_answer_only)
        - combined_response: includes reasoning + answer for rich debugging feedback
        - final_answer_only: only the final answer for conversation history (API requirement)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2048),  # Controls reasoning + answer together
                # Note: temperature/top_p are ignored by deepseek-reasoner but allowed for compatibility
                temperature=kwargs.get("temperature", 0.1),
                top_p=kwargs.get("top_p", 1.0),
            )
            
            # Extract both reasoning (chain-of-thought) and final answer
            message = response.choices[0].message
            reasoning = message.reasoning_content if hasattr(message, 'reasoning_content') else None
            final_answer = message.content.strip() if message.content else ""
            
            # Combine reasoning and answer for comprehensive debugging feedback
            if reasoning:
                combined = f"**Reasoning Process:**\n{reasoning}\n\n**Analysis:**\n{final_answer}"
            else:
                combined = final_answer
            
            # Return both: combined for display, final_answer for history
            # (API will 400 if we send reasoning_content back in next request)
            return (combined, final_answer)
                
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")
    
    def create_context(self, session_id: str, system_message: str = ""):
        """Override to ensure proper initialization in _conversation_contexts"""
        if session_id not in self._conversation_contexts:
            self._conversation_contexts[session_id] = []
            if system_message:
                self._conversation_contexts[session_id].append({
                    "role": "system",
                    "content": system_message
                })
    
    def get_context(self, session_id: str):
        """Get conversation context for a session"""
        return self._conversation_contexts.get(session_id)
    
    def chat(self, session_id: str, user_message: str, **kwargs) -> str:
        """Override chat to handle DeepSeek's dual response (reasoning + final answer)
        
        Important: We return the combined response (reasoning + answer) to the caller,
        but only store the final answer in conversation history to avoid API 400 errors.
        """
        if session_id not in self._conversation_contexts:
            raise ValueError(f"Session {session_id} not found. Create context first.")
        
        # Add user message to context
        self._conversation_contexts[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Make API call and get both combined and final-only responses
        combined_response, final_answer = self._make_api_call(
            self._conversation_contexts[session_id],
            **kwargs
        )
        
        # CRITICAL: Store only final answer in conversation history
        # (DeepSeek API will return 400 if reasoning_content is sent back)
        self._conversation_contexts[session_id].append({
            "role": "assistant",
            "content": final_answer  # NOT combined_response!
        })
        
        # Return combined response (with reasoning) to caller for rich debugging feedback
        return combined_response
    
    def generate_hint(self, session_id: str, problem_statement: str, 
                     failed_solution: str, verdict: str, error_details: str, **kwargs) -> str:
        """Generate debugging hint with context"""
        
        # Create context if it doesn't exist
        if not self.get_context(session_id):
            system_message = """You are an expert competitive programming mentor and debugging specialist with advanced reasoning capabilities.

Your expertise lies in deeply analyzing failed competitive programming solutions and providing precise, actionable debugging hints.

Your approach:
1. Carefully analyze the problem requirements and constraints
2. Examine the failed solution for logical errors, edge cases, and algorithmic issues
3. Consider the specific verdict (WA, TLE, MLE, RE) and error details
4. Use step-by-step reasoning to identify the root cause
5. Provide targeted hints that guide toward the correct solution
6. Suggest specific improvements without giving away the complete answer
7. Focus on the most critical issues first

Be analytical, precise, and educational in your hints."""
            
            self.create_context(session_id, system_message)
        
        # Build user message
        user_message = f"""Problem Analysis Request:

Problem Statement:
{problem_statement}

Failed Solution:
{failed_solution}

Verdict: {verdict}

Error Details:
{error_details}

Please provide specific debugging hints to help fix this solution. Focus on the root cause of the failure and suggest targeted improvements."""
        
        return self.chat(session_id, user_message, **kwargs)

