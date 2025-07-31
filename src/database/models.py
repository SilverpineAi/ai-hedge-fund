"""
Database Models

SQLAlchemy models for the influencer discovery application.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import enum

Base = declarative_base()

class PlatformEnum(enum.Enum):
    """Enum for social media platforms"""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"

class CategoryEnum(enum.Enum):
    """Enum for influencer categories"""
    FITNESS = "fitness"
    FASHION = "fashion"
    FOOD = "food"
    TRAVEL = "travel"
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    BEAUTY = "beauty"
    CRYPTO = "crypto"
    FINANCE = "finance"
    NEWS = "news"
    EDUCATION = "education"
    HEALTH = "health"

class CampaignStatusEnum(enum.Enum):
    """Enum for campaign statuses"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Influencer(Base):
    """Influencer model"""
    __tablename__ = "influencers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    display_name = Column(String(200))
    platform = Column(Enum(PlatformEnum), nullable=False, index=True)
    follower_count = Column(Integer, default=0, index=True)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    bio = Column(Text)
    profile_image_url = Column(String(500))
    verified = Column(Boolean, default=False, index=True)
    engagement_rate = Column(Float, default=0.0, index=True)
    average_likes = Column(Float, default=0.0)
    average_comments = Column(Float, default=0.0)
    category = Column(Enum(CategoryEnum), index=True)
    location = Column(String(200))
    external_url = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_scraped_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    
    # Additional analysis data
    authenticity_score = Column(Float, default=0.0)  # AI-calculated authenticity
    brand_safety_score = Column(Float, default=0.0)  # Brand safety rating
    content_quality_score = Column(Float, default=0.0)  # Content quality rating
    audience_demographics = Column(JSON)  # Age, gender, location breakdown
    top_hashtags = Column(JSON)  # Most used hashtags
    collaboration_rate = Column(Float, default=0.0)  # Rate of sponsored content
    
    # Relationships
    posts = relationship("Post", back_populates="influencer", cascade="all, delete-orphan")
    metrics = relationship("InfluencerMetrics", back_populates="influencer", cascade="all, delete-orphan")
    brand_matches = relationship("BrandInfluencerMatch", back_populates="influencer")
    campaign_participations = relationship("CampaignInfluencer", back_populates="influencer")
    
    def __repr__(self):
        return f"<Influencer(username={self.username}, platform={self.platform.value}, followers={self.follower_count})>"

class Brand(Base):
    """Brand model"""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100), index=True)
    website = Column(String(500))
    logo_url = Column(String(500))
    
    # Brand preferences for influencer matching
    target_categories = Column(JSON)  # List of preferred categories
    min_followers = Column(Integer, default=1000)
    max_followers = Column(Integer)
    min_engagement_rate = Column(Float, default=1.0)
    target_demographics = Column(JSON)  # Age, gender, location preferences
    budget_range = Column(JSON)  # Min/max budget
    brand_values = Column(JSON)  # List of brand values/keywords
    
    # Contact information
    contact_email = Column(String(200))
    contact_name = Column(String(200))
    contact_phone = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="brand", cascade="all, delete-orphan")
    influencer_matches = relationship("BrandInfluencerMatch", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(name={self.name}, industry={self.industry})>"

class Campaign(Base):
    """Marketing campaign model"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    objectives = Column(JSON)  # Campaign objectives/goals
    
    # Campaign details
    budget = Column(Float)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(Enum(CampaignStatusEnum), default=CampaignStatusEnum.DRAFT, index=True)
    
    # Target criteria
    target_platforms = Column(JSON)  # List of platforms
    target_categories = Column(JSON)  # List of categories
    target_demographics = Column(JSON)  # Demographics
    min_followers = Column(Integer, default=1000)
    max_followers = Column(Integer)
    min_engagement_rate = Column(Float, default=1.0)
    
    # Campaign content
    content_guidelines = Column(Text)
    hashtags = Column(JSON)  # Required hashtags
    mentions = Column(JSON)  # Required mentions
    deliverables = Column(JSON)  # Expected deliverables
    
    # Performance metrics
    total_reach = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    roi = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="campaigns")
    influencer_participations = relationship("CampaignInfluencer", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign(name={self.name}, brand_id={self.brand_id}, status={self.status.value})>"

class Post(Base):
    """Social media post model"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False, index=True)
    platform_post_id = Column(String(100), nullable=False)  # Original post ID from platform
    
    # Post content
    caption = Column(Text)
    media_urls = Column(JSON)  # List of image/video URLs
    post_type = Column(String(50))  # photo, video, carousel, story, etc.
    
    # Post metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    
    # Post analysis
    hashtags = Column(JSON)  # List of hashtags used
    mentions = Column(JSON)  # List of mentions
    sentiment_score = Column(Float, default=0.0)  # AI-calculated sentiment
    is_sponsored = Column(Boolean, default=False)  # AI-detected sponsored content
    brand_mentions = Column(JSON)  # Detected brand mentions
    
    # Timestamps
    posted_at = Column(DateTime(timezone=True), nullable=False, index=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    influencer = relationship("Influencer", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.platform_post_id}, influencer_id={self.influencer_id}, likes={self.likes_count})>"

class InfluencerMetrics(Base):
    """Time-series metrics for influencers"""
    __tablename__ = "influencer_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False, index=True)
    
    # Snapshot metrics
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    average_likes = Column(Float, default=0.0)
    average_comments = Column(Float, default=0.0)
    
    # Growth metrics
    follower_growth = Column(Integer, default=0)  # Change since last measurement
    engagement_growth = Column(Float, default=0.0)
    
    # Advanced metrics
    reach_rate = Column(Float, default=0.0)
    impression_rate = Column(Float, default=0.0)
    save_rate = Column(Float, default=0.0)
    share_rate = Column(Float, default=0.0)
    
    # Timestamp
    measured_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    influencer = relationship("Influencer", back_populates="metrics")
    
    def __repr__(self):
        return f"<InfluencerMetrics(influencer_id={self.influencer_id}, measured_at={self.measured_at})>"

class BrandInfluencerMatch(Base):
    """Brand-Influencer matching results"""
    __tablename__ = "brand_influencer_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False, index=True)
    
    # Matching scores
    overall_score = Column(Float, nullable=False, index=True)  # Overall match score (0-100)
    category_score = Column(Float, default=0.0)  # Category alignment score
    audience_score = Column(Float, default=0.0)  # Audience alignment score
    engagement_score = Column(Float, default=0.0)  # Engagement quality score
    authenticity_score = Column(Float, default=0.0)  # Authenticity score
    brand_safety_score = Column(Float, default=0.0)  # Brand safety score
    
    # Predicted metrics
    estimated_reach = Column(Integer, default=0)
    estimated_engagement = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    roi_prediction = Column(Float, default=0.0)
    
    # Match metadata
    match_reasons = Column(JSON)  # List of reasons for the match
    potential_concerns = Column(JSON)  # List of potential concerns
    recommended_content_types = Column(JSON)  # Recommended content formats
    
    # Status
    is_contacted = Column(Boolean, default=False)
    contact_status = Column(String(50))  # interested, declined, negotiating, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="influencer_matches")
    influencer = relationship("Influencer", back_populates="brand_matches")
    
    def __repr__(self):
        return f"<BrandInfluencerMatch(brand_id={self.brand_id}, influencer_id={self.influencer_id}, score={self.overall_score})>"

class CampaignInfluencer(Base):
    """Campaign-Influencer participation"""
    __tablename__ = "campaign_influencers"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False, index=True)
    
    # Participation details
    agreed_deliverables = Column(JSON)  # What the influencer agreed to deliver
    compensation = Column(Float)  # Agreed compensation
    deadline = Column(DateTime(timezone=True))
    status = Column(String(50), default="invited")  # invited, accepted, declined, completed
    
    # Performance tracking
    posts_delivered = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Content tracking
    delivered_content = Column(JSON)  # List of delivered post IDs/URLs
    performance_metrics = Column(JSON)  # Detailed performance data
    
    # Timestamps
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    campaign = relationship("Campaign", back_populates="influencer_participations")
    influencer = relationship("Influencer", back_populates="campaign_participations")
    
    def __repr__(self):
        return f"<CampaignInfluencer(campaign_id={self.campaign_id}, influencer_id={self.influencer_id}, status={self.status})>"