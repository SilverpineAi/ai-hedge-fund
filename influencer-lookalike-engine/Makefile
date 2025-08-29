# Influencer Lookalike Engine - Development Commands

.PHONY: help install dev prod down clean test lint format

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Development
install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && python -m pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

dev: ## Start development environment
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

prod: ## Start production environment
	@echo "Starting production environment..."
	docker-compose up -d
	@echo "✅ Production environment started!"

down: ## Stop all containers
	@echo "Stopping containers..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ All containers stopped!"

# Database
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "⚠️  This will destroy all database data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker volume rm influencer-lookalike-engine_backend_data 2>/dev/null || true
	@echo "✅ Database reset complete!"

# Testing
test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false
	@echo "✅ All tests passed!"

test-backend: ## Run backend tests only
	cd backend && python -m pytest

test-frontend: ## Run frontend tests only
	cd frontend && npm test -- --watchAll=false

# Code Quality
lint: ## Run linters
	@echo "Linting backend..."
	cd backend && python -m flake8 .
	@echo "Linting frontend..."
	cd frontend && npm run lint 2>/dev/null || echo "Frontend linting not configured"
	@echo "✅ Linting complete!"

format: ## Format code
	@echo "Formatting backend code..."
	cd backend && python -m black .
	@echo "Formatting frontend code..."
	cd frontend && npx prettier --write src/
	@echo "✅ Code formatting complete!"

# Cleanup
clean: ## Clean up build artifacts and caches
	@echo "Cleaning up..."
	cd backend && rm -rf __pycache__ .pytest_cache *.egg-info
	cd frontend && rm -rf build node_modules/.cache
	docker system prune -f
	@echo "✅ Cleanup complete!"

# Logs
logs: ## Show container logs
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

# Health checks
health: ## Check service health
	@echo "Checking backend health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ Backend not responding"
	@echo "Checking frontend..."
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200" && echo "✅ Frontend OK" || echo "❌ Frontend not responding"

# Build
build: ## Build all containers
	@echo "Building containers..."
	docker-compose build
	@echo "✅ Build complete!"

build-backend: ## Build backend container only
	docker-compose build backend

build-frontend: ## Build frontend container only
	docker-compose build frontend

# Database operations
db-backup: ## Backup database
	@echo "Creating database backup..."
	docker-compose exec backend cp /app/data/influencers.db /app/data/influencers_backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "✅ Database backup created!"

# Quick setup for new developers
setup: ## Complete setup for new developers
	@echo "🚀 Setting up Influencer Lookalike Engine..."
	@echo "1. Copying environment file..."
	cp backend/.env.example .env
	@echo "2. Installing dependencies..."
	$(MAKE) install
	@echo "3. Building containers..."
	$(MAKE) build
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run 'make dev' to start development environment"
	@echo "3. Visit http://localhost:3000 to see the application"

# Production deployment helpers
deploy-check: ## Check if ready for production deployment
	@echo "🔍 Checking production readiness..."
	@test -f .env || (echo "❌ .env file missing" && exit 1)
	@grep -q "your_.*_key_here" .env && echo "❌ Please update API keys in .env" && exit 1 || echo "✅ API keys configured"
	@docker-compose config >/dev/null && echo "✅ Docker configuration valid" || (echo "❌ Docker configuration invalid" && exit 1)
	@echo "✅ Ready for production deployment!"

# Monitoring
stats: ## Show container resource usage
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"