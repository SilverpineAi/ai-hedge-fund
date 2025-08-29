# Backend API Documentation

FastAPI backend for the Influencer Lookalike Engine.

## 🏗️ Architecture

```
FastAPI Application
├── main.py              # FastAPI app with routes
├── db.py               # Database management (SQLite + Pinecone)
├── embeddings.py       # OpenAI embedding generation
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run
docker build -t influencer-backend .
docker run -p 8000:8000 --env-file .env influencer-backend
```

## 📡 API Endpoints

### Authentication
Currently no authentication required (MVP). Add JWT/OAuth for production.

### Health Check
```http
GET /health
```
Returns service status and component health.

### Influencer Management

#### Add Influencer
```http
POST /add_influencer
Content-Type: application/json

{
  "handle": "string",                    # Required: @username
  "bio": "string",                       # Optional: Bio text
  "captions": ["string"],                # Optional: Sample captions
  "follower_count": 0,                   # Optional: Number of followers
  "engagement_rate": 0.0,                # Optional: Engagement percentage
  "niche_tags": ["string"],              # Optional: Category tags
  "profile_pic_url": "string"            # Optional: Profile image URL
}
```

**Response:** `InfluencerResponse` object with generated ID

#### Get All Influencers
```http
GET /influencers?skip=0&limit=100
```
Returns paginated list of all influencers (admin/debug endpoint).

#### Delete Influencer
```http
DELETE /influencers/{handle}
```
Removes influencer from both SQLite and Pinecone (admin/debug endpoint).

### Search & Discovery

#### Find Lookalikes
```http
POST /find_lookalikes
Content-Type: application/json

{
  "seed_handle": "string",               # Search by existing handle
  "seed_bio": "string",                  # OR search by description
  "top_k": 10,                          # Number of results (1-50)
  "min_followers": 1000,                # Optional: Min follower filter
  "max_followers": 1000000,             # Optional: Max follower filter  
  "min_engagement": 2.0                 # Optional: Min engagement filter
}
```

**Response:**
```json
{
  "query_info": {
    "type": "seed_handle|raw_bio",
    "seed_handle": "username",
    "seed_bio": "description text"
  },
  "results": [
    {
      "id": 1,
      "handle": "similar_user",
      "bio": "Bio text",
      "follower_count": 50000,
      "engagement_rate": 3.2,
      "niche_tags": "fitness,health",
      "profile_pic_url": "https://...",
      "similarity_score": 0.89
    }
  ],
  "total_results": 10
}
```

## 🗄️ Database Schema

### SQLite Tables

#### influencers
```sql
CREATE TABLE influencers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    handle VARCHAR(100) UNIQUE NOT NULL,
    bio TEXT,
    follower_count INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    niche_tags TEXT,                    -- Comma-separated tags
    profile_pic_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Pinecone Vectors

- **Dimension**: 3072 (OpenAI text-embedding-3-large)
- **Metric**: Cosine similarity
- **Metadata**: Handle, bio, follower_count, engagement_rate, niche_tags

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `PINECONE_API_KEY` | Pinecone API key | Yes | - |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Yes | - |
| `PINECONE_INDEX_NAME` | Pinecone index name | No | `influencer-embeddings` |
| `DATABASE_URL` | Database connection string | No | `sqlite:///./influencers.db` |

### OpenAI Configuration

- **Model**: `text-embedding-3-large`
- **Max tokens**: ~8000 characters per request
- **Rate limits**: Handled with exponential backoff

### Pinecone Configuration

- **Auto-creates index** if it doesn't exist
- **Dimension**: 3072 (matches OpenAI model)
- **Metric**: Cosine similarity for semantic search

## 🧪 Testing

### Unit Tests
```bash
pytest
```

### Integration Tests
```bash
pytest tests/test_integration.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Add test influencer
curl -X POST http://localhost:8000/add_influencer \
  -H "Content-Type: application/json" \
  -d '{
    "handle": "testuser",
    "bio": "Fitness enthusiast and personal trainer",
    "follower_count": 50000,
    "engagement_rate": 3.5,
    "niche_tags": ["fitness", "health"]
  }'

# Search for similar
curl -X POST http://localhost:8000/find_lookalikes \
  -H "Content-Type: application/json" \
  -d '{
    "seed_handle": "testuser",
    "top_k": 5
  }'
```

## 🚀 Production Deployment

### Performance Optimization

1. **Database Connection Pooling**
   ```python
   # Use PostgreSQL with connection pooling
   DATABASE_URL=postgresql://user:pass@localhost/db
   ```

2. **Async Processing**
   ```python
   # All embedding operations are async-ready
   await embedding_service.generate_embedding(text)
   ```

3. **Caching**
   ```python
   # Add Redis caching for frequent queries
   @cache(expire=3600)
   async def find_lookalikes(...):
   ```

### Security

1. **API Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @limiter.limit("10/minute")
   async def add_influencer(...):
   ```

2. **Input Validation**
   ```python
   # Pydantic models handle validation
   # Add custom validators for business logic
   ```

3. **CORS Configuration**
   ```python
   # Update allowed origins for production
   allow_origins=["https://yourdomain.com"]
   ```

### Monitoring

1. **Logging**
   ```python
   import structlog
   logger = structlog.get_logger()
   ```

2. **Metrics**
   ```python
   from prometheus_client import Counter, Histogram
   REQUEST_COUNT = Counter('requests_total', 'Total requests')
   ```

3. **Health Checks**
   ```python
   # Comprehensive health checks included
   GET /health
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Pinecone Index Not Found**
   ```
   IndexNotFoundError: Index 'influencer-embeddings' not found
   ```
   - Check Pinecone dashboard
   - Verify environment and API key
   - Index will be auto-created on first run

2. **OpenAI Rate Limits**
   ```
   RateLimitError: Rate limit exceeded
   ```
   - Implement exponential backoff
   - Consider upgrading OpenAI plan
   - Cache embeddings to reduce API calls

3. **Database Lock Errors**
   ```
   sqlite3.OperationalError: database is locked
   ```
   - Use connection pooling
   - Consider PostgreSQL for production
   - Check file permissions

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

### Performance Profiling

```bash
# Install profiling tools
pip install py-spy

# Profile running application
py-spy record -o profile.svg --pid <process_id>
```

## 📚 Code Examples

### Custom Embedding Processing

```python
from embeddings import EmbeddingService

# Initialize service
embedding_service = EmbeddingService(api_key="your-key")

# Process custom text
text = "Tech reviewer covering latest smartphones and gadgets"
embedding = await embedding_service.generate_query_embedding(text)

# Search similar influencers
results = db.find_similar_influencers(embedding, top_k=10)
```

### Batch Processing

```python
# Add multiple influencers
influencers = [
    {"handle": "user1", "bio": "Fitness trainer"},
    {"handle": "user2", "bio": "Nutrition expert"},
    # ... more influencers
]

for inf_data in influencers:
    embedding = embedding_service.generate_influencer_embedding_sync(
        bio=inf_data["bio"], 
        captions=[]
    )
    db.add_influencer(InfluencerCreate(**inf_data), embedding)
```

### Custom Similarity Search

```python
# Advanced search with custom filters
def find_niche_influencers(niche: str, min_followers: int = 10000):
    # Generate embedding for niche description
    niche_embedding = embedding_service.generate_query_embedding_sync(niche)
    
    # Search with custom filters
    results = db.find_similar_influencers(
        query_embedding=niche_embedding,
        top_k=20,
        filters={
            "follower_count_min": min_followers,
            "niche_filter": niche
        }
    )
    
    return results
```

## 🔄 API Versioning

Future versions will include:
- `/v1/` prefix for all endpoints
- Backward compatibility support
- Deprecation warnings

```python
# Future API structure
@app.post("/v1/add_influencer")
@app.post("/v1/find_lookalikes")
```