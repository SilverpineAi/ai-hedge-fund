from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import List
import io
import asyncio

from ..models.influencer import (
    InfluencerSearchRequest, InfluencerSearchResponse, 
    InfluencerProfile, InfluencerAnalytics, InfluencerCategory
)
from ..services.influencer_discovery import InfluencerDiscoveryService

router = APIRouter(prefix="/api/influencers", tags=["influencers"])

# Initialize the service
influencer_service = InfluencerDiscoveryService()

@router.post("/search", response_model=InfluencerSearchResponse)
async def search_influencers(search_request: InfluencerSearchRequest):
    """
    Search for Instagram influencers based on various criteria
    """
    try:
        result = await influencer_service.search_influencers(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/categories", response_model=List[str])
async def get_categories():
    """
    Get list of available influencer categories
    """
    return [category.value for category in InfluencerCategory]

@router.get("/{username}/analytics", response_model=InfluencerAnalytics)
async def get_influencer_analytics(username: str):
    """
    Get detailed analytics for a specific influencer
    """
    try:
        analytics = await influencer_service.get_influencer_analytics(username)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/export/csv")
async def export_influencers_csv(influencers: List[InfluencerProfile]):
    """
    Export influencer data to CSV format
    """
    try:
        csv_content = influencer_service.export_to_csv(influencers)
        
        # Create a BytesIO object to serve as file
        csv_buffer = io.StringIO(csv_content)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(csv_content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=influencers.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/search/trending")
async def get_trending_influencers(limit: int = 20):
    """
    Get trending influencers (mock data for demonstration)
    """
    try:
        # Create a search request for trending content
        search_request = InfluencerSearchRequest(
            keywords=["trending", "viral", "popular"],
            min_followers=10000,
            max_followers=5000000,
            min_engagement_rate=3.0,
            limit=limit
        )
        
        result = await influencer_service.search_influencers(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending influencers: {str(e)}")

@router.get("/search/by-category/{category}")
async def search_by_category(category: InfluencerCategory, limit: int = 20):
    """
    Search influencers by specific category
    """
    try:
        search_request = InfluencerSearchRequest(
            categories=[category],
            keywords=[category.value],
            min_followers=1000,
            limit=limit
        )
        
        result = await influencer_service.search_influencers(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category search failed: {str(e)}")

@router.get("/search/by-tier/{tier}")
async def search_by_tier(tier: str, limit: int = 20):
    """
    Search influencers by tier (nano, micro, mid, macro, mega)
    """
    try:
        # Define follower ranges for each tier
        tier_ranges = {
            "nano": (1000, 10000),
            "micro": (10000, 100000),
            "mid": (100000, 1000000),
            "macro": (1000000, 10000000),
            "mega": (10000000, 100000000)
        }
        
        if tier not in tier_ranges:
            raise HTTPException(status_code=400, detail="Invalid tier. Use: nano, micro, mid, macro, mega")
        
        min_followers, max_followers = tier_ranges[tier]
        
        search_request = InfluencerSearchRequest(
            min_followers=min_followers,
            max_followers=max_followers,
            limit=limit
        )
        
        result = await influencer_service.search_influencers(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tier search failed: {str(e)}")

@router.get("/stats/summary")
async def get_summary_stats():
    """
    Get summary statistics about available influencers
    """
    try:
        # Mock summary statistics
        return {
            "total_influencers": 125000,
            "categories": {
                "fashion": 25000,
                "beauty": 22000,
                "lifestyle": 20000,
                "fitness": 18000,
                "food": 15000,
                "travel": 12000,
                "technology": 8000,
                "business": 5000
            },
            "tiers": {
                "nano": 60000,
                "micro": 40000,
                "mid": 20000,
                "macro": 4500,
                "mega": 500
            },
            "verified_accounts": 15000,
            "business_accounts": 75000,
            "avg_engagement_rate": 4.2,
            "top_locations": ["United States", "United Kingdom", "Canada", "Australia", "Germany"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary stats: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "influencer_discovery"}