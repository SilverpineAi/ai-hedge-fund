import asyncio
import json
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import time

from ..models.influencer import (
    InfluencerProfile, InfluencerMetrics, InfluencerContact,
    InfluencerCategory, InfluencerTier, InfluencerSearchRequest,
    InfluencerSearchResponse, InfluencerAnalytics
)

class InfluencerDiscoveryService:
    def __init__(self):
        self.cl = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _determine_tier(self, followers_count: int) -> InfluencerTier:
        """Determine influencer tier based on follower count"""
        if followers_count >= 10000000:
            return InfluencerTier.MEGA
        elif followers_count >= 1000000:
            return InfluencerTier.MACRO
        elif followers_count >= 100000:
            return InfluencerTier.MID
        elif followers_count >= 10000:
            return InfluencerTier.MICRO
        else:
            return InfluencerTier.NANO
    
    def _calculate_engagement_rate(self, avg_likes: int, avg_comments: int, followers: int) -> float:
        """Calculate engagement rate"""
        if followers == 0:
            return 0.0
        total_engagement = avg_likes + avg_comments
        return round((total_engagement / followers) * 100, 2)
    
    def _estimate_cost_per_post(self, followers_count: int, engagement_rate: float) -> float:
        """Estimate cost per post based on followers and engagement"""
        base_rate = 0.01  # $0.01 per follower as base
        
        # Adjust based on tier
        if followers_count >= 1000000:
            base_rate = 0.005  # Lower rate for macro/mega influencers
        elif followers_count >= 100000:
            base_rate = 0.008
        elif followers_count >= 10000:
            base_rate = 0.012
        else:
            base_rate = 0.015  # Higher rate for nano influencers
            
        # Engagement rate multiplier
        engagement_multiplier = 1 + (engagement_rate / 100)
        
        estimated_cost = followers_count * base_rate * engagement_multiplier
        return round(max(estimated_cost, 25), 2)  # Minimum $25
    
    def _categorize_influencer(self, bio: str, username: str) -> Optional[InfluencerCategory]:
        """Categorize influencer based on bio and username"""
        bio_lower = (bio or "").lower()
        username_lower = username.lower()
        
        category_keywords = {
            InfluencerCategory.FASHION: ['fashion', 'style', 'outfit', 'ootd', 'designer', 'model', 'wardrobe'],
            InfluencerCategory.BEAUTY: ['beauty', 'makeup', 'skincare', 'cosmetics', 'mua', 'beautyblogger'],
            InfluencerCategory.FITNESS: ['fitness', 'gym', 'workout', 'health', 'fit', 'training', 'yoga'],
            InfluencerCategory.FOOD: ['food', 'recipe', 'chef', 'cooking', 'foodie', 'restaurant', 'cuisine'],
            InfluencerCategory.TRAVEL: ['travel', 'wanderlust', 'adventure', 'explore', 'nomad', 'vacation'],
            InfluencerCategory.TECHNOLOGY: ['tech', 'gadget', 'programming', 'developer', 'software', 'ai'],
            InfluencerCategory.LIFESTYLE: ['lifestyle', 'blogger', 'life', 'daily', 'motivation', 'inspiration'],
            InfluencerCategory.BUSINESS: ['entrepreneur', 'business', 'ceo', 'startup', 'finance', 'marketing'],
            InfluencerCategory.ENTERTAINMENT: ['entertainment', 'actor', 'comedian', 'performer', 'celebrity'],
            InfluencerCategory.GAMING: ['gaming', 'gamer', 'esports', 'streamer', 'twitch', 'youtube'],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in bio_lower or keyword in username_lower for keyword in keywords):
                return category
                
        return InfluencerCategory.LIFESTYLE  # Default category
    
    async def search_influencers_by_hashtag(self, hashtag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for influencers using hashtags"""
        influencers = []
        
        # Simulate Instagram hashtag search (in production, use actual Instagram API)
        # This is a mock implementation for demonstration
        sample_usernames = [
            f"user_{hashtag}_{i}" for i in range(limit)
        ]
        
        for username in sample_usernames:
            # Simulate profile data
            followers = random.randint(1000, 5000000)
            following = random.randint(100, 2000)
            posts = random.randint(50, 3000)
            avg_likes = random.randint(int(followers * 0.01), int(followers * 0.1))
            avg_comments = random.randint(int(avg_likes * 0.02), int(avg_likes * 0.1))
            
            influencer_data = {
                'username': username,
                'full_name': f"Influencer {username.split('_')[-1]}",
                'bio': f"Content creator passionate about {hashtag}. Lifestyle & inspiration 📸✨",
                'followers_count': followers,
                'following_count': following,
                'posts_count': posts,
                'verified': random.choice([True, False]) if followers > 100000 else False,
                'business_account': random.choice([True, False]),
                'avg_likes': avg_likes,
                'avg_comments': avg_comments,
                'profile_pic_url': f"https://via.placeholder.com/150?text={username}"
            }
            influencers.append(influencer_data)
            
        return influencers
    
    async def search_influencers_by_location(self, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for influencers by location"""
        influencers = []
        
        # Mock location-based search
        for i in range(limit):
            followers = random.randint(5000, 1000000)
            following = random.randint(200, 1500)
            posts = random.randint(100, 2000)
            avg_likes = random.randint(int(followers * 0.02), int(followers * 0.08))
            avg_comments = random.randint(int(avg_likes * 0.03), int(avg_likes * 0.08))
            
            username = f"{location.lower().replace(' ', '')}_creator_{i}"
            
            influencer_data = {
                'username': username,
                'full_name': f"{location} Influencer {i}",
                'bio': f"Local influencer from {location} 📍 Sharing life & adventures",
                'followers_count': followers,
                'following_count': following,
                'posts_count': posts,
                'verified': random.choice([True, False]) if followers > 50000 else False,
                'business_account': random.choice([True, False]),
                'avg_likes': avg_likes,
                'avg_comments': avg_comments,
                'location': location,
                'profile_pic_url': f"https://via.placeholder.com/150?text={username}"
            }
            influencers.append(influencer_data)
            
        return influencers
    
    def _create_influencer_profile(self, data: Dict[str, Any]) -> InfluencerProfile:
        """Create InfluencerProfile from raw data"""
        followers = data.get('followers_count', 0)
        avg_likes = data.get('avg_likes', 0)
        avg_comments = data.get('avg_comments', 0)
        
        engagement_rate = self._calculate_engagement_rate(avg_likes, avg_comments, followers)
        tier = self._determine_tier(followers)
        category = self._categorize_influencer(data.get('bio', ''), data.get('username', ''))
        estimated_cost = self._estimate_cost_per_post(followers, engagement_rate)
        
        metrics = InfluencerMetrics(
            followers_count=followers,
            following_count=data.get('following_count', 0),
            posts_count=data.get('posts_count', 0),
            engagement_rate=engagement_rate,
            avg_likes=avg_likes,
            avg_comments=avg_comments,
            verified=data.get('verified', False),
            business_account=data.get('business_account', False)
        )
        
        contact_info = InfluencerContact()
        if data.get('business_account'):
            # Mock contact info for business accounts
            contact_info.email = f"contact@{data.get('username', 'user')}.com"
        
        return InfluencerProfile(
            username=data.get('username', ''),
            full_name=data.get('full_name'),
            bio=data.get('bio'),
            profile_pic_url=data.get('profile_pic_url'),
            category=category,
            tier=tier,
            location=data.get('location'),
            contact_info=contact_info if contact_info.email else None,
            metrics=metrics,
            last_updated=datetime.now(),
            estimated_cost_per_post=estimated_cost,
            content_quality_score=round(random.uniform(6.0, 9.5), 1),
            brand_safety_score=round(random.uniform(7.0, 9.8), 1)
        )
    
    async def search_influencers(self, search_request: InfluencerSearchRequest) -> InfluencerSearchResponse:
        """Main search function for influencers"""
        all_influencers = []
        
        # Search by keywords/hashtags
        if search_request.keywords:
            for keyword in search_request.keywords:
                hashtag_results = await self.search_influencers_by_hashtag(
                    keyword, 
                    limit=min(search_request.limit // len(search_request.keywords), 50)
                )
                all_influencers.extend(hashtag_results)
        
        # Search by location
        if search_request.location:
            location_results = await self.search_influencers_by_location(
                search_request.location, 
                limit=search_request.limit
            )
            all_influencers.extend(location_results)
        
        # If no specific search criteria, generate sample influencers
        if not search_request.keywords and not search_request.location:
            sample_results = await self.search_influencers_by_hashtag("lifestyle", search_request.limit)
            all_influencers.extend(sample_results)
        
        # Convert to InfluencerProfile objects
        profiles = [self._create_influencer_profile(data) for data in all_influencers]
        
        # Apply filters
        filtered_profiles = self._apply_filters(profiles, search_request)
        
        # Sort by engagement rate (descending)
        filtered_profiles.sort(key=lambda x: x.metrics.engagement_rate or 0, reverse=True)
        
        # Limit results
        final_profiles = filtered_profiles[:search_request.limit]
        
        return InfluencerSearchResponse(
            influencers=final_profiles,
            total_found=len(filtered_profiles),
            search_params=search_request,
            export_available=True
        )
    
    def _apply_filters(self, profiles: List[InfluencerProfile], search_request: InfluencerSearchRequest) -> List[InfluencerProfile]:
        """Apply search filters to influencer profiles"""
        filtered = []
        
        for profile in profiles:
            # Follower count filter
            if (search_request.min_followers and 
                profile.metrics.followers_count < search_request.min_followers):
                continue
                
            if (search_request.max_followers and 
                profile.metrics.followers_count > search_request.max_followers):
                continue
            
            # Engagement rate filter
            if (search_request.min_engagement_rate and 
                (profile.metrics.engagement_rate or 0) < search_request.min_engagement_rate):
                continue
                
            if (search_request.max_engagement_rate and 
                (profile.metrics.engagement_rate or 0) > search_request.max_engagement_rate):
                continue
            
            # Verified filter
            if search_request.verified_only and not profile.metrics.verified:
                continue
                
            # Business account filter
            if search_request.business_accounts_only and not profile.metrics.business_account:
                continue
            
            # Category filter
            if (search_request.categories and 
                profile.category not in search_request.categories):
                continue
                
            filtered.append(profile)
        
        return filtered
    
    async def get_influencer_analytics(self, username: str) -> InfluencerAnalytics:
        """Get detailed analytics for a specific influencer"""
        # Mock analytics data
        recent_engagement = [random.uniform(2.0, 8.0) for _ in range(10)]
        
        return InfluencerAnalytics(
            username=username,
            recent_posts_engagement=recent_engagement,
            best_posting_times=["9:00 AM", "12:00 PM", "6:00 PM", "8:00 PM"],
            top_hashtags=["#lifestyle", "#ootd", "#instagood", "#photooftheday", "#love"],
            audience_demographics={
                "gender": {"female": 65, "male": 35},
                "age_groups": {"18-24": 30, "25-34": 40, "35-44": 20, "45+": 10},
                "top_countries": ["United States", "United Kingdom", "Canada", "Australia"]
            },
            brand_mentions=["@nike", "@adidas", "@zara", "@hm", "@starbucks"],
            collaboration_history=["Fashion Brand A", "Beauty Brand B", "Lifestyle Brand C"]
        )
    
    def export_to_csv(self, influencers: List[InfluencerProfile]) -> str:
        """Export influencer data to CSV format"""
        data = []
        for influencer in influencers:
            data.append({
                'Username': influencer.username,
                'Full Name': influencer.full_name,
                'Followers': influencer.metrics.followers_count,
                'Engagement Rate (%)': influencer.metrics.engagement_rate,
                'Category': influencer.category.value if influencer.category else None,
                'Tier': influencer.tier.value if influencer.tier else None,
                'Verified': influencer.metrics.verified,
                'Business Account': influencer.metrics.business_account,
                'Estimated Cost per Post ($)': influencer.estimated_cost_per_post,
                'Content Quality Score': influencer.content_quality_score,
                'Brand Safety Score': influencer.brand_safety_score,
                'Location': influencer.location,
                'Email': influencer.contact_info.email if influencer.contact_info else None,
                'Bio': influencer.bio
            })
        
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False)
        return csv_content