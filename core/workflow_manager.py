"""
Workflow Manager for Different LLM Combinations
"""
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
import uuid

from .llm_providers.openai_provider import OpenAIProvider
from .llm_providers.mistral_provider import MistralProvider
from .llm_providers.groq_provider import GroqProvider

class WorkflowType(Enum):
    """Available workflow types"""
    GPT_MISTRAL = "gpt_mistral"
    GPT_GROQ = "gpt_groq"
    # Future workflows can be added here
    # GPT_CLAUDE = "gpt_claude"
    # MISTRAL_GROQ = "mistral_groq"

@dataclass
class WorkflowConfig:
    """Configuration for a workflow"""
    name: str
    solution_provider: str
    hint_provider: str
    solution_model: str
    hint_model: str
    description: str

class WorkflowManager:
    """Manages different LLM workflow combinations"""
    
    # Predefined workflow configurations
    WORKFLOWS = {
        WorkflowType.GPT_MISTRAL: WorkflowConfig(
            name="GPT + Mistral",
            solution_provider="openai",
            hint_provider="mistral",
            solution_model="gpt-4",
            hint_model="codestral-2508",
            description="GPT-4 for solution generation, Codestral for debugging hints"
        ),
        WorkflowType.GPT_GROQ: WorkflowConfig(
            name="GPT + Groq",
            solution_provider="openai", 
            hint_provider="groq",
            solution_model="gpt-4",
            hint_model="llama-3.3-70b-versatile",
            description="GPT-4 for solution generation, Llama 3.3 70B for debugging hints"
        )
    }
    
    def __init__(self):
        self._providers: Dict[str, Any] = {}
        self._active_sessions: Dict[str, Dict[str, str]] = {}  # session_id -> {solution_session, hint_session}
    
    def _get_provider(self, provider_type: str, model_name: str):
        """Get or create a provider instance"""
        provider_key = f"{provider_type}_{model_name}"
        
        if provider_key not in self._providers:
            if provider_type == "openai":
                self._providers[provider_key] = OpenAIProvider(model_name=model_name)
            elif provider_type == "mistral":
                self._providers[provider_key] = MistralProvider(model_name=model_name)
            elif provider_type == "groq":
                self._providers[provider_key] = GroqProvider(model_name=model_name)
            else:
                raise ValueError(f"Unknown provider type: {provider_type}")
        
        return self._providers[provider_key]
    
    def create_session(self, workflow_type: WorkflowType, problem_id: str) -> str:
        """Create a new workflow session"""
        session_id = f"{problem_id}_{workflow_type.value}_{uuid.uuid4().hex[:8]}"
        
        config = self.WORKFLOWS[workflow_type]
        
        # Create unique session IDs for each provider
        solution_session_id = f"{session_id}_solution"
        hint_session_id = f"{session_id}_hint"
        
        # Get providers
        solution_provider = self._get_provider(config.solution_provider, config.solution_model)
        hint_provider = self._get_provider(config.hint_provider, config.hint_model)
        
        # Create contexts (will be created when first used)
        self._active_sessions[session_id] = {
            "workflow_type": workflow_type.value,
            "solution_session": solution_session_id,
            "hint_session": hint_session_id,
            "solution_provider": config.solution_provider,
            "hint_provider": config.hint_provider,
            "solution_model": config.solution_model,
            "hint_model": config.hint_model,
            "problem_id": problem_id
        }
        
        return session_id
    
    def generate_solution(self, session_id: str, problem_statement: str, 
                         previous_attempts: Optional[List[Dict]] = None, **kwargs) -> str:
        """Generate solution using the configured solution provider"""
        if session_id not in self._active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_info = self._active_sessions[session_id]
        solution_provider = self._get_provider(
            session_info["solution_provider"], 
            session_info["solution_model"]
        )
        
        return solution_provider.generate_solution(
            session_info["solution_session"],
            problem_statement,
            previous_attempts,
            **kwargs
        )
    
    def generate_hint(self, session_id: str, problem_statement: str, 
                     failed_solution: str, verdict: str, error_details: str, **kwargs) -> str:
        """Generate hint using the configured hint provider"""
        if session_id not in self._active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_info = self._active_sessions[session_id]
        hint_provider = self._get_provider(
            session_info["hint_provider"], 
            session_info["hint_model"]
        )
        
        return hint_provider.generate_hint(
            session_info["hint_session"],
            problem_statement,
            failed_solution,
            verdict,
            error_details,
            **kwargs
        )
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self._active_sessions:
            return {}
        
        session_info = self._active_sessions[session_id]
        
        # Get context summaries
        solution_provider = self._get_provider(
            session_info["solution_provider"], 
            session_info["solution_model"]
        )
        hint_provider = self._get_provider(
            session_info["hint_provider"], 
            session_info["hint_model"]
        )
        
        return {
            "session_id": session_id,
            "workflow_type": session_info["workflow_type"],
            "problem_id": session_info["problem_id"],
            "solution_context": solution_provider.get_context_summary(session_info["solution_session"]),
            "hint_context": hint_provider.get_context_summary(session_info["hint_session"]),
            "config": {
                "solution_provider": session_info["solution_provider"],
                "hint_provider": session_info["hint_provider"],
                "solution_model": session_info["solution_model"],
                "hint_model": session_info["hint_model"]
            }
        }
    
    def clear_session(self, session_id: str) -> None:
        """Clear a specific session"""
        if session_id not in self._active_sessions:
            return
        
        session_info = self._active_sessions[session_id]
        
        # Clear provider contexts
        solution_provider = self._get_provider(
            session_info["solution_provider"], 
            session_info["solution_model"]
        )
        hint_provider = self._get_provider(
            session_info["hint_provider"], 
            session_info["hint_model"]
        )
        
        solution_provider.clear_context(session_info["solution_session"])
        hint_provider.clear_context(session_info["hint_session"])
        
        # Remove session
        del self._active_sessions[session_id]
    
    def list_workflows(self) -> Dict[str, WorkflowConfig]:
        """List available workflows"""
        return {wf.value: config for wf, config in self.WORKFLOWS.items()}
    
    def list_active_sessions(self) -> List[str]:
        """List active session IDs"""
        return list(self._active_sessions.keys())
    
    @classmethod
    def add_workflow(cls, workflow_type: WorkflowType, config: WorkflowConfig):
        """Add a new workflow configuration (for future extensibility)"""
        cls.WORKFLOWS[workflow_type] = config
