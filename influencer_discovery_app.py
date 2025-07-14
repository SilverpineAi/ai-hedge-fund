import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from app.backend.models.influencer import (
    InfluencerSearchRequest, InfluencerCategory, InfluencerProfile
)
from app.backend.services.influencer_discovery import InfluencerDiscoveryService

# Page configuration
st.set_page_config(
    page_title="Instagram Influencer Discovery Tool",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .influencer-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        transition: transform 0.2s;
    }
    
    .influencer-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .tier-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .tier-nano { background-color: #e3f2fd; color: #1976d2; }
    .tier-micro { background-color: #f3e5f5; color: #7b1fa2; }
    .tier-mid { background-color: #fff3e0; color: #f57c00; }
    .tier-macro { background-color: #e8f5e8; color: #388e3c; }
    .tier-mega { background-color: #fce4ec; color: #c2185b; }
    
    .category-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background-color: #f5f5f5;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_influencers' not in st.session_state:
    st.session_state.selected_influencers = []

def format_number(num):
    """Format large numbers with K, M notation"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def get_tier_badge_html(tier):
    """Generate HTML for tier badge"""
    if not tier:
        return ""
    tier_class = f"tier-{tier.lower()}"
    return f'<span class="tier-badge {tier_class}">{tier}</span>'

def get_engagement_color(rate):
    """Get color based on engagement rate"""
    if rate >= 6:
        return "#4caf50"  # Green
    elif rate >= 3:
        return "#ff9800"  # Orange
    else:
        return "#f44336"  # Red

def display_influencer_card(influencer: InfluencerProfile, index: int):
    """Display an influencer card with all information"""
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        
        with col1:
            # Profile picture placeholder
            st.image(
                influencer.profile_pic_url or "https://via.placeholder.com/100", 
                width=80
            )
            
        with col2:
            # Basic info
            st.markdown(f"**@{influencer.username}**")
            if influencer.full_name:
                st.markdown(f"*{influencer.full_name}*")
            
            # Tier and verification badges
            tier_html = get_tier_badge_html(influencer.tier.value if influencer.tier else "")
            verified_html = "✅ Verified" if influencer.metrics.verified else ""
            business_html = "🏢 Business" if influencer.metrics.business_account else ""
            
            st.markdown(f"{tier_html} {verified_html} {business_html}", unsafe_allow_html=True)
            
            # Category
            if influencer.category:
                st.markdown(f'<span class="category-tag">{influencer.category.value.title()}</span>', 
                           unsafe_allow_html=True)
        
        with col3:
            # Metrics
            st.metric("Followers", format_number(influencer.metrics.followers_count))
            engagement_rate = influencer.metrics.engagement_rate or 0
            st.metric(
                "Engagement Rate", 
                f"{engagement_rate:.1f}%",
                delta=None,
                delta_color="normal"
            )
            
        with col4:
            # Actions and cost
            if influencer.estimated_cost_per_post:
                st.metric("Est. Cost/Post", f"${influencer.estimated_cost_per_post:,.0f}")
            
            # Select checkbox
            selected = st.checkbox(
                "Select", 
                key=f"select_{index}",
                value=influencer.username in [inf.username for inf in st.session_state.selected_influencers]
            )
            
            if selected and influencer not in st.session_state.selected_influencers:
                st.session_state.selected_influencers.append(influencer)
            elif not selected and influencer in st.session_state.selected_influencers:
                st.session_state.selected_influencers = [
                    inf for inf in st.session_state.selected_influencers 
                    if inf.username != influencer.username
                ]

def create_analytics_dashboard(influencers: List[InfluencerProfile]):
    """Create analytics dashboard for search results"""
    if not influencers:
        return
    
    st.subheader("📊 Search Results Analytics")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_influencers = len(influencers)
    avg_followers = sum(inf.metrics.followers_count for inf in influencers) / total_influencers
    avg_engagement = sum(inf.metrics.engagement_rate or 0 for inf in influencers) / total_influencers
    verified_count = sum(1 for inf in influencers if inf.metrics.verified)
    
    with col1:
        st.metric("Total Found", total_influencers)
    with col2:
        st.metric("Avg Followers", format_number(int(avg_followers)))
    with col3:
        st.metric("Avg Engagement", f"{avg_engagement:.1f}%")
    with col4:
        st.metric("Verified Accounts", verified_count)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Tier distribution
        tier_data = {}
        for inf in influencers:
            tier = inf.tier.value if inf.tier else "unknown"
            tier_data[tier] = tier_data.get(tier, 0) + 1
        
        if tier_data:
            fig_tier = px.pie(
                values=list(tier_data.values()),
                names=list(tier_data.keys()),
                title="Distribution by Tier"
            )
            st.plotly_chart(fig_tier, use_container_width=True)
    
    with col2:
        # Category distribution
        category_data = {}
        for inf in influencers:
            category = inf.category.value if inf.category else "unknown"
            category_data[category] = category_data.get(category, 0) + 1
        
        if category_data:
            fig_category = px.bar(
                x=list(category_data.keys()),
                y=list(category_data.values()),
                title="Distribution by Category"
            )
            st.plotly_chart(fig_category, use_container_width=True)
    
    # Engagement vs Followers scatter plot
    followers_data = [inf.metrics.followers_count for inf in influencers]
    engagement_data = [inf.metrics.engagement_rate or 0 for inf in influencers]
    usernames = [inf.username for inf in influencers]
    
    fig_scatter = px.scatter(
        x=followers_data,
        y=engagement_data,
        hover_name=usernames,
        title="Engagement Rate vs Followers",
        labels={"x": "Followers", "y": "Engagement Rate (%)"},
        log_x=True
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

async def perform_search(search_params):
    """Perform influencer search"""
    service = InfluencerDiscoveryService()
    
    # Create search request
    search_request = InfluencerSearchRequest(
        keywords=search_params.get('keywords', []),
        categories=search_params.get('categories', []),
        min_followers=search_params.get('min_followers'),
        max_followers=search_params.get('max_followers'),
        min_engagement_rate=search_params.get('min_engagement_rate'),
        max_engagement_rate=search_params.get('max_engagement_rate'),
        location=search_params.get('location'),
        verified_only=search_params.get('verified_only', False),
        business_accounts_only=search_params.get('business_accounts_only', False),
        limit=search_params.get('limit', 20)
    )
    
    # Perform search
    return await service.search_influencers(search_request)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📱 Instagram Influencer Discovery Tool</h1>
        <p>Find the perfect influencers for your ecommerce brand</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for search filters
    st.sidebar.markdown("## 🔍 Search Filters")
    
    # Keywords
    keywords_input = st.sidebar.text_input(
        "Keywords/Hashtags", 
        placeholder="fashion, beauty, lifestyle",
        help="Enter keywords separated by commas"
    )
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()] if keywords_input else []
    
    # Categories
    categories = st.sidebar.multiselect(
        "Categories",
        options=[cat.value for cat in InfluencerCategory],
        help="Select one or more categories"
    )
    category_enums = [InfluencerCategory(cat) for cat in categories]
    
    # Follower range
    st.sidebar.markdown("### 👥 Follower Range")
    min_followers = st.sidebar.number_input("Minimum Followers", min_value=0, value=1000, step=1000)
    max_followers = st.sidebar.number_input("Maximum Followers", min_value=1000, value=10000000, step=100000)
    
    # Engagement rate
    st.sidebar.markdown("### 💬 Engagement Rate")
    min_engagement = st.sidebar.slider("Minimum Engagement Rate (%)", 0.0, 20.0, 1.0, 0.1)
    max_engagement = st.sidebar.slider("Maximum Engagement Rate (%)", 0.0, 20.0, 20.0, 0.1)
    
    # Location
    location = st.sidebar.text_input("Location", placeholder="New York, Los Angeles")
    
    # Additional filters
    st.sidebar.markdown("### ⚙️ Additional Filters")
    verified_only = st.sidebar.checkbox("Verified accounts only")
    business_only = st.sidebar.checkbox("Business accounts only")
    
    # Result limit
    limit = st.sidebar.slider("Number of results", 10, 100, 20, 10)
    
    # Search button
    if st.sidebar.button("🚀 Search Influencers", type="primary"):
        search_params = {
            'keywords': keywords,
            'categories': category_enums,
            'min_followers': min_followers,
            'max_followers': max_followers,
            'min_engagement_rate': min_engagement,
            'max_engagement_rate': max_engagement,
            'location': location if location else None,
            'verified_only': verified_only,
            'business_accounts_only': business_only,
            'limit': limit
        }
        
        with st.spinner("Searching for influencers..."):
            # Run async search
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                st.session_state.search_results = loop.run_until_complete(perform_search(search_params))
            finally:
                loop.close()
    
    # Quick search buttons
    st.sidebar.markdown("### ⚡ Quick Searches")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔥 Trending"):
            search_params = {
                'keywords': ['trending', 'viral'],
                'min_followers': 10000,
                'max_followers': 5000000,
                'min_engagement_rate': 3.0,
                'limit': 20
            }
            with st.spinner("Finding trending influencers..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    st.session_state.search_results = loop.run_until_complete(perform_search(search_params))
                finally:
                    loop.close()
    
    with col2:
        if st.button("💎 Premium"):
            search_params = {
                'min_followers': 100000,
                'verified_only': True,
                'business_accounts_only': True,
                'min_engagement_rate': 4.0,
                'limit': 20
            }
            with st.spinner("Finding premium influencers..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    st.session_state.search_results = loop.run_until_complete(perform_search(search_params))
                finally:
                    loop.close()
    
    # Main content area
    if st.session_state.search_results:
        results = st.session_state.search_results
        
        # Analytics dashboard
        create_analytics_dashboard(results.influencers)
        
        # Action buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"📋 Search Results ({results.total_found} found)")
        
        with col2:
            if st.session_state.selected_influencers:
                if st.button("📊 Analyze Selected"):
                    st.session_state.show_analysis = True
        
        with col3:
            if st.session_state.selected_influencers:
                # Export functionality
                service = InfluencerDiscoveryService()
                csv_data = service.export_to_csv(st.session_state.selected_influencers)
                st.download_button(
                    "📥 Export CSV",
                    csv_data,
                    f"influencers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
        
        # Display results
        for i, influencer in enumerate(results.influencers):
            with st.container():
                st.markdown('<div class="influencer-card">', unsafe_allow_html=True)
                display_influencer_card(influencer, i)
                
                # Expandable details
                with st.expander("View Details"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Profile Information**")
                        st.write(f"Bio: {influencer.bio or 'Not available'}")
                        st.write(f"Location: {influencer.location or 'Not specified'}")
                        st.write(f"Posts: {format_number(influencer.metrics.posts_count)}")
                        st.write(f"Following: {format_number(influencer.metrics.following_count)}")
                    
                    with col2:
                        st.markdown("**Engagement Metrics**")
                        st.write(f"Avg Likes: {format_number(influencer.metrics.avg_likes or 0)}")
                        st.write(f"Avg Comments: {format_number(influencer.metrics.avg_comments or 0)}")
                        st.write(f"Engagement Rate: {influencer.metrics.engagement_rate:.1f}%")
                    
                    with col3:
                        st.markdown("**Quality Scores**")
                        st.write(f"Content Quality: {influencer.content_quality_score}/10")
                        st.write(f"Brand Safety: {influencer.brand_safety_score}/10")
                        st.write(f"Estimated Cost: ${influencer.estimated_cost_per_post:,.0f}")
                        
                        # Contact info
                        if influencer.contact_info and influencer.contact_info.email:
                            st.write(f"Email: {influencer.contact_info.email}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Welcome to the Instagram Influencer Discovery Tool!
        
        This powerful tool helps ecommerce brands find the perfect influencers for their marketing campaigns.
        
        ### 🌟 Features:
        - **Smart Search**: Find influencers by keywords, categories, location, and more
        - **Advanced Filters**: Filter by follower count, engagement rate, verification status
        - **Analytics Dashboard**: Visualize search results with interactive charts
        - **Quality Scoring**: Content quality and brand safety scores for each influencer
        - **Cost Estimation**: Estimated cost per post based on followers and engagement
        - **Export Functionality**: Download influencer data as CSV for further analysis
        
        ### 🎯 How to Use:
        1. Use the sidebar to set your search criteria
        2. Click "Search Influencers" to find matching profiles
        3. Review the results and select influencers of interest
        4. Analyze selected influencers or export data
        
        **Get started by setting your search filters in the sidebar!**
        """)
        
        # Sample statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Influencers", "125K+", "Growing daily")
        with col2:
            st.metric("Categories", "20+", "All major niches")
        with col3:
            st.metric("Verified Accounts", "15K+", "Premium quality")
        with col4:
            st.metric("Success Rate", "94%", "Brand satisfaction")

if __name__ == "__main__":
    main()