"""
Database management for influencer metadata and Pinecone vector operations.
Handles both SQLite/Postgres for structured data and Pinecone for embeddings.
"""

import os
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
import pinecone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

class Influencer(Base):
    """SQLAlchemy model for influencer metadata"""
    __tablename__ = "influencers"
    
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String(100), unique=True, index=True, nullable=False)
    bio = Column(Text, nullable=True)
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    niche_tags = Column(Text, nullable=True)  # JSON string of tags
    profile_pic_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API
class InfluencerCreate(BaseModel):
    handle: str
    bio: Optional[str] = None
    captions: Optional[List[str]] = []
    follower_count: Optional[int] = 0
    engagement_rate: Optional[float] = 0.0
    niche_tags: Optional[List[str]] = []
    profile_pic_url: Optional[str] = None

class InfluencerResponse(BaseModel):
    id: int
    handle: str
    bio: Optional[str]
    follower_count: int
    engagement_rate: float
    niche_tags: Optional[str]
    profile_pic_url: Optional[str]
    similarity_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class DatabaseManager:
    """Manages both SQL database and Pinecone vector database operations"""
    
    def __init__(self, database_url: str, pinecone_api_key: str, pinecone_environment: str, index_name: str):
        # Initialize SQL database
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()
        
        # Initialize Pinecone
        try:
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {index_name}")
                pinecone.create_index(
                    name=index_name,
                    dimension=3072,  # OpenAI text-embedding-3-large dimension
                    metric='cosine'
                )
            
            self.index = pinecone.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def add_influencer(self, influencer_data: InfluencerCreate, embedding: List[float]) -> Influencer:
        """Add influencer to both SQL database and Pinecone vector store"""
        try:
            # Create influencer in SQL database
            db_influencer = Influencer(
                handle=influencer_data.handle,
                bio=influencer_data.bio,
                follower_count=influencer_data.follower_count,
                engagement_rate=influencer_data.engagement_rate,
                niche_tags=','.join(influencer_data.niche_tags) if influencer_data.niche_tags else None,
                profile_pic_url=influencer_data.profile_pic_url
            )
            
            self.session.add(db_influencer)
            self.session.commit()
            self.session.refresh(db_influencer)
            
            # Store embedding in Pinecone with metadata
            metadata = {
                "handle": influencer_data.handle,
                "bio": influencer_data.bio or "",
                "follower_count": influencer_data.follower_count,
                "engagement_rate": influencer_data.engagement_rate,
                "niche_tags": ','.join(influencer_data.niche_tags) if influencer_data.niche_tags else ""
            }
            
            self.index.upsert([(str(db_influencer.id), embedding, metadata)])
            logger.info(f"Added influencer {influencer_data.handle} with ID {db_influencer.id}")
            
            return db_influencer
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to add influencer {influencer_data.handle}: {e}")
            raise
    
    def find_similar_influencers(self, query_embedding: List[float], top_k: int = 10, 
                               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find similar influencers using vector similarity search"""
        try:
            # Query Pinecone for similar embeddings
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            results = []
            for match in query_response.matches:
                influencer_id = int(match.id)
                similarity_score = match.score
                
                # Get full influencer data from SQL database
                db_influencer = self.session.query(Influencer).filter(Influencer.id == influencer_id).first()
                
                if db_influencer:
                    influencer_dict = {
                        "id": db_influencer.id,
                        "handle": db_influencer.handle,
                        "bio": db_influencer.bio,
                        "follower_count": db_influencer.follower_count,
                        "engagement_rate": db_influencer.engagement_rate,
                        "niche_tags": db_influencer.niche_tags,
                        "profile_pic_url": db_influencer.profile_pic_url,
                        "similarity_score": float(similarity_score)
                    }
                    results.append(influencer_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar influencers: {e}")
            raise
    
    def get_influencer_by_handle(self, handle: str) -> Optional[Influencer]:
        """Get influencer by handle from SQL database"""
        return self.session.query(Influencer).filter(Influencer.handle == handle).first()
    
    def get_all_influencers(self, skip: int = 0, limit: int = 100) -> List[Influencer]:
        """Get all influencers with pagination"""
        return self.session.query(Influencer).offset(skip).limit(limit).all()
    
    def delete_influencer(self, handle: str) -> bool:
        """Delete influencer from both databases"""
        try:
            db_influencer = self.get_influencer_by_handle(handle)
            if not db_influencer:
                return False
            
            # Delete from Pinecone
            self.index.delete(ids=[str(db_influencer.id)])
            
            # Delete from SQL database
            self.session.delete(db_influencer)
            self.session.commit()
            
            logger.info(f"Deleted influencer {handle}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to delete influencer {handle}: {e}")
            raise
    
    def close(self):
        """Close database connections"""
        self.session.close()

# Global database instance
db_manager: Optional[DatabaseManager] = None

def get_database() -> DatabaseManager:
    """Dependency to get database instance"""
    global db_manager
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_manager

def init_database(database_url: str, pinecone_api_key: str, pinecone_environment: str, index_name: str):
    """Initialize database connections"""
    global db_manager
    db_manager = DatabaseManager(database_url, pinecone_api_key, pinecone_environment, index_name)
    logger.info("Database initialized successfully")