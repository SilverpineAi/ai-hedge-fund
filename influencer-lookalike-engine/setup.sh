#!/bin/bash

# Influencer Lookalike Engine - Quick Setup Script
# This script helps you get started quickly with the development environment

set -e  # Exit on any error

echo "🚀 Influencer Lookalike Engine - Quick Setup"
echo "============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if required tools are installed
check_requirements() {
    echo "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_status "All requirements met!"
}

# Create environment file
setup_environment() {
    echo ""
    echo "Setting up environment..."
    
    if [ ! -f .env ]; then
        cp backend/.env.example .env
        print_status "Created .env file from template"
        
        print_warning "IMPORTANT: You need to update the .env file with your API keys!"
        print_info "Required API keys:"
        echo "  - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)"
        echo "  - PINECONE_API_KEY (get from https://app.pinecone.io/)"
        echo "  - PINECONE_ENVIRONMENT (from your Pinecone dashboard)"
        echo ""
        
        read -p "Do you want to edit the .env file now? [y/N]: " edit_env
        if [[ $edit_env =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        print_info ".env file already exists, skipping creation"
    fi
}

# Check if API keys are configured
check_api_keys() {
    echo ""
    echo "Checking API key configuration..."
    
    if grep -q "your_.*_key_here" .env; then
        print_warning "API keys not configured yet!"
        print_info "Please update your .env file with real API keys before running the application."
        return 1
    else
        print_status "API keys appear to be configured"
        return 0
    fi
}

# Build Docker containers
build_containers() {
    echo ""
    echo "Building Docker containers..."
    
    print_info "This may take a few minutes on first run..."
    if docker-compose build; then
        print_status "Docker containers built successfully!"
    else
        print_error "Failed to build Docker containers"
        exit 1
    fi
}

# Start development environment
start_development() {
    echo ""
    echo "Starting development environment..."
    
    if docker-compose -f docker-compose.dev.yml up -d; then
        print_status "Development environment started!"
        
        # Wait a moment for services to start
        sleep 3
        
        echo ""
        print_info "Services are starting up..."
        print_info "Frontend: http://localhost:3000"
        print_info "Backend API: http://localhost:8000"
        print_info "API Documentation: http://localhost:8000/docs"
        
        # Check service health
        echo ""
        echo "Checking service health..."
        
        # Wait for backend to be ready
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                print_status "Backend is healthy!"
                break
            fi
            
            if [ $i -eq 30 ]; then
                print_warning "Backend health check timed out. Check logs with: docker-compose logs backend"
            else
                echo -n "."
                sleep 2
            fi
        done
        
        # Check frontend
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_status "Frontend is running!"
        else
            print_warning "Frontend not responding yet. It may still be starting up."
        fi
        
    else
        print_error "Failed to start development environment"
        exit 1
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup complete!"
    echo "=================="
    echo ""
    print_info "Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Try adding a sample influencer"
    echo "3. Search for similar influencers"
    echo ""
    print_info "Useful commands:"
    echo "• View logs: docker-compose logs -f"
    echo "• Stop services: docker-compose down"
    echo "• Restart: docker-compose restart"
    echo "• Full cleanup: make clean"
    echo ""
    print_info "For more commands, run: make help"
    echo ""
    print_info "Documentation:"
    echo "• Main README: README.md"
    echo "• Backend API: backend/README.md"
    echo "• Frontend: frontend/README.md"
}

# Main setup flow
main() {
    check_requirements
    setup_environment
    
    # Check if API keys are configured
    if check_api_keys; then
        build_containers
        start_development
        show_next_steps
    else
        echo ""
        print_warning "Setup paused - API keys need to be configured"
        print_info "After updating your .env file, run this script again or use:"
        echo "  make dev"
        echo ""
        print_info "To get API keys:"
        echo "• OpenAI: https://platform.openai.com/api-keys"
        echo "• Pinecone: https://app.pinecone.io/"
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --force        Skip API key check and start anyway"
        echo ""
        exit 0
        ;;
    --force)
        print_warning "Forcing start without API key validation"
        check_requirements
        setup_environment
        build_containers
        start_development
        show_next_steps
        ;;
    *)
        main
        ;;
esac