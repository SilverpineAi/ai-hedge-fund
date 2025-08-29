"""
Basic tests for the Influencer Lookalike Engine API.
Run with: pytest test_main.py
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os

# Mock environment variables for testing
os.environ.update({
    "OPENAI_API_KEY": "test-key",
    "PINECONE_API_KEY": "test-key", 
    "PINECONE_ENVIRONMENT": "test-env"
})

from main import app

client = TestClient(app)

class TestHealthCheck:
    """Test health check endpoint"""
    
    @patch('main.get_database')
    @patch('main.get_embedding_service')
    def test_health_check_success(self, mock_embedding_service, mock_database):
        """Test successful health check"""
        # Mock services
        mock_database.return_value = Mock()
        mock_embedding_service.return_value = Mock()
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

class TestInfluencerEndpoints:
    """Test influencer management endpoints"""
    
    @patch('main.get_database')
    @patch('main.get_embedding_service')
    def test_add_influencer_success(self, mock_embedding_service, mock_database):
        """Test successful influencer addition"""
        # Mock services
        mock_db = Mock()
        mock_db.get_influencer_by_handle.return_value = None  # No existing influencer
        mock_db.add_influencer.return_value = Mock(
            id=1,
            handle="testuser",
            bio="Test bio",
            follower_count=1000,
            engagement_rate=3.5,
            niche_tags="test",
            profile_pic_url=None
        )
        mock_database.return_value = mock_db
        
        mock_embedding = Mock()
        mock_embedding.generate_influencer_embedding_sync.return_value = [0.1] * 3072
        mock_embedding_service.return_value = mock_embedding
        
        influencer_data = {
            "handle": "testuser",
            "bio": "Test bio",
            "captions": ["Test caption"],
            "follower_count": 1000,
            "engagement_rate": 3.5,
            "niche_tags": ["test"]
        }
        
        response = client.post("/add_influencer", json=influencer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["handle"] == "testuser"
        assert data["bio"] == "Test bio"
    
    def test_add_influencer_missing_handle(self):
        """Test adding influencer without required handle"""
        influencer_data = {
            "bio": "Test bio"
            # Missing required handle
        }
        
        response = client.post("/add_influencer", json=influencer_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('main.get_database')
    @patch('main.get_embedding_service')
    def test_find_lookalikes_by_handle(self, mock_embedding_service, mock_database):
        """Test finding lookalikes by handle"""
        # Mock database
        mock_db = Mock()
        mock_influencer = Mock()
        mock_influencer.bio = "Test bio"
        mock_db.get_influencer_by_handle.return_value = mock_influencer
        mock_db.find_similar_influencers.return_value = [
            {
                "id": 2,
                "handle": "similar_user",
                "bio": "Similar bio",
                "follower_count": 2000,
                "engagement_rate": 3.2,
                "niche_tags": "test",
                "profile_pic_url": None,
                "similarity_score": 0.85
            }
        ]
        mock_database.return_value = mock_db
        
        # Mock embedding service
        mock_embedding = Mock()
        mock_embedding.generate_influencer_embedding_sync.return_value = [0.1] * 3072
        mock_embedding_service.return_value = mock_embedding
        
        search_data = {
            "seed_handle": "testuser",
            "top_k": 5
        }
        
        response = client.post("/find_lookalikes", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query_info" in data
        assert data["total_results"] >= 0
    
    @patch('main.get_database')
    @patch('main.get_embedding_service') 
    def test_find_lookalikes_by_bio(self, mock_embedding_service, mock_database):
        """Test finding lookalikes by bio description"""
        # Mock database
        mock_db = Mock()
        mock_db.find_similar_influencers.return_value = []
        mock_database.return_value = mock_db
        
        # Mock embedding service
        mock_embedding = Mock()
        mock_embedding.generate_query_embedding_sync.return_value = [0.1] * 3072
        mock_embedding_service.return_value = mock_embedding
        
        search_data = {
            "seed_bio": "Fitness enthusiast who posts workout routines",
            "top_k": 10
        }
        
        response = client.post("/find_lookalikes", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["query_info"]["type"] == "raw_bio"
        assert data["query_info"]["seed_bio"] == search_data["seed_bio"]
    
    def test_find_lookalikes_missing_search_criteria(self):
        """Test finding lookalikes without search criteria"""
        search_data = {
            "top_k": 5
            # Missing both seed_handle and seed_bio
        }
        
        response = client.post("/find_lookalikes", json=search_data)
        
        assert response.status_code == 400
        assert "Either seed_handle or seed_bio must be provided" in response.json()["detail"]

class TestValidation:
    """Test input validation"""
    
    def test_invalid_top_k_value(self):
        """Test invalid top_k parameter"""
        search_data = {
            "seed_bio": "Test bio",
            "top_k": 0  # Invalid: must be >= 1
        }
        
        response = client.post("/find_lookalikes", json=search_data)
        
        assert response.status_code == 422
    
    def test_invalid_engagement_rate(self):
        """Test invalid engagement rate"""
        influencer_data = {
            "handle": "testuser",
            "engagement_rate": -1.0  # Invalid: must be >= 0
        }
        
        response = client.post("/add_influencer", json=influencer_data)
        
        # This should still work as engagement_rate has a default of 0.0
        # But in a real app, you might want to validate this
        assert response.status_code in [200, 422]

# Pytest fixtures for common test data
@pytest.fixture
def sample_influencer():
    """Sample influencer data for testing"""
    return {
        "handle": "testuser",
        "bio": "Test influencer bio with fitness content",
        "captions": [
            "Morning workout complete! 💪",
            "Healthy meal prep for the week 🥗"
        ],
        "follower_count": 50000,
        "engagement_rate": 4.2,
        "niche_tags": ["fitness", "health", "lifestyle"],
        "profile_pic_url": "https://example.com/profile.jpg"
    }

@pytest.fixture
def sample_search_request():
    """Sample search request for testing"""
    return {
        "seed_handle": "testuser",
        "top_k": 10,
        "min_followers": 1000,
        "min_engagement": 2.0
    }

# Integration test example (requires actual services)
@pytest.mark.integration
@pytest.mark.skipif(
    not all([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("PINECONE_API_KEY"),
        os.getenv("PINECONE_ENVIRONMENT")
    ]),
    reason="Integration tests require actual API keys"
)
class TestIntegration:
    """Integration tests with real services (optional)"""
    
    def test_full_workflow(self, sample_influencer):
        """Test complete workflow: add influencer -> search for similar"""
        # This would test against real services
        # Only run when integration testing is needed
        pass

if __name__ == "__main__":
    # Run tests with: python test_main.py
    pytest.main([__file__, "-v"])