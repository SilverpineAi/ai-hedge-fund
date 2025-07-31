"""
Base Agent Class

Abstract base class for all AI agents in the influencer discovery system.
Uses the existing LLM infrastructure from the hedge fund project.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
import json
from datetime import datetime

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

# Import existing LLM infrastructure
from src.llm.llm_config import get_llm_config, LLMConfig, LLMFactory

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Base class for analysis results"""
    agent_name: str
    confidence_score: float  # 0-100
    analysis_data: Dict[str, Any]
    reasoning: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_name": self.agent_name,
            "confidence_score": self.confidence_score,
            "analysis_data": self.analysis_data,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat()
        }

class BaseAgent(ABC):
    """Abstract base class for AI agents"""
    
    def __init__(self, 
                 llm_config: Optional[LLMConfig] = None,
                 temperature: float = 0.3,
                 max_tokens: int = 2000):
        """
        Initialize the agent
        
        Args:
            llm_config: LLM configuration (uses default if None)
            temperature: Temperature for LLM responses
            max_tokens: Maximum tokens for responses
        """
        self.llm_config = llm_config or get_llm_config()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM
        self.llm = LLMFactory.create_llm(
            provider=self.llm_config.provider,
            model=self.llm_config.model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"Initialized {self.__class__.__name__} with {self.llm_config.provider}:{self.llm_config.model}")
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the name of the agent"""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for the agent"""
        pass
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Perform analysis on the provided data
        
        Args:
            data: Input data for analysis
            
        Returns:
            AnalysisResult object
        """
        pass
    
    def _create_messages(self, user_prompt: str) -> List[BaseMessage]:
        """
        Create message list for LLM
        
        Args:
            user_prompt: User prompt
            
        Returns:
            List of messages
        """
        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt)
        ]
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with a prompt
        
        Args:
            prompt: User prompt
            
        Returns:
            LLM response
        """
        try:
            messages = self._create_messages(prompt)
            response = self.llm.invoke(messages)
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error calling LLM in {self.agent_name}: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
        
        Args:
            response: LLM response string
            
        Returns:
            Parsed JSON data
        """
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON found, try parsing the whole response
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response in {self.agent_name}: {e}")
            logger.error(f"Response was: {response}")
            
            # Return a default structure
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response,
                "confidence_score": 0
            }
    
    def _extract_confidence_score(self, analysis_data: Dict[str, Any]) -> float:
        """
        Extract confidence score from analysis data
        
        Args:
            analysis_data: Analysis results
            
        Returns:
            Confidence score (0-100)
        """
        # Look for confidence score in various possible keys
        confidence_keys = ['confidence_score', 'confidence', 'score', 'certainty']
        
        for key in confidence_keys:
            if key in analysis_data:
                score = analysis_data[key]
                if isinstance(score, (int, float)):
                    return max(0, min(100, float(score)))
        
        # Default confidence score
        return 50.0
    
    def _format_data_for_prompt(self, data: Dict[str, Any]) -> str:
        """
        Format data dictionary for inclusion in prompt
        
        Args:
            data: Data to format
            
        Returns:
            Formatted string
        """
        formatted_parts = []
        
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                formatted_parts.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                formatted_parts.append(f"{key}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _create_analysis_result(self, 
                              analysis_data: Dict[str, Any], 
                              reasoning: str = "") -> AnalysisResult:
        """
        Create an AnalysisResult object
        
        Args:
            analysis_data: Analysis results
            reasoning: Reasoning for the analysis
            
        Returns:
            AnalysisResult object
        """
        confidence_score = self._extract_confidence_score(analysis_data)
        
        return AnalysisResult(
            agent_name=self.agent_name,
            confidence_score=confidence_score,
            analysis_data=analysis_data,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Override in subclasses for specific validation
        return isinstance(data, dict) and len(data) > 0
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for this agent
        
        Returns:
            List of required field names
        """
        # Override in subclasses
        return []
    
    def preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess data before analysis
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data
        """
        # Override in subclasses for specific preprocessing
        return data
    
    def postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess analysis results
        
        Args:
            results: Raw analysis results
            
        Returns:
            Postprocessed results
        """
        # Override in subclasses for specific postprocessing
        return results