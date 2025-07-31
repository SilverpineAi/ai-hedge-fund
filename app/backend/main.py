"""
FastAPI Backend for Influencer Discovery App

Main FastAPI application providing REST API endpoints for influencer discovery,
analysis, and brand matching functionality.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Import application modules
from src.scrapers import InstagramScraper, TwitterScraper
from src.agents import BrandMatchingAgent
from src.database.models import Influencer, Brand, Campaign, PlatformEnum, CategoryEnum
from src.database.connection import get_database_session

logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="Influencer Discovery API",
    description="AI-powered influencer discovery and brand matching platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scrapers and agents
scrapers = {}
agents = {}

@app.on_event("startup")
async def startup_event():
    """Initialize scrapers and agents on startup"""
    try:
        # Initialize scrapers
        scrapers['instagram'] = InstagramScraper(rate_limit=2.0)
        scrapers['twitter'] = TwitterScraper(rate_limit=1.0)
        
        # Initialize agents
        agents['brand_matching'] = BrandMatchingAgent()
        
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Pydantic models for API
class InfluencerSearchRequest(BaseModel):
    platform: str = Field(..., description="Social media platform")
    keyword: str = Field(..., description="Search keyword or hashtag")
    min_followers: int = Field(1000, description="Minimum follower count")
    max_results: int = Field(50, description="Maximum number of results")

class InfluencerAnalysisRequest(BaseModel):
    username: str = Field(..., description="Influencer username")
    platform: str = Field(..., description="Social media platform")

class BrandRequirements(BaseModel):
    name: str = Field(..., description="Brand name")
    industry: str = Field(..., description="Brand industry")
    description: Optional[str] = Field(None, description="Brand description")
    target_categories: List[str] = Field([], description="Target influencer categories")
    min_followers: int = Field(1000, description="Minimum follower count")
    max_followers: Optional[int] = Field(None, description="Maximum follower count")
    min_engagement_rate: float = Field(1.0, description="Minimum engagement rate")
    target_demographics: Dict[str, Any] = Field({}, description="Target demographics")
    budget_range: Dict[str, float] = Field({}, description="Budget range")
    brand_values: List[str] = Field([], description="Brand values")

class BrandMatchingRequest(BaseModel):
    brand: BrandRequirements
    influencer_ids: Optional[List[int]] = Field(None, description="Specific influencer IDs to match")
    platform: Optional[str] = Field(None, description="Filter by platform")
    category: Optional[str] = Field(None, description="Filter by category")
    max_results: int = Field(20, description="Maximum number of matches")

class CampaignCreateRequest(BaseModel):
    brand_id: int
    name: str
    description: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_platforms: List[str] = []
    target_categories: List[str] = []
    min_followers: int = 1000
    max_followers: Optional[int] = None
    min_engagement_rate: float = 1.0

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Influencer Discovery API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scrapers": list(scrapers.keys()),
        "agents": list(agents.keys())
    }

@app.post("/api/influencers/search")
async def search_influencers(request: InfluencerSearchRequest):
    """
    Search for influencers on social media platforms
    
    Args:
        request: Search parameters
        
    Returns:
        List of discovered influencer profiles
    """
    try:
        if request.platform not in scrapers:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported platform: {request.platform}"
            )
        
        scraper = scrapers[request.platform]
        
        # Perform search
        influencers = scraper.search_influencers(
            keyword=request.keyword,
            min_followers=request.min_followers,
            max_results=request.max_results
        )
        
        # Convert to dictionaries
        results = [inf.__dict__ for inf in influencers]
        
        return {
            "success": True,
            "count": len(results),
            "platform": request.platform,
            "keyword": request.keyword,
            "influencers": results
        }
        
    except Exception as e:
        logger.error(f"Error searching influencers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/influencers/analyze")
async def analyze_influencer(request: InfluencerAnalysisRequest):
    """
    Analyze a specific influencer profile
    
    Args:
        request: Analysis parameters
        
    Returns:
        Detailed influencer analysis
    """
    try:
        if request.platform not in scrapers:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform: {request.platform}"
            )
        
        scraper = scrapers[request.platform]
        
        # Get profile data
        profile = scraper.get_profile(request.username)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile @{request.username} not found on {request.platform}"
            )
        
        # Convert to dict
        profile_dict = profile.__dict__
        
        return {
            "success": True,
            "platform": request.platform,
            "username": request.username,
            "profile": profile_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing influencer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brands/{brand_id}/match")
async def match_influencers_with_brand(
    brand_id: int,
    request: BrandMatchingRequest,
    db: Session = Depends(get_database_session)
):
    """
    Find matching influencers for a brand
    
    Args:
        brand_id: Brand ID
        request: Matching parameters
        db: Database session
        
    Returns:
        List of brand-influencer matches
    """
    try:
        # Get brand from database
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Get brand matching agent
        if 'brand_matching' not in agents:
            raise HTTPException(status_code=500, detail="Brand matching agent not available")
        
        agent = agents['brand_matching']
        
        # Get influencers to match
        query = db.query(Influencer).filter(Influencer.is_active == True)
        
        if request.influencer_ids:
            query = query.filter(Influencer.id.in_(request.influencer_ids))
        
        if request.platform:
            query = query.filter(Influencer.platform == request.platform)
        
        if request.category:
            query = query.filter(Influencer.category == request.category)
        
        # Apply brand filters
        query = query.filter(Influencer.follower_count >= request.brand.min_followers)
        if request.brand.max_followers:
            query = query.filter(Influencer.follower_count <= request.brand.max_followers)
        
        query = query.filter(Influencer.engagement_rate >= request.brand.min_engagement_rate)
        
        # Get influencers
        influencers = query.limit(request.max_results * 2).all()  # Get more for better matching
        
        if not influencers:
            return {
                "success": True,
                "brand_id": brand_id,
                "matches": []
            }
        
        # Convert to dicts for analysis
        influencer_dicts = []
        for inf in influencers:
            inf_dict = {
                'id': inf.id,
                'username': inf.username,
                'platform': inf.platform.value,
                'follower_count': inf.follower_count,
                'engagement_rate': inf.engagement_rate,
                'category': inf.category.value if inf.category else 'lifestyle',
                'bio': inf.bio,
                'verified': inf.verified,
                'average_likes': inf.average_likes,
                'average_comments': inf.average_comments,
                'authenticity_score': inf.authenticity_score,
                'content_quality_score': inf.content_quality_score,
                'brand_safety_score': inf.brand_safety_score,
                'top_hashtags': inf.top_hashtags or [],
                'posts': []  # Would need to load posts separately
            }
            influencer_dicts.append(inf_dict)
        
        # Brand data for matching
        brand_dict = {
            'name': request.brand.name,
            'industry': request.brand.industry,
            'description': request.brand.description,
            'target_categories': request.brand.target_categories,
            'min_followers': request.brand.min_followers,
            'max_followers': request.brand.max_followers,
            'min_engagement_rate': request.brand.min_engagement_rate,
            'target_demographics': request.brand.target_demographics,
            'budget_range': request.brand.budget_range,
            'brand_values': request.brand.brand_values
        }
        
        # Perform matching
        matches = []
        for inf_dict in influencer_dicts[:request.max_results]:
            try:
                result = agent.analyze({
                    'influencer': inf_dict,
                    'brand': brand_dict
                })
                
                match_data = {
                    'influencer_id': inf_dict['id'],
                    'username': inf_dict['username'],
                    'platform': inf_dict['platform'],
                    'match_analysis': result.analysis_data,
                    'confidence': result.confidence_score
                }
                
                matches.append(match_data)
                
            except Exception as e:
                logger.error(f"Error matching influencer {inf_dict['username']}: {e}")
                continue
        
        # Sort by overall score
        matches.sort(key=lambda x: x['match_analysis'].get('overall_score', 0), reverse=True)
        
        return {
            "success": True,
            "brand_id": brand_id,
            "brand_name": brand.name,
            "total_analyzed": len(matches),
            "matches": matches[:request.max_results]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching influencers with brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/influencers")
async def get_influencers(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_followers: int = Query(0, description="Minimum follower count"),
    max_followers: Optional[int] = Query(None, description="Maximum follower count"),
    verified_only: bool = Query(False, description="Only verified influencers"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_database_session)
):
    """
    Get influencers from database with filtering
    
    Returns:
        List of influencers matching the criteria
    """
    try:
        query = db.query(Influencer).filter(Influencer.is_active == True)
        
        # Apply filters
        if platform:
            query = query.filter(Influencer.platform == platform)
        
        if category:
            query = query.filter(Influencer.category == category)
        
        query = query.filter(Influencer.follower_count >= min_followers)
        
        if max_followers:
            query = query.filter(Influencer.follower_count <= max_followers)
        
        if verified_only:
            query = query.filter(Influencer.verified == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        influencers = query.offset(offset).limit(limit).all()
        
        # Convert to dicts
        results = []
        for inf in influencers:
            inf_dict = {
                'id': inf.id,
                'username': inf.username,
                'display_name': inf.display_name,
                'platform': inf.platform.value,
                'follower_count': inf.follower_count,
                'following_count': inf.following_count,
                'post_count': inf.post_count,
                'bio': inf.bio,
                'profile_image_url': inf.profile_image_url,
                'verified': inf.verified,
                'engagement_rate': inf.engagement_rate,
                'average_likes': inf.average_likes,
                'average_comments': inf.average_comments,
                'category': inf.category.value if inf.category else None,
                'location': inf.location,
                'authenticity_score': inf.authenticity_score,
                'brand_safety_score': inf.brand_safety_score,
                'content_quality_score': inf.content_quality_score,
                'created_at': inf.created_at.isoformat() if inf.created_at else None,
                'last_scraped_at': inf.last_scraped_at.isoformat() if inf.last_scraped_at else None
            }
            results.append(inf_dict)
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "influencers": results
        }
        
    except Exception as e:
        logger.error(f"Error getting influencers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/influencers/{influencer_id}")
async def get_influencer(
    influencer_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Get detailed information about a specific influencer
    
    Args:
        influencer_id: Influencer ID
        db: Database session
        
    Returns:
        Detailed influencer information
    """
    try:
        influencer = db.query(Influencer).filter(Influencer.id == influencer_id).first()
        
        if not influencer:
            raise HTTPException(status_code=404, detail="Influencer not found")
        
        # Convert to dict with all details
        result = {
            'id': influencer.id,
            'username': influencer.username,
            'display_name': influencer.display_name,
            'platform': influencer.platform.value,
            'follower_count': influencer.follower_count,
            'following_count': influencer.following_count,
            'post_count': influencer.post_count,
            'bio': influencer.bio,
            'profile_image_url': influencer.profile_image_url,
            'verified': influencer.verified,
            'engagement_rate': influencer.engagement_rate,
            'average_likes': influencer.average_likes,
            'average_comments': influencer.average_comments,
            'category': influencer.category.value if influencer.category else None,
            'location': influencer.location,
            'external_url': influencer.external_url,
            'authenticity_score': influencer.authenticity_score,
            'brand_safety_score': influencer.brand_safety_score,
            'content_quality_score': influencer.content_quality_score,
            'audience_demographics': influencer.audience_demographics,
            'top_hashtags': influencer.top_hashtags,
            'collaboration_rate': influencer.collaboration_rate,
            'created_at': influencer.created_at.isoformat() if influencer.created_at else None,
            'updated_at': influencer.updated_at.isoformat() if influencer.updated_at else None,
            'last_scraped_at': influencer.last_scraped_at.isoformat() if influencer.last_scraped_at else None,
            'posts': []  # Would load recent posts here
        }
        
        return {
            "success": True,
            "influencer": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting influencer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/platforms")
async def get_platforms():
    """Get supported social media platforms"""
    return {
        "success": True,
        "platforms": [
            {
                "name": "instagram",
                "display_name": "Instagram",
                "supported_features": ["profile_analysis", "hashtag_search", "post_scraping"]
            },
            {
                "name": "twitter",
                "display_name": "Twitter/X", 
                "supported_features": ["profile_analysis", "keyword_search", "tweet_scraping"]
            }
        ]
    }

@app.get("/api/categories")
async def get_categories():
    """Get supported influencer categories"""
    categories = [
        {"name": "fitness", "display_name": "Fitness & Health"},
        {"name": "fashion", "display_name": "Fashion & Style"},
        {"name": "food", "display_name": "Food & Cooking"},
        {"name": "travel", "display_name": "Travel & Adventure"},
        {"name": "tech", "display_name": "Technology"},
        {"name": "lifestyle", "display_name": "Lifestyle"},
        {"name": "business", "display_name": "Business & Entrepreneurship"},
        {"name": "entertainment", "display_name": "Entertainment"},
        {"name": "sports", "display_name": "Sports"},
        {"name": "beauty", "display_name": "Beauty & Cosmetics"},
        {"name": "crypto", "display_name": "Cryptocurrency"},
        {"name": "finance", "display_name": "Finance & Investing"},
        {"name": "news", "display_name": "News & Media"},
        {"name": "education", "display_name": "Education"},
        {"name": "health", "display_name": "Health & Wellness"}
    ]
    
    return {
        "success": True,
        "categories": categories
    }

@app.post("/api/scrape/platform/{platform}")
async def trigger_platform_scraping(
    platform: str,
    background_tasks: BackgroundTasks,
    keywords: List[str] = Query(..., description="Keywords to scrape"),
    max_results: int = Query(100, description="Maximum results per keyword")
):
    """
    Trigger background scraping for a platform
    
    Args:
        platform: Social media platform
        background_tasks: FastAPI background tasks
        keywords: List of keywords to scrape
        max_results: Maximum results per keyword
        
    Returns:
        Task confirmation
    """
    if platform not in scrapers:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}"
        )
    
    # Add background scraping task
    background_tasks.add_task(
        background_scraping_task,
        platform,
        keywords,
        max_results
    )
    
    return {
        "success": True,
        "message": f"Started background scraping for {platform}",
        "platform": platform,
        "keywords": keywords,
        "max_results": max_results
    }

async def background_scraping_task(platform: str, keywords: List[str], max_results: int):
    """Background task for scraping social media platforms"""
    try:
        scraper = scrapers[platform]
        
        for keyword in keywords:
            logger.info(f"Scraping {platform} for keyword: {keyword}")
            
            influencers = scraper.search_influencers(
                keyword=keyword,
                min_followers=1000,
                max_results=max_results
            )
            
            logger.info(f"Found {len(influencers)} influencers for keyword: {keyword}")
            
            # Here you would save the influencers to the database
            # This is a simplified version - you'd want proper database handling
            
    except Exception as e:
        logger.error(f"Error in background scraping task: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
