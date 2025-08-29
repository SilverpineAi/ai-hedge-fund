"""
FastAPI application for Influencer Lookalike Engine.
Provides REST API endpoints for adding influencers and finding lookalikes.
"""

import os
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from db import (
    DatabaseManager, InfluencerCreate, InfluencerResponse, 
    get_database, init_database
)
from embeddings import (
    EmbeddingService, get_embedding_service, init_embedding_service
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Models
class FindLookalikesRequest(BaseModel):
    seed_handle: Optional[str] = Field(None, description="Handle of seed influencer")
    seed_bio: Optional[str] = Field(None, description="Raw bio text for search")
    top_k: int = Field(10, ge=1, le=50, description="Number of results to return")
    min_followers: Optional[int] = Field(None, ge=0, description="Minimum follower count filter")
    max_followers: Optional[int] = Field(None, ge=0, description="Maximum follower count filter")
    min_engagement: Optional[float] = Field(None, ge=0.0, le=100.0, description="Minimum engagement rate filter")

class FindLookalikesResponse(BaseModel):
    query_info: Dict[str, Any]
    results: List[InfluencerResponse]
    total_results: int

class HealthResponse(BaseModel):
    status: str
    message: str
    services: Dict[str, str]

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    try:
        # Initialize services
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "influencer-embeddings")
        database_url = os.getenv("DATABASE_URL", "sqlite:///./influencers.db")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        if not pinecone_environment:
            raise ValueError("PINECONE_ENVIRONMENT environment variable is required")
        
        # Initialize embedding service
        init_embedding_service(openai_api_key)
        
        # Initialize database
        init_database(database_url, pinecone_api_key, pinecone_environment, pinecone_index_name)
        
        logger.info("All services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        try:
            db = get_database()
            db.close()
            logger.info("Services cleaned up successfully")
        except:
            pass

# Create FastAPI app
app = FastAPI(
    title="Influencer Lookalike Engine",
    description="API for finding similar influencers using AI embeddings",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify service status"""
    try:
        # Check database connection
        db = get_database()
        db_status = "healthy"
        
        # Check embedding service
        embedding_service = get_embedding_service()
        embedding_status = "healthy"
        
        return HealthResponse(
            status="healthy",
            message="All services are operational",
            services={
                "database": db_status,
                "embeddings": embedding_status
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": str(e),
                "services": {
                    "database": "error",
                    "embeddings": "error"
                }
            }
        )

# Add influencer endpoint
@app.post("/add_influencer", response_model=InfluencerResponse)
async def add_influencer(influencer: InfluencerCreate, db: DatabaseManager = Depends(get_database), 
                        embedding_service: EmbeddingService = Depends(get_embedding_service)):
    """
    Add a new influencer to the system.
    Generates embeddings from bio and captions, stores in vector database.
    """
    try:
        # Check if influencer already exists
        existing = db.get_influencer_by_handle(influencer.handle)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Influencer with handle '{influencer.handle}' already exists"
            )
        
        # Generate embedding from bio and captions
        try:
            embedding = embedding_service.generate_influencer_embedding_sync(
                bio=influencer.bio,
                captions=influencer.captions
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate embedding: {str(e)}"
            )
        
        # Add influencer to database
        db_influencer = db.add_influencer(influencer, embedding)
        
        response = InfluencerResponse(
            id=db_influencer.id,
            handle=db_influencer.handle,
            bio=db_influencer.bio,
            follower_count=db_influencer.follower_count,
            engagement_rate=db_influencer.engagement_rate,
            niche_tags=db_influencer.niche_tags,
            profile_pic_url=db_influencer.profile_pic_url
        )
        
        logger.info(f"Successfully added influencer: {influencer.handle}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add influencer {influencer.handle}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Find lookalikes endpoint
@app.post("/find_lookalikes", response_model=FindLookalikesResponse)
async def find_lookalikes(request: FindLookalikesRequest, 
                         db: DatabaseManager = Depends(get_database),
                         embedding_service: EmbeddingService = Depends(get_embedding_service)):
    """
    Find similar influencers based on seed influencer handle or raw bio text.
    Returns ranked list of similar influencers with similarity scores.
    """
    try:
        query_embedding = None
        query_info = {}
        
        # Generate query embedding from seed handle or bio
        if request.seed_handle:
            # Find seed influencer in database
            seed_influencer = db.get_influencer_by_handle(request.seed_handle)
            if not seed_influencer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seed influencer '{request.seed_handle}' not found"
                )
            
            # Generate embedding from seed influencer's data
            query_embedding = embedding_service.generate_influencer_embedding_sync(
                bio=seed_influencer.bio,
                captions=[]  # We don't store captions in the database yet
            )
            query_info = {
                "type": "seed_handle",
                "seed_handle": request.seed_handle,
                "seed_bio": seed_influencer.bio
            }
            
        elif request.seed_bio:
            # Generate embedding from raw bio text
            query_embedding = embedding_service.generate_query_embedding_sync(request.seed_bio)
            query_info = {
                "type": "raw_bio",
                "seed_bio": request.seed_bio
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either seed_handle or seed_bio must be provided"
            )
        
        # Apply basic filters (more sophisticated filtering can be added later)
        filters = {}
        if request.min_followers is not None:
            filters["follower_count_min"] = request.min_followers
        if request.max_followers is not None:
            filters["follower_count_max"] = request.max_followers
        if request.min_engagement is not None:
            filters["engagement_rate_min"] = request.min_engagement
        
        # Find similar influencers
        similar_influencers = db.find_similar_influencers(
            query_embedding=query_embedding,
            top_k=request.top_k,
            filters=filters if filters else None
        )
        
        # Convert to response format
        results = []
        for influencer_data in similar_influencers:
            # Skip the seed influencer if it appears in results
            if request.seed_handle and influencer_data["handle"] == request.seed_handle:
                continue
                
            result = InfluencerResponse(
                id=influencer_data["id"],
                handle=influencer_data["handle"],
                bio=influencer_data["bio"],
                follower_count=influencer_data["follower_count"],
                engagement_rate=influencer_data["engagement_rate"],
                niche_tags=influencer_data["niche_tags"],
                profile_pic_url=influencer_data["profile_pic_url"],
                similarity_score=influencer_data["similarity_score"]
            )
            results.append(result)
        
        response = FindLookalikesResponse(
            query_info=query_info,
            results=results,
            total_results=len(results)
        )
        
        logger.info(f"Found {len(results)} similar influencers")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to find lookalikes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Get all influencers endpoint (for debugging/admin)
@app.get("/influencers", response_model=List[InfluencerResponse])
async def get_influencers(skip: int = 0, limit: int = 100, db: DatabaseManager = Depends(get_database)):
    """Get all influencers with pagination"""
    try:
        influencers = db.get_all_influencers(skip=skip, limit=limit)
        return [
            InfluencerResponse(
                id=inf.id,
                handle=inf.handle,
                bio=inf.bio,
                follower_count=inf.follower_count,
                engagement_rate=inf.engagement_rate,
                niche_tags=inf.niche_tags,
                profile_pic_url=inf.profile_pic_url
            )
            for inf in influencers
        ]
    except Exception as e:
        logger.error(f"Failed to get influencers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Delete influencer endpoint (for debugging/admin)
@app.delete("/influencers/{handle}")
async def delete_influencer(handle: str, db: DatabaseManager = Depends(get_database)):
    """Delete an influencer by handle"""
    try:
        success = db.delete_influencer(handle)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Influencer '{handle}' not found"
            )
        return {"message": f"Influencer '{handle}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete influencer {handle}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )