"""
Instagram Scraper

Scrapes Instagram profiles and posts to discover influencers.
Uses instaloader and web scraping techniques.
"""

import instaloader
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json

from .base_scraper import BaseScraper, InfluencerProfile, PostData

logger = logging.getLogger(__name__)

class InstagramScraper(BaseScraper):
    """Instagram scraper using instaloader and Selenium"""
    
    def __init__(self, username: str = None, password: str = None, **kwargs):
        """
        Initialize Instagram scraper
        
        Args:
            username: Instagram username for login (optional)
            password: Instagram password for login (optional)
        """
        super().__init__(**kwargs)
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Login if credentials provided
        if username and password:
            try:
                self.loader.login(username, password)
                logger.info("Successfully logged into Instagram")
            except Exception as e:
                logger.warning(f"Failed to login to Instagram: {e}")
        
        self.driver = None
        
    def _init_selenium_driver(self):
        """Initialize Selenium WebDriver for web scraping"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                logger.error(f"Failed to initialize Chrome driver: {e}")
                raise
    
    def get_profile(self, username: str) -> Optional[InfluencerProfile]:
        """
        Get Instagram profile information
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            InfluencerProfile object or None if not found
        """
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            # Get profile using instaloader
            profile = self.loader.get_profile(username)
            
            # Get recent posts
            posts = self.get_posts(username, limit=20)
            
            # Calculate engagement metrics
            engagement_rate = self.calculate_engagement_rate(posts, profile.followers)
            
            avg_likes = sum(post.likes_count for post in posts) / len(posts) if posts else 0
            avg_comments = sum(post.comments_count for post in posts) / len(posts) if posts else 0
            
            # Determine category based on bio and posts
            category = self._determine_category(profile.biography, posts)
            
            return InfluencerProfile(
                username=profile.username,
                display_name=profile.full_name or profile.username,
                platform="instagram",
                follower_count=profile.followers,
                following_count=profile.followees,
                post_count=profile.mediacount,
                bio=profile.biography or "",
                profile_image_url=profile.profile_pic_url,
                verified=profile.is_verified,
                engagement_rate=engagement_rate,
                average_likes=avg_likes,
                average_comments=avg_comments,
                category=category,
                location="",  # Instagram API doesn't provide location easily
                external_url=profile.external_url or "",
                posts=[post.__dict__ for post in posts],
                scraped_at=datetime.now()
            )
            
        except instaloader.exceptions.ProfileNotExistsException:
            logger.warning(f"Instagram profile @{username} not found")
            return None
        except Exception as e:
            logger.error(f"Error scraping Instagram profile @{username}: {e}")
            return None
    
    def search_influencers(self, 
                          keyword: str, 
                          min_followers: int = 1000,
                          max_results: int = 100) -> List[InfluencerProfile]:
        """
        Search for Instagram influencers by hashtag or keyword
        
        Args:
            keyword: Hashtag or keyword to search
            min_followers: Minimum follower count
            max_results: Maximum number of results
            
        Returns:
            List of InfluencerProfile objects
        """
        influencers = []
        
        try:
            # Search by hashtag
            if not keyword.startswith('#'):
                keyword = f"#{keyword}"
                
            hashtag = self.loader.get_hashtag_posts(keyword.lstrip('#'))
            
            processed_usernames = set()
            
            for post in hashtag:
                if len(influencers) >= max_results:
                    break
                    
                username = post.owner_username
                
                # Skip if already processed
                if username in processed_usernames:
                    continue
                    
                processed_usernames.add(username)
                
                # Get profile
                profile = self.get_profile(username)
                
                if profile and profile.follower_count >= min_followers:
                    influencers.append(profile)
                    logger.info(f"Found influencer: @{username} ({profile.follower_count} followers)")
                
                # Rate limiting
                self._rate_limit_delay()
                
        except Exception as e:
            logger.error(f"Error searching Instagram influencers for '{keyword}': {e}")
        
        return influencers
    
    def get_posts(self, username: str, limit: int = 50) -> List[PostData]:
        """
        Get recent posts for an Instagram user
        
        Args:
            username: Instagram username
            limit: Maximum number of posts
            
        Returns:
            List of PostData objects
        """
        posts = []
        
        try:
            username = username.lstrip('@')
            profile = self.loader.get_profile(username)
            
            for post in profile.get_posts():
                if len(posts) >= limit:
                    break
                
                # Determine post type
                post_type = "photo"
                if post.is_video:
                    post_type = "video"
                elif post.typename == "GraphSidecar":
                    post_type = "carousel"
                
                # Get media URLs
                media_urls = []
                if post.typename == "GraphSidecar":
                    # Multiple images/videos
                    for node in post.get_sidecar_nodes():
                        if node.is_video:
                            media_urls.append(node.video_url)
                        else:
                            media_urls.append(node.display_url)
                else:
                    # Single image/video
                    if post.is_video:
                        media_urls.append(post.video_url)
                    else:
                        media_urls.append(post.url)
                
                post_data = PostData(
                    post_id=post.shortcode,
                    caption=post.caption or "",
                    likes_count=post.likes,
                    comments_count=post.comments,
                    shares_count=0,  # Instagram doesn't provide share count
                    views_count=post.video_view_count if post.is_video else 0,
                    post_type=post_type,
                    media_urls=media_urls,
                    hashtags=self.extract_hashtags(post.caption or ""),
                    mentions=self.extract_mentions(post.caption or ""),
                    posted_at=post.date
                )
                
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Error getting posts for @{username}: {e}")
        
        return posts
    
    def _determine_category(self, bio: str, posts: List[PostData]) -> str:
        """
        Determine influencer category based on bio and posts
        
        Args:
            bio: Profile biography
            posts: Recent posts
            
        Returns:
            Category string
        """
        # Keywords for different categories
        categories = {
            "fitness": ["fitness", "gym", "workout", "health", "bodybuilding", "yoga", "pilates"],
            "fashion": ["fashion", "style", "outfit", "ootd", "designer", "model", "beauty"],
            "food": ["food", "recipe", "cooking", "chef", "restaurant", "foodie", "culinary"],
            "travel": ["travel", "adventure", "explore", "wanderlust", "vacation", "journey"],
            "tech": ["tech", "technology", "gadget", "startup", "coding", "developer", "ai"],
            "lifestyle": ["lifestyle", "life", "daily", "vlog", "blogger", "influencer"],
            "business": ["entrepreneur", "business", "ceo", "founder", "startup", "marketing"],
            "entertainment": ["music", "artist", "actor", "comedian", "entertainment", "show"],
            "sports": ["sport", "athlete", "football", "basketball", "soccer", "tennis", "golf"],
            "beauty": ["makeup", "skincare", "cosmetics", "beauty", "glam", "tutorial"]
        }
        
        text_to_analyze = (bio or "").lower()
        
        # Add post captions to analysis
        for post in posts[:5]:  # Analyze first 5 posts
            text_to_analyze += " " + (post.caption or "").lower()
        
        # Count category keywords
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "lifestyle"  # Default category
    
    def get_trending_hashtags(self, category: str = None) -> List[str]:
        """
        Get trending hashtags for a category
        
        Args:
            category: Category to get hashtags for
            
        Returns:
            List of trending hashtags
        """
        # This would require web scraping or third-party APIs
        # For now, return some common hashtags by category
        trending_hashtags = {
            "fitness": ["#fitness", "#gym", "#workout", "#health", "#motivation"],
            "fashion": ["#fashion", "#style", "#ootd", "#outfit", "#trendy"],
            "food": ["#food", "#foodie", "#recipe", "#delicious", "#cooking"],
            "travel": ["#travel", "#wanderlust", "#adventure", "#explore", "#vacation"],
            "tech": ["#tech", "#technology", "#innovation", "#startup", "#ai"],
            "lifestyle": ["#lifestyle", "#life", "#daily", "#instagood", "#photooftheday"]
        }
        
        if category and category in trending_hashtags:
            return trending_hashtags[category]
        
        # Return general trending hashtags
        return ["#instagood", "#photooftheday", "#love", "#beautiful", "#happy"]
    
    @property
    def platform_name(self) -> str:
        """Return platform name"""
        return "instagram"
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass