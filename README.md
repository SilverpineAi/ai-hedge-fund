# Influencer Discovery App

An AI-powered influencer discovery platform that scrapes social media sites to find the perfect influencers for online brands. This application uses advanced AI agents to analyze social media profiles, engagement rates, audience demographics, and content quality to match brands with relevant influencers.

## 🚀 Features

- **Multi-Platform Scraping**: Scrapes Instagram, Twitter/X, TikTok, and YouTube
- **AI-Powered Analysis**: Uses multiple AI agents to analyze influencer profiles and content
- **Smart Matching**: Matches brands with influencers based on audience, engagement, and niche
- **Real-time Analytics**: Provides comprehensive analytics and metrics
- **Modern Web Interface**: Beautiful React-based dashboard
- **Automated Discovery**: Scheduled scraping and discovery processes
- **Engagement Analysis**: Deep analysis of likes, comments, shares, and audience interaction
- **Content Quality Assessment**: AI evaluation of content quality and brand alignment

## 🤖 AI Agents

The system employs several specialized AI agents:

1. **Profile Analyzer Agent** - Analyzes influencer profiles and bio information
2. **Content Quality Agent** - Evaluates content quality, aesthetics, and brand alignment
3. **Engagement Analyst Agent** - Analyzes engagement patterns and authenticity
4. **Audience Demographics Agent** - Analyzes follower demographics and interests
5. **Brand Matching Agent** - Matches influencers with suitable brands
6. **Trend Analysis Agent** - Identifies trending topics and hashtags
7. **Authenticity Checker Agent** - Detects fake followers and engagement
8. **ROI Predictor Agent** - Predicts campaign performance and ROI

## 📊 Supported Platforms

- **Instagram**: Profile scraping, post analysis, story metrics, reel performance
- **Twitter/X**: Tweet analysis, engagement metrics, follower analysis
- **TikTok**: Video performance, trending content, audience demographics
- **YouTube**: Channel analytics, video performance, subscriber analysis

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis
- **AI/ML**: LangChain, OpenAI GPT-4, Anthropic Claude, Local LLMs
- **Web Scraping**: Selenium, BeautifulSoup, Social Media APIs
- **Frontend**: React, TypeScript, Tailwind CSS
- **Data Processing**: Pandas, NumPy, OpenCV, Pillow
- **Deployment**: Docker, Docker Compose

## 📋 Prerequisites

- Python 3.11+
- Docker (optional)
- Social Media API Keys (optional for enhanced features)
- OpenAI/Anthropic API Keys for AI analysis

## 🚀 Quick Start

### Using Poetry

1. Clone the repository:
```bash
git clone <repository-url>
cd influencer-discovery-app
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
# Start the backend API
poetry run uvicorn app.backend.main:app --reload

# In another terminal, start the frontend
cd app/frontend
npm install
npm start
```

### Using Docker

1. Clone and setup:
```bash
git clone <repository-url>
cd influencer-discovery-app
cp .env.example .env
# Edit .env with your API keys
```

2. Build and run:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔑 Environment Variables

Create a `.env` file with the following variables:

```bash
# AI API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GROQ_API_KEY=your-groq-api-key

# Social Media API Keys (optional)
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token
YOUTUBE_API_KEY=your-youtube-api-key
TIKTOK_ACCESS_TOKEN=your-tiktok-access-token

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/influencer_db
REDIS_URL=redis://localhost:6379

# App Configuration
SECRET_KEY=your-secret-key
DEBUG=True
```

## 📖 Usage

### Web Interface

1. **Dashboard**: Overview of discovered influencers and analytics
2. **Search**: Search for influencers by niche, location, follower count
3. **Brand Matching**: Input brand details to find matching influencers
4. **Analytics**: Detailed analytics and performance metrics
5. **Campaigns**: Manage influencer marketing campaigns

### API Endpoints

- `GET /api/influencers` - List discovered influencers
- `POST /api/influencers/search` - Search influencers with filters
- `POST /api/brands/{brand_id}/match` - Find matching influencers for a brand
- `GET /api/analytics/{influencer_id}` - Get influencer analytics
- `POST /api/scrape/platform/{platform}` - Trigger scraping for a platform

### Command Line

```bash
# Discover influencers on Instagram
poetry run python src/main.py --platform instagram --niche fitness --min-followers 10000

# Analyze specific influencer
poetry run python src/analyze.py --username @influencer_handle --platform instagram

# Run brand matching
poetry run python src/match.py --brand "fitness apparel" --budget 5000
```

## 🔧 Configuration

### Scraping Settings

Configure scraping parameters in `config/scraping.yaml`:

```yaml
instagram:
  rate_limit: 1  # requests per second
  max_profiles: 1000
  min_followers: 1000
  
twitter:
  rate_limit: 2
  max_tweets: 500
  
tiktok:
  rate_limit: 1
  max_videos: 200
```

### AI Agent Settings

Configure AI agents in `config/agents.yaml`:

```yaml
profile_analyzer:
  model: "gpt-4"
  temperature: 0.3
  
content_quality:
  model: "claude-3-sonnet"
  temperature: 0.2
```

## 📊 Analytics & Metrics

The app provides comprehensive analytics:

- **Engagement Rate**: Likes, comments, shares per post
- **Audience Quality**: Follower authenticity and demographics  
- **Content Performance**: Best performing content types
- **Growth Trends**: Follower growth over time
- **Brand Alignment**: How well content aligns with brand values
- **ROI Predictions**: Expected campaign performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Legal & Ethical Considerations

- **Respect Platform Terms**: Ensure compliance with social media platform terms of service
- **Rate Limiting**: Implement proper rate limiting to avoid being blocked
- **Data Privacy**: Handle user data responsibly and in compliance with privacy laws
- **Ethical Scraping**: Only scrape publicly available information
- **API Usage**: Prefer official APIs when available

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern AI and web scraping technologies
- Inspired by the need for better influencer-brand matching
- Thanks to the open-source community for the amazing tools

## 📞 Support

For support, email support@example.com or open an issue on GitHub.
