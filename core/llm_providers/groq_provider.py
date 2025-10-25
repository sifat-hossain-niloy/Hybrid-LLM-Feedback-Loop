"""
Groq Provider
"""
import os
from typing import List, Dict, Optional
from groq import Groq
from .base import BaseLLMProvider

class GroqProvider(BaseLLMProvider):
    """Groq provider with persistent context"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "llama-3.3-70b-versatile"):
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Groq API key is required")
        
        super().__init__(api_key, model_name)
        self.client = Groq(api_key=api_key)
    
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make Groq API call"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def generate_hint(self, session_id: str, problem_statement: str, 
                     failed_solution: str, verdict: str, error_details: str, **kwargs) -> str:
        """Generate debugging hint with context"""
        
        # Create context if it doesn't exist
        if not self.get_context(session_id):
            system_message = """You are an expert competitive programming mentor and debugging specialist.

Your expertise lies in analyzing failed competitive programming solutions and providing precise, actionable debugging hints.

Your approach:
1. Carefully analyze the problem requirements and constraints
2. Examine the failed solution for logical errors, edge cases, and algorithmic issues
3. Consider the specific verdict (WA, TLE, MLE, RE) and error details
4. Provide targeted hints that guide toward the correct solution
5. Suggest specific improvements without giving away the complete answer
6. Focus on the most critical issues first

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
