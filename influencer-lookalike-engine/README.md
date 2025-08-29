# Influencer Lookalike Engine

An AI-powered MVP that functions like Meta's lookalike audiences but for influencers. Find similar influencers using OpenAI embeddings and vector similarity search.

![Influencer Lookalike Engine](https://via.placeholder.com/800x400/667eea/ffffff?text=Influencer+Lookalike+Engine)

## 🚀 Features

### Core Functionality
- **Add Influencer**: Input handle, bio, and sample captions to build your database
- **Find Lookalikes**: Discover similar influencers using AI-powered semantic search
- **Smart Filtering**: Filter results by follower count, engagement rate, and niche tags
- **Similarity Scoring**: Get ranked results with similarity percentages

### Technical Features
- **Vector Search**: Powered by Pinecone for fast, scalable similarity matching
- **AI Embeddings**: Uses OpenAI's text-embedding-3-large for semantic understanding
- **Dual Database**: Pinecone for vectors + SQLite/Postgres for metadata
- **Modern UI**: React + Tailwind CSS with responsive design
- **Production Ready**: Docker containerization with health checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   Pinecone DB   │
│                 │────│                 │────│                 │
│ • Search UI     │    │ • REST API      │    │ • Vector Store  │
│ • Results View  │    │ • Embeddings    │    │ • Similarity    │
│ • Filters       │    │ • DB Management │    │   Search        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                       ┌─────────────────┐
                       │  SQLite/Postgres │
                       │                 │
                       │ • Metadata      │
                       │ • User Data     │
                       └─────────────────┘
```

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended)
- **OR Manual Setup**:
  - Python 3.11+
  - Node.js 18+
  - OpenAI API key
  - Pinecone account

## 🛠️ Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd influencer-lookalike-engine
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment_here
   PINECONE_INDEX_NAME=influencer-embeddings
   ```

3. **Start the application**
   ```bash
   # Production mode
   docker-compose up -d
   
   # Development mode (with hot reloading)
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the backend
uvicorn main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📖 API Documentation

### Core Endpoints

#### Add Influencer
```http
POST /add_influencer
Content-Type: application/json

{
  "handle": "username",
  "bio": "Influencer bio text",
  "captions": ["Sample caption 1", "Sample caption 2"],
  "follower_count": 50000,
  "engagement_rate": 3.2,
  "niche_tags": ["fitness", "lifestyle"],
  "profile_pic_url": "https://example.com/pic.jpg"
}
```

#### Find Lookalikes
```http
POST /find_lookalikes
Content-Type: application/json

{
  "seed_handle": "username",          // OR
  "seed_bio": "fitness enthusiast",   // Raw text search
  "top_k": 10,
  "min_followers": 10000,
  "max_followers": 1000000,
  "min_engagement": 2.0
}
```

#### Health Check
```http
GET /health
```

### Response Format

```json
{
  "query_info": {
    "type": "seed_handle",
    "seed_handle": "username",
    "seed_bio": "Bio text"
  },
  "results": [
    {
      "id": 1,
      "handle": "similar_user",
      "bio": "Similar influencer bio",
      "follower_count": 45000,
      "engagement_rate": 3.1,
      "niche_tags": "fitness,health",
      "profile_pic_url": "https://...",
      "similarity_score": 0.89
    }
  ],
  "total_results": 10
}
```

## 🎯 Usage Examples

### 1. Add Sample Influencers

```python
import requests

# Add a fitness influencer
response = requests.post("http://localhost:8000/add_influencer", json={
    "handle": "fitnessguru",
    "bio": "Personal trainer helping you achieve your fitness goals 💪",
    "captions": [
        "Morning workout complete! Remember, consistency is key 🔥",
        "Healthy meal prep Sunday. Fuel your body right! 🥗"
    ],
    "follower_count": 75000,
    "engagement_rate": 4.2,
    "niche_tags": ["fitness", "health", "motivation"]
})
```

### 2. Find Similar Influencers

```python
# Search by handle
response = requests.post("http://localhost:8000/find_lookalikes", json={
    "seed_handle": "fitnessguru",
    "top_k": 5
})

# Search by description
response = requests.post("http://localhost:8000/find_lookalikes", json={
    "seed_bio": "Tech reviewer who covers latest gadgets and smartphones",
    "top_k": 10,
    "min_followers": 20000
})
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | `influencer-embeddings` |
| `DATABASE_URL` | SQLite/Postgres connection | `sqlite:///./influencers.db` |

### Frontend Configuration

Create `frontend/.env.local`:
```env
REACT_APP_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Add influencer
curl -X POST http://localhost:8000/add_influencer \
  -H "Content-Type: application/json" \
  -d '{
    "handle": "testuser",
    "bio": "Test bio",
    "follower_count": 1000
  }'

# Find lookalikes
curl -X POST http://localhost:8000/find_lookalikes \
  -H "Content-Type: application/json" \
  -d '{
    "seed_handle": "testuser",
    "top_k": 5
  }'
```

## 🚀 Deployment

### Production Deployment

1. **Set up production environment**
   ```bash
   # Use production docker-compose
   docker-compose -f docker-compose.yml up -d
   ```

2. **Configure reverse proxy** (nginx example)
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:3000;
       }
       
       location /api/ {
           proxy_pass http://localhost:8000/;
       }
   }
   ```

3. **Set up SSL** with Let's Encrypt
   ```bash
   certbot --nginx -d yourdomain.com
   ```

### Scaling Considerations

- **Database**: Switch to PostgreSQL for production
- **Vector DB**: Pinecone scales automatically
- **Caching**: Add Redis for API response caching
- **Load Balancing**: Use multiple backend instances
- **Monitoring**: Add logging and metrics collection

## 🔮 Stretch Goals & Future Features

### Phase 2 Enhancements
- **Auto-scraping**: Automatically fetch influencer data from social platforms
- **Multi-platform**: Support Instagram, TikTok, YouTube, Twitter
- **Advanced Filters**: Location, age, gender, brand affinity
- **Batch Processing**: Upload CSV files with multiple influencers

### Phase 3 Advanced Features
- **Visualization**: Interactive clustering with D3.js/Recharts
- **API Rate Limiting**: Implement usage quotas
- **User Authentication**: Multi-tenant support
- **Analytics Dashboard**: Usage stats and insights
- **Export Features**: PDF reports, CSV exports

### Phase 4 Enterprise Features
- **Campaign Management**: Track influencer outreach
- **Performance Metrics**: ROI tracking and analytics
- **Integration APIs**: Connect with marketing tools
- **White-label Solution**: Custom branding options

## 🐛 Troubleshooting

### Common Issues

1. **Pinecone Connection Error**
   ```
   Error: Failed to initialize Pinecone
   ```
   - Verify API key and environment are correct
   - Check Pinecone dashboard for service status

2. **OpenAI API Quota Exceeded**
   ```
   Error: Rate limit exceeded
   ```
   - Check your OpenAI usage limits
   - Implement request queuing for high-volume usage

3. **Frontend Can't Connect to Backend**
   ```
   Network Error
   ```
   - Verify backend is running on port 8000
   - Check CORS settings in main.py

4. **Docker Build Issues**
   ```
   Error: Cannot find module
   ```
   - Clear Docker cache: `docker system prune -a`
   - Rebuild images: `docker-compose build --no-cache`

### Debug Mode

Enable debug logging:
```bash
# Backend
export LOG_LEVEL=DEBUG

# Frontend
export REACT_APP_DEBUG=true
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Documentation**: Check this README and API docs
- **Issues**: Create a GitHub issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: contact@yourcompany.com

---

**Built with ❤️ using FastAPI, React, OpenAI, and Pinecone**