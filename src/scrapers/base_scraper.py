"""
Base Scraper Class

Abstract base class for all social media scrapers.
Provides common functionality and interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import time
import logging
import random

logger = logging.getLogger(__name__)

@dataclass
class InfluencerProfile:
    """Data class for influencer profile information"""
    username: str
    display_name: str
    platform: str
    follower_count: int
    following_count: int
    post_count: int
    bio: str
    profile_image_url: str
    verified: bool
    engagement_rate: float
    average_likes: float
    average_comments: float
    category: str
    location: str
    external_url: str
    posts: List[Dict[str, Any]]
    scraped_at: datetime

@dataclass
class PostData:
    """Data class for individual post information"""
    post_id: str
    caption: str
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    post_type: str  # photo, video, carousel, etc.
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    posted_at: datetime

class BaseScraper(ABC):
    """Abstract base class for social media scrapers"""
    
    def __init__(self, rate_limit: float = 1.0, max_retries: int = 3):
        """
        Initialize the scraper
        
        Args:
            rate_limit: Minimum time between requests (seconds)
            max_retries: Maximum number of retries for failed requests
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.last_request_time = 0
        
    def _rate_limit_delay(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            # Add small random delay to avoid detection
            sleep_time += random.uniform(0.1, 0.5)
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _retry_request(self, func, *args, **kwargs):
        """Retry a request with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                self._rate_limit_delay()
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {delay:.2f}s: {e}")
                time.sleep(delay)
    
    @abstractmethod
    def get_profile(self, username: str) -> Optional[InfluencerProfile]:
        """
        Get profile information for a user
        
        Args:
            username: Username to scrape
            
        Returns:
            InfluencerProfile object or None if not found
        """
        pass
    
    @abstractmethod
    def search_influencers(self, 
                          keyword: str, 
                          min_followers: int = 1000,
                          max_results: int = 100) -> List[InfluencerProfile]:
        """
        Search for influencers based on keywords
        
        Args:
            keyword: Search keyword/hashtag
            min_followers: Minimum follower count
            max_results: Maximum number of results
            
        Returns:
            List of InfluencerProfile objects
        """
        pass
    
    @abstractmethod
    def get_posts(self, username: str, limit: int = 50) -> List[PostData]:
        """
        Get recent posts for a user
        
        Args:
            username: Username to get posts for
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of PostData objects
        """
        pass
    
    def calculate_engagement_rate(self, posts: List[PostData], follower_count: int) -> float:
        """
        Calculate engagement rate based on posts
        
        Args:
            posts: List of posts
            follower_count: Number of followers
            
        Returns:
            Engagement rate as percentage
        """
        if not posts or follower_count == 0:
            return 0.0
            
        total_engagement = sum(
            post.likes_count + post.comments_count + post.shares_count 
            for post in posts
        )
        
        avg_engagement = total_engagement / len(posts)
        engagement_rate = (avg_engagement / follower_count) * 100
        
        return round(engagement_rate, 2)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        mentions = re.findall(r'@(\w+)', text)
        return mentions
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep emojis
        import re
        text = re.sub(r'[^\w\s#@.,!?-]', '', text)
        
        return text.strip()
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the name of the platform"""
        pass