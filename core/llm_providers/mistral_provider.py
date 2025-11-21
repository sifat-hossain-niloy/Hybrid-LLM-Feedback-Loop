"""
Mistral AI Provider
"""
import os
from typing import List, Dict, Optional
from mistralai import Mistral
from .base import BaseLLMProvider

class MistralProvider(BaseLLMProvider):
    """Mistral AI provider with persistent context"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "codestral-2508"):
        api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        super().__init__(api_key, model_name)
        self.client = Mistral(api_key=api_key)
    
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make Mistral API call"""
        try:
            response = self.client.chat.complete(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Mistral API error: {str(e)}")
    
    def generate_hint(self, session_id: str, problem_statement: str, 
                     failed_solution: str, verdict: str, error_details: str, **kwargs) -> str:
        """Generate debugging hint with context"""
        
        # Create context if it doesn't exist
        if not self.get_context(session_id):
            system_message = """You are an expert competitive programming mentor specializing in debugging and providing hints.

Your role is to analyze failed solutions and provide specific, actionable hints to help fix the issues.

Guidelines:
1. Analyze the problem statement, failed code, and error details
2. Identify the root cause of the failure
3. Provide specific hints about what to fix
4. Suggest algorithmic improvements if needed
5. Point out edge cases that might be missed
6. Be concise but thorough in your analysis
7. Focus on the specific error, not rewriting the entire solution

Provide hints that guide the programmer to the correct solution without giving away the complete answer."""
            
            self.create_context(session_id, system_message)
        
        # Build user message
        user_message = f"""Problem Statement:
{problem_statement}

Failed Solution:
{failed_solution}

Verdict: {verdict}

Error Details:
{error_details}

Please analyze this failure and provide specific hints on what needs to be fixed."""
        
        return self.chat(session_id, user_message, **kwargs)
