"""
OpenAI embedding generation for influencer text data.
Handles text preprocessing and embedding generation using OpenAI's text-embedding-3-large model.
"""

import openai
from typing import List, Optional
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings from influencer text data"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-large"):
        """Initialize OpenAI client with API key"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized embedding service with model: {model}")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for embedding generation"""
        if not text:
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        
        # Remove hashtags and mentions for cleaner text (optional)
        # text = re.sub(r'#\w+', '', text)
        # text = re.sub(r'@\w+', '', text)
        
        return text.strip()
    
    def combine_influencer_text(self, bio: Optional[str], captions: Optional[List[str]]) -> str:
        """Combine bio and captions into a single text for embedding"""
        combined_parts = []
        
        # Add bio if available
        if bio:
            processed_bio = self.preprocess_text(bio)
            if processed_bio:
                combined_parts.append(f"Bio: {processed_bio}")
        
        # Add captions if available
        if captions:
            processed_captions = []
            for caption in captions[:10]:  # Limit to first 10 captions to avoid token limits
                processed_caption = self.preprocess_text(caption)
                if processed_caption:
                    processed_captions.append(processed_caption)
            
            if processed_captions:
                combined_parts.append(f"Sample content: {' | '.join(processed_captions)}")
        
        combined_text = " ".join(combined_parts)
        
        # Truncate if too long (OpenAI has token limits)
        if len(combined_text) > 8000:  # Conservative limit
            combined_text = combined_text[:8000] + "..."
        
        return combined_text
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text using OpenAI API"""
        try:
            if not text.strip():
                raise ValueError("Cannot generate embedding for empty text")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with dimension: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embedding_sync(self, text: str) -> List[float]:
        """Synchronous version of embedding generation"""
        try:
            if not text.strip():
                raise ValueError("Cannot generate embedding for empty text")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with dimension: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_influencer_embedding(self, bio: Optional[str], captions: Optional[List[str]]) -> List[float]:
        """Generate embedding specifically for influencer data"""
        combined_text = self.combine_influencer_text(bio, captions)
        
        if not combined_text:
            raise ValueError("No valid text data provided for embedding generation")
        
        logger.info(f"Generating embedding for text: {combined_text[:100]}...")
        return await self.generate_embedding(combined_text)
    
    def generate_influencer_embedding_sync(self, bio: Optional[str], captions: Optional[List[str]]) -> List[float]:
        """Synchronous version of influencer embedding generation"""
        combined_text = self.combine_influencer_text(bio, captions)
        
        if not combined_text:
            raise ValueError("No valid text data provided for embedding generation")
        
        logger.info(f"Generating embedding for text: {combined_text[:100]}...")
        return self.generate_embedding_sync(combined_text)
    
    async def generate_query_embedding(self, query_text: str) -> List[float]:
        """Generate embedding for search query"""
        processed_query = self.preprocess_text(query_text)
        
        if not processed_query:
            raise ValueError("Query text is empty after preprocessing")
        
        return await self.generate_embedding(processed_query)
    
    def generate_query_embedding_sync(self, query_text: str) -> List[float]:
        """Synchronous version of query embedding generation"""
        processed_query = self.preprocess_text(query_text)
        
        if not processed_query:
            raise ValueError("Query text is empty after preprocessing")
        
        return self.generate_embedding_sync(processed_query)

# Global embedding service instance
embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Dependency to get embedding service instance"""
    global embedding_service
    if embedding_service is None:
        raise RuntimeError("Embedding service not initialized. Call init_embedding_service() first.")
    return embedding_service

def init_embedding_service(api_key: str, model: str = "text-embedding-3-large"):
    """Initialize embedding service"""
    global embedding_service
    embedding_service = EmbeddingService(api_key, model)
    logger.info("Embedding service initialized successfully")