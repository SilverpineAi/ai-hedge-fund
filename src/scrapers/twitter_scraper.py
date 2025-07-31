"""
Twitter/X Scraper

Scrapes Twitter/X profiles and tweets to discover influencers.
Uses tweepy API and web scraping techniques.
"""

import tweepy
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
import requests
import json

from .base_scraper import BaseScraper, InfluencerProfile, PostData

logger = logging.getLogger(__name__)

class TwitterScraper(BaseScraper):
    """Twitter/X scraper using tweepy and Selenium"""
    
    def __init__(self, bearer_token: str = None, **kwargs):
        """
        Initialize Twitter scraper
        
        Args:
            bearer_token: Twitter API v2 Bearer Token
        """
        super().__init__(**kwargs)
        
        self.api = None
        if bearer_token:
            try:
                self.api = tweepy.Client(bearer_token=bearer_token)
                logger.info("Successfully initialized Twitter API client")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter API: {e}")
        
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
        Get Twitter profile information
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            InfluencerProfile object or None if not found
        """
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            if self.api:
                # Use Twitter API v2
                user = self.api.get_user(
                    username=username,
                    user_fields=['public_metrics', 'description', 'profile_image_url', 
                               'verified', 'location', 'url', 'created_at']
                )
                
                if not user.data:
                    logger.warning(f"Twitter user @{username} not found")
                    return None
                
                user_data = user.data
                metrics = user_data.public_metrics
                
                # Get recent tweets
                tweets = self.get_posts(username, limit=20)
                
                # Calculate engagement metrics
                engagement_rate = self.calculate_engagement_rate(tweets, metrics['followers_count'])
                
                avg_likes = sum(tweet.likes_count for tweet in tweets) / len(tweets) if tweets else 0
                avg_comments = sum(tweet.comments_count for tweet in tweets) / len(tweets) if tweets else 0
                
                # Determine category based on bio and tweets
                category = self._determine_category(user_data.description, tweets)
                
                return InfluencerProfile(
                    username=user_data.username,
                    display_name=user_data.name,
                    platform="twitter",
                    follower_count=metrics['followers_count'],
                    following_count=metrics['following_count'],
                    post_count=metrics['tweet_count'],
                    bio=user_data.description or "",
                    profile_image_url=user_data.profile_image_url or "",
                    verified=user_data.verified or False,
                    engagement_rate=engagement_rate,
                    average_likes=avg_likes,
                    average_comments=avg_comments,
                    category=category,
                    location=user_data.location or "",
                    external_url=user_data.url or "",
                    posts=[tweet.__dict__ for tweet in tweets],
                    scraped_at=datetime.now()
                )
            else:
                # Fallback to web scraping
                return self._scrape_profile_web(username)
                
        except Exception as e:
            logger.error(f"Error scraping Twitter profile @{username}: {e}")
            return None
    
    def _scrape_profile_web(self, username: str) -> Optional[InfluencerProfile]:
        """
        Scrape Twitter profile using Selenium (fallback method)
        
        Args:
            username: Twitter username
            
        Returns:
            InfluencerProfile object or None
        """
        try:
            self._init_selenium_driver()
            
            # Navigate to Twitter profile
            url = f"https://twitter.com/{username}"
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="UserName"]'))
            )
            
            # Extract profile information
            display_name = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserName"] span').text
            
            # Get follower/following counts
            stats_elements = self.driver.find_elements(By.CSS_SELECTOR, '[href*="/followers"], [href*="/following"]')
            follower_count = 0
            following_count = 0
            
            for element in stats_elements:
                text = element.text.lower()
                if 'followers' in text:
                    follower_count = self._extract_number_from_text(text)
                elif 'following' in text:
                    following_count = self._extract_number_from_text(text)
            
            # Get bio
            bio = ""
            try:
                bio_element = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserDescription"]')
                bio = bio_element.text
            except:
                pass
            
            # Get profile image
            profile_image_url = ""
            try:
                img_element = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserAvatar-Container-"] img')
                profile_image_url = img_element.get_attribute('src')
            except:
                pass
            
            # Check if verified
            verified = len(self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="icon-verified"]')) > 0
            
            # Get recent tweets
            tweets = self.get_posts(username, limit=20)
            
            # Calculate engagement metrics
            engagement_rate = self.calculate_engagement_rate(tweets, follower_count)
            
            avg_likes = sum(tweet.likes_count for tweet in tweets) / len(tweets) if tweets else 0
            avg_comments = sum(tweet.comments_count for tweet in tweets) / len(tweets) if tweets else 0
            
            # Determine category
            category = self._determine_category(bio, tweets)
            
            return InfluencerProfile(
                username=username,
                display_name=display_name,
                platform="twitter",
                follower_count=follower_count,
                following_count=following_count,
                post_count=len(tweets),  # Approximate
                bio=bio,
                profile_image_url=profile_image_url,
                verified=verified,
                engagement_rate=engagement_rate,
                average_likes=avg_likes,
                average_comments=avg_comments,
                category=category,
                location="",
                external_url="",
                posts=[tweet.__dict__ for tweet in tweets],
                scraped_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error web scraping Twitter profile @{username}: {e}")
            return None
    
    def search_influencers(self, 
                          keyword: str, 
                          min_followers: int = 1000,
                          max_results: int = 100) -> List[InfluencerProfile]:
        """
        Search for Twitter influencers by keyword or hashtag
        
        Args:
            keyword: Keyword or hashtag to search
            min_followers: Minimum follower count
            max_results: Maximum number of results
            
        Returns:
            List of InfluencerProfile objects
        """
        influencers = []
        
        try:
            if self.api:
                # Use Twitter API v2 search
                query = keyword
                if not keyword.startswith('#'):
                    query = f"#{keyword}"
                
                tweets = self.api.search_recent_tweets(
                    query=query,
                    max_results=100,
                    tweet_fields=['author_id', 'public_metrics', 'created_at']
                )
                
                if not tweets.data:
                    return influencers
                
                # Get unique author IDs
                author_ids = list(set(tweet.author_id for tweet in tweets.data))
                
                # Get user information for authors
                users = self.api.get_users(
                    ids=author_ids,
                    user_fields=['public_metrics', 'description', 'profile_image_url', 
                               'verified', 'location', 'url']
                )
                
                for user in users.data:
                    if len(influencers) >= max_results:
                        break
                    
                    metrics = user.public_metrics
                    if metrics['followers_count'] >= min_followers:
                        profile = self.get_profile(user.username)
                        if profile:
                            influencers.append(profile)
                            logger.info(f"Found influencer: @{user.username} ({metrics['followers_count']} followers)")
                    
                    # Rate limiting
                    self._rate_limit_delay()
            
        except Exception as e:
            logger.error(f"Error searching Twitter influencers for '{keyword}': {e}")
        
        return influencers
    
    def get_posts(self, username: str, limit: int = 50) -> List[PostData]:
        """
        Get recent tweets for a Twitter user
        
        Args:
            username: Twitter username
            limit: Maximum number of tweets
            
        Returns:
            List of PostData objects
        """
        posts = []
        
        try:
            username = username.lstrip('@')
            
            if self.api:
                # Get user ID first
                user = self.api.get_user(username=username)
                if not user.data:
                    return posts
                
                # Get user's tweets
                tweets = self.api.get_users_tweets(
                    id=user.data.id,
                    max_results=min(limit, 100),
                    tweet_fields=['public_metrics', 'created_at', 'attachments'],
                    expansions=['attachments.media_keys'],
                    media_fields=['url', 'type']
                )
                
                if not tweets.data:
                    return posts
                
                for tweet in tweets.data:
                    # Get media URLs
                    media_urls = []
                    if hasattr(tweets, 'includes') and 'media' in tweets.includes:
                        if tweet.attachments and 'media_keys' in tweet.attachments:
                            for media_key in tweet.attachments['media_keys']:
                                for media in tweets.includes['media']:
                                    if media.media_key == media_key:
                                        if hasattr(media, 'url'):
                                            media_urls.append(media.url)
                    
                    # Determine post type
                    post_type = "text"
                    if media_urls:
                        post_type = "media"
                    
                    metrics = tweet.public_metrics
                    
                    post_data = PostData(
                        post_id=tweet.id,
                        caption=tweet.text,
                        likes_count=metrics['like_count'],
                        comments_count=metrics['reply_count'],
                        shares_count=metrics['retweet_count'],
                        views_count=metrics.get('impression_count', 0),
                        post_type=post_type,
                        media_urls=media_urls,
                        hashtags=self.extract_hashtags(tweet.text),
                        mentions=self.extract_mentions(tweet.text),
                        posted_at=tweet.created_at
                    )
                    
                    posts.append(post_data)
                    
        except Exception as e:
            logger.error(f"Error getting tweets for @{username}: {e}")
        
        return posts
    
    def _determine_category(self, bio: str, posts: List[PostData]) -> str:
        """
        Determine influencer category based on bio and tweets
        
        Args:
            bio: Profile bio
            posts: Recent posts
            
        Returns:
            Category string
        """
        # Keywords for different categories
        categories = {
            "tech": ["tech", "technology", "startup", "ai", "ml", "coding", "developer", "software"],
            "crypto": ["crypto", "bitcoin", "blockchain", "defi", "nft", "ethereum", "web3"],
            "finance": ["finance", "trading", "stocks", "investment", "market", "economy"],
            "news": ["news", "journalist", "reporter", "breaking", "politics", "media"],
            "sports": ["sports", "athlete", "football", "basketball", "soccer", "tennis", "nfl"],
            "entertainment": ["music", "artist", "actor", "comedian", "entertainment", "celebrity"],
            "business": ["entrepreneur", "ceo", "founder", "business", "startup", "marketing"],
            "lifestyle": ["lifestyle", "life", "motivation", "inspiration", "personal", "thoughts"],
            "education": ["education", "teacher", "learning", "knowledge", "academic", "research"],
            "health": ["health", "fitness", "wellness", "medical", "doctor", "nutrition"]
        }
        
        text_to_analyze = (bio or "").lower()
        
        # Add tweet content to analysis
        for post in posts[:10]:  # Analyze first 10 tweets
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
    
    def _extract_number_from_text(self, text: str) -> int:
        """Extract number from text like '1.2K followers' or '500 following'"""
        import re
        
        # Find number with possible K, M suffix
        match = re.search(r'([\d.]+)([KMB]?)', text.upper())
        if match:
            number_str, suffix = match.groups()
            number = float(number_str)
            
            if suffix == 'K':
                number *= 1000
            elif suffix == 'M':
                number *= 1000000
            elif suffix == 'B':
                number *= 1000000000
                
            return int(number)
        
        return 0
    
    def get_trending_topics(self) -> List[str]:
        """
        Get trending topics/hashtags
        
        Returns:
            List of trending topics
        """
        try:
            if self.api:
                # Get trending topics for worldwide
                trends = self.api.get_place_trends(id=1)  # 1 = worldwide
                return [trend['name'] for trend in trends[0]['trends'][:10]]
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
        
        # Fallback trending topics
        return ["#AI", "#Tech", "#Crypto", "#NFT", "#Web3", "#Startup", "#Innovation", "#Business"]
    
    @property
    def platform_name(self) -> str:
        """Return platform name"""
        return "twitter"
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass