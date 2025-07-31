"""
LLM Configuration Module

Simplified configuration for LLM models used by AI agents.
"""

import os
from dataclasses import dataclass
from typing import Optional
from .models import ModelProvider, get_model

@dataclass
class LLMConfig:
    """Configuration for LLM models"""
    provider: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 2000

def get_llm_config() -> LLMConfig:
    """
    Get default LLM configuration
    
    Returns:
        LLMConfig with default settings
    """
    # Try to use OpenAI by default, fallback to other providers
    if os.getenv("OPENAI_API_KEY"):
        return LLMConfig(
            provider=ModelProvider.OPENAI.value,
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=2000
        )
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LLMConfig(
            provider=ModelProvider.ANTHROPIC.value,
            model="claude-3-haiku-20240307",
            temperature=0.3,
            max_tokens=2000
        )
    elif os.getenv("GROQ_API_KEY"):
        return LLMConfig(
            provider=ModelProvider.GROQ.value,
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=2000
        )
    else:
        # Default to OpenAI even without API key (will fail gracefully)
        return LLMConfig(
            provider=ModelProvider.OPENAI.value,
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=2000
        )

class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    def create_llm(provider: str, model: str, temperature: float = 0.3, max_tokens: int = 2000):
        """
        Create LLM instance
        
        Args:
            provider: LLM provider name
            model: Model name
            temperature: Temperature setting
            max_tokens: Maximum tokens
            
        Returns:
            LLM instance
        """
        provider_enum = ModelProvider(provider)
        llm = get_model(model, provider_enum)
        
        # Set temperature and max_tokens if supported
        if hasattr(llm, 'temperature'):
            llm.temperature = temperature
        if hasattr(llm, 'max_tokens'):
            llm.max_tokens = max_tokens
            
        return llm