# Sales Intelligence Platform

A comprehensive sales intelligence platform that processes lead lists, enriches data, detects growth signals, and prioritizes outreach opportunities.

![Sales Intelligence Platform](https://img.shields.io/badge/Status-MVP%20Complete-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue)

## 🚀 Features

### Core Functionality
- **CSV Upload & Processing**: Upload lead lists with up to 10,000 contacts
- **Data Enrichment**: Automatically find missing emails, LinkedIn profiles, and company data
- **Growth Signals**: Detect funding, leadership changes, product launches, and market activity
- **Contact Grading**: Grade contacts A-F based on data quality and decision-making power
- **Prospect Scoring**: Score prospects 0-100 based on signal strength and timing
- **Task Generation**: AI-powered outreach task recommendations across multiple channels

### Technical Features
- **Multi-tenant Architecture**: Project-based organization for scalability
- **Real-time Processing**: Progress tracking for batch operations
- **API Integration**: Hunter.io, Clearbit, News APIs for data enrichment
- **Performance Optimized**: Handles 1000+ leads efficiently
- **Enterprise Security**: File validation, rate limiting, comprehensive error handling

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with async support
- **SQLAlchemy**: ORM with async support for database operations
- **Pydantic**: Data validation and serialization
- **Background Jobs**: Async processing for data enrichment and scoring

### Frontend (React + TypeScript)
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality, accessible UI components
- **React Query**: Server state management and caching
- **React Router**: Client-side routing

### Database Schema
- **Contacts**: Full contact profiles with enrichment status and scores
- **Companies**: Company intelligence data and growth tracking
- **Signals**: Time-stamped growth events with relevance scoring
- **Tasks**: AI-generated outreach recommendations
- **Projects**: Multi-tenant organization structure

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 13+
- Git

### One-Command Setup
```bash
cd app
chmod +x start.sh
./start.sh
```

This script will:
1. Check all dependencies
2. Set up Python virtual environment
3. Install backend dependencies
4. Create database
5. Install frontend dependencies
6. Start both services
7. Open your browser automatically

### Manual Setup

#### Backend Setup
```bash
cd app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys and database settings

# Create database
createdb sales_intelligence

# Start backend
uvicorn main:app --reload
```

#### Frontend Setup
```bash
cd app/frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start frontend
npm run dev
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/sales_intelligence

# External APIs
HUNTER_API_KEY=your_hunter_io_api_key
CLEARBIT_API_KEY=your_clearbit_api_key
NEWS_API_KEY=your_news_api_key

# Security
SECRET_KEY=your_secret_key_here
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

### API Keys Setup
1. **Hunter.io**: Email finding service
   - Sign up at [hunter.io](https://hunter.io)
   - Get API key from dashboard
   - 100 free requests/month

2. **Clearbit**: Company enrichment
   - Sign up at [clearbit.com](https://clearbit.com)
   - Get API key from settings
   - Free tier available

3. **News API**: Growth signal detection
   - Sign up at [newsapi.org](https://newsapi.org)
   - Get API key from dashboard
   - 500 free requests/day

## 📊 Usage

### 1. Create a Project
- Navigate to Projects page
- Click "New Project"
- Enter project name and description

### 2. Upload Contacts
- Go to Upload page
- Select your project
- Drag & drop CSV file or click to browse
- Review upload results and validation errors

### 3. Enrich Data
- Contacts are automatically queued for enrichment
- Monitor progress in real-time
- View enriched data in contact profiles

### 4. Review Scores & Grades
- Contacts are automatically scored and graded
- View top prospects on dashboard
- Filter by grade and score ranges

### 5. Detect Signals
- Growth signals are detected automatically
- View recent high-impact signals
- Signals influence prospect scoring

### 6. Execute Tasks
- AI generates outreach recommendations
- Tasks are prioritized by urgency and impact
- Track completion and follow-ups

## 📁 CSV Format

### Required Columns
- `full_name`: Contact's full name

### Optional Columns
- `first_name`, `last_name`: Name components
- `email`: Email address
- `phone`: Phone number
- `title`: Job title
- `company_name`: Company name
- `company_domain`: Company website
- `location`: Geographic location
- `linkedin_url`: LinkedIn profile URL
- `department`: Department/function
- `seniority_level`: Seniority level

### Example CSV
```csv
full_name,email,title,company_name,company_domain,location
John Smith,john@acme.com,VP Sales,Acme Corp,acme.com,New York
Jane Doe,,Marketing Manager,TechStart,techstart.io,San Francisco
```

## 🔌 API Documentation

Once the backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints
- `POST /api/v1/upload/csv` - Upload CSV file
- `GET /api/v1/contacts` - List contacts with filtering
- `POST /api/v1/contacts/{id}/enrich` - Enrich specific contact
- `POST /api/v1/contacts/{id}/score` - Score specific contact
- `GET /api/v1/signals` - List growth signals
- `GET /api/v1/dashboard/overview` - Dashboard statistics

## 🏢 Scaling for Production

### Performance Optimizations
- **Database Indexing**: Optimized indexes for common queries
- **Async Processing**: Background jobs for heavy operations
- **Rate Limiting**: API rate limiting to prevent abuse
- **Caching**: Redis caching for frequently accessed data
- **CDN**: Static asset delivery via CDN

### Security Features
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Parameterized queries
- **File Upload Security**: Type and size validation
- **CORS Configuration**: Proper cross-origin setup
- **Authentication Ready**: JWT token infrastructure

### Deployment
- **Docker Support**: Containerized deployment
- **Environment Variables**: 12-factor app configuration
- **Health Checks**: Application health monitoring
- **Logging**: Structured logging with levels
- **Monitoring**: Application performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**Database Connection Error**
```bash
# Make sure PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

**API Key Errors**
- Verify API keys in `.env` file
- Check API key quotas and limits
- Ensure proper network connectivity

**Port Already in Use**
```bash
# Kill processes on ports 8000 and 5173
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Getting Help
- 📧 Email: support@salesintelligence.com
- 💬 Discord: [Join our community](https://discord.gg/salesintel)
- 📖 Documentation: [docs.salesintelligence.com](https://docs.salesintelligence.com)
- 🐛 Bug Reports: [GitHub Issues](https://github.com/your-org/sales-intelligence/issues)

---

Built with ❤️ for sales teams who want to work smarter, not harder.