from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

class InfluencerCategory(str, Enum):
    FASHION = "fashion"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    GAMING = "gaming"
    HEALTH = "health"
    EDUCATION = "education"
    ART = "art"
    MUSIC = "music"
    PHOTOGRAPHY = "photography"
    PETS = "pets"
    PARENTING = "parenting"
    HOME_DECOR = "home_decor"
    AUTOMOTIVE = "automotive"
    SPORTS = "sports"

class InfluencerTier(str, Enum):
    NANO = "nano"  # 1K-10K followers
    MICRO = "micro"  # 10K-100K followers  
    MID = "mid"  # 100K-1M followers
    MACRO = "macro"  # 1M-10M followers
    MEGA = "mega"  # 10M+ followers

class InfluencerMetrics(BaseModel):
    followers_count: int
    following_count: int
    posts_count: int
    engagement_rate: Optional[float] = None
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None
    avg_views: Optional[int] = None
    verified: bool = False
    business_account: bool = False

class InfluencerContact(BaseModel):
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    business_phone: Optional[str] = None
    business_address: Optional[str] = None

class InfluencerProfile(BaseModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_pic_url: Optional[HttpUrl] = None
    category: Optional[InfluencerCategory] = None
    tier: Optional[InfluencerTier] = None
    location: Optional[str] = None
    contact_info: Optional[InfluencerContact] = None
    metrics: InfluencerMetrics
    last_updated: datetime
    estimated_cost_per_post: Optional[float] = None
    content_quality_score: Optional[float] = None
    brand_safety_score: Optional[float] = None

class InfluencerSearchRequest(BaseModel):
    keywords: Optional[List[str]] = []
    categories: Optional[List[InfluencerCategory]] = []
    min_followers: Optional[int] = 1000
    max_followers: Optional[int] = 10000000
    min_engagement_rate: Optional[float] = 1.0
    max_engagement_rate: Optional[float] = 20.0
    location: Optional[str] = None
    verified_only: bool = False
    business_accounts_only: bool = False
    limit: int = 20

class InfluencerSearchResponse(BaseModel):
    influencers: List[InfluencerProfile]
    total_found: int
    search_params: InfluencerSearchRequest
    export_available: bool = True

class InfluencerAnalytics(BaseModel):
    username: str
    recent_posts_engagement: List[float]
    best_posting_times: List[str]
    top_hashtags: List[str]
    audience_demographics: dict
    brand_mentions: List[str]
    collaboration_history: List[str]