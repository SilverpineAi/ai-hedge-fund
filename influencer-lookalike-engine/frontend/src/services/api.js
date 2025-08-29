import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 404:
          throw new Error(data.detail || 'Resource not found');
        case 409:
          throw new Error(data.detail || 'Resource already exists');
        case 422:
          throw new Error(data.detail || 'Invalid data provided');
        case 500:
          throw new Error('Server error. Please try again later.');
        default:
          throw new Error(data.detail || `Server error (${status})`);
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error. Please check your connection.');
    } else {
      // Other error
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// API service functions
export const apiService = {
  // Health check
  async checkHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Add influencer
  async addInfluencer(influencerData) {
    const response = await api.post('/add_influencer', influencerData);
    return response.data;
  },

  // Find lookalikes
  async findLookalikes(searchData) {
    const response = await api.post('/find_lookalikes', searchData);
    return response.data;
  },

  // Get all influencers (for debugging/admin)
  async getAllInfluencers(skip = 0, limit = 100) {
    const response = await api.get('/influencers', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Delete influencer (for debugging/admin)
  async deleteInfluencer(handle) {
    const response = await api.delete(`/influencers/${handle}`);
    return response.data;
  }
};

export default api;