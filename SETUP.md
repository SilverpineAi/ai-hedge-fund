# Influencer Discovery App - Setup Guide

This guide will help you set up and run the AI-powered influencer discovery application.

## 📋 Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- Docker and Docker Compose (optional, for containerized deployment)
- Chrome browser (for web scraping)
- PostgreSQL (if running without Docker)
- Redis (if running without Docker)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd influencer-discovery-app
```

### 2. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Environment Configuration

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys and configuration:

```bash
# Required: At least one AI API key
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROQ_API_KEY=your-groq-api-key-here

# Optional: Social Media API keys for enhanced features
TWITTER_BEARER_TOKEN=your-twitter-bearer-token-here
INSTAGRAM_USERNAME=your-instagram-username
INSTAGRAM_PASSWORD=your-instagram-password

# Database (if not using Docker)
DATABASE_URL=postgresql://user:password@localhost:5432/influencer_discovery
REDIS_URL=redis://localhost:6379/0
```

### 5. Run the Application

#### Option A: Using Poetry (Development)

```bash
# Terminal 1: Start the backend API
poetry run uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Run command-line interface
poetry run python src/main.py --platform instagram --keyword fitness --min-followers 10000
```

#### Option B: Using Docker (Production)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## 🔧 Configuration

### API Keys Setup

1. **OpenAI API Key** (Recommended)
   - Sign up at https://platform.openai.com/
   - Create an API key
   - Add to `.env`: `OPENAI_API_KEY=your-key-here`

2. **Twitter API** (Optional)
   - Apply for developer account at https://developer.twitter.com/
   - Create an app and get Bearer Token
   - Add to `.env`: `TWITTER_BEARER_TOKEN=your-token-here`

3. **Instagram Credentials** (Optional)
   - Use your personal Instagram account
   - Add to `.env`: `INSTAGRAM_USERNAME=your-username` and `INSTAGRAM_PASSWORD=your-password`

### Database Setup (Without Docker)

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create Database**
   ```bash
   sudo -u postgres createuser influencer_user
   sudo -u postgres createdb influencer_discovery
   sudo -u postgres psql -c "ALTER USER influencer_user WITH PASSWORD 'secure_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE influencer_discovery TO influencer_user;"
   ```

3. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

## 🖥️ Usage Examples

### Command Line Interface

```bash
# Discover fitness influencers on Instagram
poetry run python src/main.py --platform instagram --keyword fitness --min-followers 10000

# Analyze specific influencer
poetry run python src/main.py --analyze-user @username --platform instagram

# Brand matching with JSON file
poetry run python src/main.py --platform instagram --keyword tech --brand-match brand_requirements.json
```

### API Usage

```bash
# Health check
curl http://localhost:8000/health

# Search influencers
curl -X POST "http://localhost:8000/api/influencers/search" \
  -H "Content-Type: application/json" \
  -d '{"platform": "instagram", "keyword": "fitness", "min_followers": 10000}'

# Get platforms
curl http://localhost:8000/api/platforms

# Get categories
curl http://localhost:8000/api/categories
```

### Brand Requirements JSON Example

Create `brand_requirements.json`:

```json
{
  "name": "FitTech Pro",
  "industry": "Fitness Technology",
  "description": "Smart fitness equipment and apps",
  "target_categories": ["fitness", "tech", "lifestyle"],
  "min_followers": 50000,
  "max_followers": 1000000,
  "min_engagement_rate": 2.5,
  "target_demographics": {
    "age_range": "25-45",
    "interests": ["fitness", "technology", "health"]
  },
  "budget_range": {
    "min": 1000,
    "max": 10000
  },
  "brand_values": ["innovation", "health", "quality", "sustainability"]
}
```

## 🐳 Docker Deployment

### Full Stack Deployment

```bash
# Start all services
docker-compose up -d

# Services included:
# - PostgreSQL database
# - Redis cache
# - Backend API
# - Frontend (if configured)
# - Background workers
# - Monitoring tools
```

### Individual Services

```bash
# Backend only
docker-compose up -d postgres redis backend

# With monitoring
docker-compose --profile admin up -d

# With scraping capabilities
docker-compose --profile scraping up -d

# With analytics
docker-compose --profile analytics up -d
```

### Service URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **pgAdmin**: http://localhost:5050 (admin profile)
- **Flower**: http://localhost:5555 (monitoring)
- **Kibana**: http://localhost:5601 (analytics profile)

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the poetry environment
   poetry shell
   
   # Or prefix commands with poetry run
   poetry run python src/main.py --help
   ```

2. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Test connection
   poetry run python -c "from src.database.connection import test_database_connection; print(test_database_connection())"
   ```

3. **API Key Issues**
   ```bash
   # Verify API keys are loaded
   poetry run python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
   ```

4. **Chrome Driver Issues**
   ```bash
   # Install Chrome driver
   sudo apt-get update
   sudo apt-get install -y wget unzip
   wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE/chromedriver_linux64.zip
   sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
   ```

### Performance Optimization

1. **Rate Limiting**: Adjust scraping rate limits in scrapers
2. **Database Indexing**: Ensure proper indexes for search queries
3. **Caching**: Use Redis for caching API responses
4. **Background Tasks**: Use Celery for long-running operations

## 📝 Development

### Project Structure

```
influencer-discovery-app/
├── src/
│   ├── agents/          # AI agents for analysis
│   ├── database/        # Database models and operations
│   ├── scrapers/        # Social media scrapers
│   └── llm/            # LLM configurations
├── app/
│   ├── backend/        # FastAPI application
│   └── frontend/       # React application (future)
├── docker/             # Docker configurations
├── tests/              # Test files
└── docs/               # Documentation
```

### Adding New Features

1. **New Social Platform**
   - Create scraper in `src/scrapers/`
   - Inherit from `BaseScraper`
   - Add to `__init__.py`

2. **New AI Agent**
   - Create agent in `src/agents/`
   - Inherit from `BaseAgent`
   - Add to `__init__.py`

3. **New API Endpoint**
   - Add to `app/backend/main.py`
   - Follow FastAPI patterns

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_scrapers.py

# Run with coverage
poetry run pytest --cov=src tests/
```

## 🚀 Production Deployment

1. **Environment Variables**: Set production values
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **API Keys**: Store securely (AWS Secrets Manager, etc.)
5. **Monitoring**: Set up logging and monitoring
6. **Load Balancing**: Use nginx for load balancing
7. **SSL**: Configure HTTPS certificates

## 📞 Support

For issues and questions:
1. Check this setup guide
2. Review the main README.md
3. Check the API documentation at `/docs`
4. Open an issue on GitHub

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement rate limiting for production
- Regular security updates for dependencies
- Monitor API usage and costs