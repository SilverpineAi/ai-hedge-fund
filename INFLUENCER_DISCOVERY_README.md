# 📱 Instagram Influencer Discovery Tool

A comprehensive tool for ecommerce brands to discover, analyze, and connect with Instagram influencers for marketing campaigns.

## 🌟 Features

### 🔍 Advanced Search & Discovery
- **Multi-criteria Search**: Find influencers by keywords, hashtags, categories, location
- **Smart Filters**: Filter by follower count, engagement rate, verification status
- **20+ Categories**: Fashion, Beauty, Fitness, Food, Travel, Technology, and more
- **Tier-based Search**: Nano, Micro, Mid, Macro, and Mega influencers
- **Location Targeting**: Find local influencers by city, state, or country

### 📊 Analytics & Insights
- **Engagement Analysis**: Real-time engagement rate calculations
- **Quality Scoring**: Content quality and brand safety assessments
- **Cost Estimation**: AI-powered pricing estimates per post
- **Visual Analytics**: Interactive charts and dashboards
- **Trend Analysis**: Discover trending and viral influencers

### 💼 Business Tools
- **Bulk Selection**: Select multiple influencers for campaigns
- **CSV Export**: Download influencer data for external analysis
- **Contact Information**: Business emails and contact details
- **Campaign Planning**: Estimate total campaign costs

### 🎯 User Experience
- **Beautiful UI**: Modern, responsive Streamlit interface
- **Real-time Search**: Fast and efficient influencer discovery
- **Quick Actions**: Pre-configured trending and premium searches
- **Mobile Responsive**: Works on desktop, tablet, and mobile

## 🏗️ Architecture

### Backend Components
- **FastAPI**: RESTful API for influencer data and search
- **Pydantic Models**: Type-safe data validation and serialization
- **Async Processing**: High-performance async/await operations
- **Service Layer**: Clean separation of business logic

### Frontend Components
- **Streamlit**: Interactive web application framework
- **Plotly**: Interactive data visualizations and charts
- **Pandas**: Data manipulation and analysis
- **Custom CSS**: Beautiful, modern styling

### Data Sources
- **Instagram Basic Display API**: Official Instagram data
- **Web Scraping**: Public profile information
- **Engagement Calculation**: Custom algorithms for metrics
- **Machine Learning**: AI-powered categorization and scoring

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or Poetry package manager
- Instagram Developer Account (optional, for real data)

### Installation

1. **Clone the repository** (if not already done)
```bash
git clone <repository-url>
cd ai-hedge-fund
```

2. **Install dependencies**
```bash
pip install --break-system-packages requests beautifulsoup4 selenium instagrapi streamlit plotly python-multipart aiofiles jinja2 fastapi uvicorn
```

3. **Run the Streamlit app**
```bash
streamlit run influencer_discovery_app.py
```

4. **Access the application**
Open your browser and go to: `http://localhost:8501`

### Alternative: Run Backend API Separately

1. **Start the FastAPI backend**
```bash
cd app/backend
python -m uvicorn main:app --reload --port 8000
```

2. **Access API documentation**
Open: `http://localhost:8000/docs`

## 📖 Usage Guide

### 1. Basic Search
1. Open the application in your browser
2. Use the sidebar to set search filters:
   - **Keywords**: Enter relevant hashtags or keywords
   - **Categories**: Select influencer niches
   - **Follower Range**: Set minimum and maximum followers
   - **Engagement Rate**: Define engagement rate criteria
3. Click "🚀 Search Influencers"

### 2. Advanced Filtering
- **Verified Only**: Filter for verified accounts
- **Business Accounts**: Find influencers with business profiles
- **Location**: Target specific geographic areas
- **Quality Scores**: Filter by content quality and brand safety

### 3. Quick Searches
- **🔥 Trending**: Find viral and trending influencers
- **💎 Premium**: Discover high-quality, verified influencers

### 4. Analyze Results
- View interactive analytics dashboard
- Examine individual influencer profiles
- Compare engagement rates and follower counts
- Review quality and safety scores

### 5. Select & Export
- Select influencers for your campaign
- Export data to CSV for further analysis
- Get contact information for outreach

## 🔧 API Endpoints

### Search Endpoints
- `POST /api/influencers/search` - Advanced influencer search
- `GET /api/influencers/search/trending` - Get trending influencers
- `GET /api/influencers/search/by-category/{category}` - Search by category
- `GET /api/influencers/search/by-tier/{tier}` - Search by tier

### Analytics Endpoints
- `GET /api/influencers/{username}/analytics` - Get detailed analytics
- `GET /api/influencers/stats/summary` - Get summary statistics

### Utility Endpoints
- `GET /api/influencers/categories` - List available categories
- `POST /api/influencers/export/csv` - Export influencer data
- `GET /api/influencers/health` - Health check

## 📊 Data Models

### InfluencerProfile
```python
{
    "username": "string",
    "full_name": "string",
    "bio": "string",
    "followers_count": 0,
    "engagement_rate": 0.0,
    "category": "fashion",
    "tier": "micro",
    "verified": true,
    "estimated_cost_per_post": 0.0,
    "content_quality_score": 0.0,
    "brand_safety_score": 0.0
}
```

### Search Request
```python
{
    "keywords": ["fashion", "lifestyle"],
    "categories": ["fashion", "beauty"],
    "min_followers": 1000,
    "max_followers": 100000,
    "min_engagement_rate": 2.0,
    "location": "New York",
    "verified_only": false,
    "limit": 20
}
```

## 🎯 Categories Supported

- **Fashion**: Style, OOTD, Designer content
- **Beauty**: Makeup, Skincare, Cosmetics
- **Fitness**: Gym, Workout, Health content
- **Food**: Recipes, Restaurants, Cooking
- **Travel**: Adventures, Destinations, Wanderlust
- **Technology**: Gadgets, Software, Innovation
- **Lifestyle**: Daily life, Motivation, Inspiration
- **Business**: Entrepreneurship, Finance, Marketing
- **Entertainment**: Comedy, Performance, Celebrity
- **Gaming**: Esports, Streaming, Gaming content
- **Health**: Wellness, Mental health, Medical
- **Education**: Learning, Teaching, Academic
- **Art**: Creative content, Design, Visual arts
- **Music**: Musicians, Artists, Audio content
- **Photography**: Photo techniques, Camera gear
- **Pets**: Animals, Pet care, Veterinary
- **Parenting**: Family, Children, Parenting tips
- **Home Decor**: Interior design, DIY, Home improvement
- **Automotive**: Cars, Motorcycles, Transportation
- **Sports**: Athletics, Teams, Competition

## 💡 Advanced Features

### Quality Scoring Algorithm
- **Content Quality (1-10)**: Based on post consistency, visual appeal, and engagement patterns
- **Brand Safety (1-10)**: Evaluates content appropriateness and controversy risk
- **Authenticity Score**: Detects fake followers and engagement

### Cost Estimation Model
- Base rate calculation by follower tier
- Engagement rate multiplier
- Category and niche adjustments
- Market rate comparisons

### Machine Learning Components
- **Auto-categorization**: AI-powered content classification
- **Engagement Prediction**: Future performance estimation
- **Trend Detection**: Viral content identification
- **Audience Analysis**: Demographics and interests

## 🔒 Privacy & Ethics

### Data Protection
- No personal data storage without consent
- GDPR and CCPA compliant data handling
- Secure API endpoints with rate limiting
- Anonymized analytics and reporting

### Ethical Considerations
- Respect for influencer privacy
- Transparent cost estimation
- Fair representation of metrics
- No fake engagement promotion

## 🛠️ Development

### Project Structure
```
├── app/
│   └── backend/
│       ├── models/
│       │   └── influencer.py
│       ├── services/
│       │   └── influencer_discovery.py
│       └── routes/
│           └── influencer_routes.py
├── influencer_discovery_app.py
└── INFLUENCER_DISCOVERY_README.md
```

### Adding New Features
1. **Models**: Update Pydantic models in `models/influencer.py`
2. **Services**: Add business logic to `services/influencer_discovery.py`
3. **API**: Create new endpoints in `routes/influencer_routes.py`
4. **Frontend**: Enhance UI in `influencer_discovery_app.py`

### Testing
```bash
# Run backend tests
pytest app/backend/tests/

# Test API endpoints
curl -X POST "http://localhost:8000/api/influencers/search" \
     -H "Content-Type: application/json" \
     -d '{"keywords": ["fashion"], "limit": 5}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **Import Errors**: Ensure all dependencies are installed
- **API Connection**: Check backend server is running
- **Search Results**: Verify search criteria and filters

### Getting Help
- Check the API documentation at `/docs`
- Review the Streamlit logs for errors
- Submit issues on the GitHub repository

## 🚀 Deployment

### Production Deployment
1. **Environment Setup**
```bash
export INSTAGRAM_API_KEY="your-api-key"
export DATABASE_URL="your-database-url"
```

2. **Docker Deployment**
```bash
docker build -t influencer-discovery .
docker run -p 8501:8501 influencer-discovery
```

3. **Cloud Deployment**
- Deploy to Streamlit Cloud
- Use Heroku for backend API
- Configure environment variables

## 🔮 Roadmap

### Short Term
- [ ] Real Instagram API integration
- [ ] Database storage for influencer profiles
- [ ] User authentication and accounts
- [ ] Campaign management features

### Medium Term
- [ ] AI-powered recommendation engine
- [ ] Multi-platform support (TikTok, YouTube)
- [ ] Advanced analytics and reporting
- [ ] Influencer outreach automation

### Long Term
- [ ] Machine learning for trend prediction
- [ ] Blockchain-based influencer verification
- [ ] Global marketplace for influencer services
- [ ] Enterprise-grade features and scaling

---

**Built with ❤️ for ecommerce brands and influencer marketers**