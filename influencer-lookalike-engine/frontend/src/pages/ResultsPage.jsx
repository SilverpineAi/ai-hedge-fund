import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Filter, SortDesc, Search, Users, TrendingUp } from 'lucide-react';
import InfluencerCard from '../components/InfluencerCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [results, setResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);
  const [queryInfo, setQueryInfo] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Filter states
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    minFollowers: '',
    maxFollowers: '',
    minEngagement: '',
    sortBy: 'similarity' // 'similarity', 'followers', 'engagement'
  });

  useEffect(() => {
    // Get data from navigation state
    if (location.state?.results) {
      const { results: searchResults, searchQuery, searchType } = location.state;
      setResults(searchResults.results || []);
      setQueryInfo({
        ...searchResults.query_info,
        searchQuery,
        searchType,
        totalResults: searchResults.total_results
      });
    } else {
      // Redirect to search page if no data
      navigate('/');
    }
  }, [location.state, navigate]);

  useEffect(() => {
    // Apply filters and sorting
    let filtered = [...results];

    // Apply follower count filters
    if (filters.minFollowers) {
      filtered = filtered.filter(inf => inf.follower_count >= parseInt(filters.minFollowers));
    }
    if (filters.maxFollowers) {
      filtered = filtered.filter(inf => inf.follower_count <= parseInt(filters.maxFollowers));
    }

    // Apply engagement rate filter
    if (filters.minEngagement) {
      filtered = filtered.filter(inf => inf.engagement_rate >= parseFloat(filters.minEngagement));
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'followers':
          return b.follower_count - a.follower_count;
        case 'engagement':
          return b.engagement_rate - a.engagement_rate;
        case 'similarity':
        default:
          return (b.similarity_score || 0) - (a.similarity_score || 0);
      }
    });

    setFilteredResults(filtered);
  }, [results, filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      minFollowers: '',
      maxFollowers: '',
      minEngagement: '',
      sortBy: 'similarity'
    });
  };

  const formatFollowerCount = (count) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  if (isLoading) {
    return <LoadingSpinner size="xl" text="Finding similar influencers..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Search Failed"
        message={error}
        onRetry={() => navigate('/')}
      />
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Link
            to="/"
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Search</span>
          </Link>
          
          <div className="h-6 w-px bg-gray-300"></div>
          
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Lookalike Results
            </h1>
            <p className="text-gray-600 text-sm">
              {queryInfo.searchType === 'handle' 
                ? `Similar to @${queryInfo.seed_handle}`
                : 'Based on your description'
              }
            </p>
          </div>
        </div>

        {/* Results count and filters */}
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            <span className="font-medium">{filteredResults.length}</span> of{' '}
            <span className="font-medium">{results.length}</span> results
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center space-x-2 ${
              showFilters ? 'bg-primary-50 text-primary-700 border-primary-200' : ''
            }`}
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Query Info */}
      {queryInfo.seed_bio && (
        <div className="card p-4 mb-6 bg-primary-50 border-primary-200">
          <div className="flex items-start space-x-3">
            <Search className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-medium text-primary-900 mb-1">Search Query</h3>
              <p className="text-primary-700 text-sm">{queryInfo.seed_bio}</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters Panel */}
      {showFilters && (
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Filters & Sorting</h3>
            <button
              onClick={clearFilters}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear All
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Follower Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Followers
              </label>
              <input
                type="number"
                value={filters.minFollowers}
                onChange={(e) => handleFilterChange('minFollowers', e.target.value)}
                placeholder="e.g., 10000"
                className="input-primary"
                min="0"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Followers
              </label>
              <input
                type="number"
                value={filters.maxFollowers}
                onChange={(e) => handleFilterChange('maxFollowers', e.target.value)}
                placeholder="e.g., 1000000"
                className="input-primary"
                min="0"
              />
            </div>
            
            {/* Engagement Rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Engagement (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={filters.minEngagement}
                onChange={(e) => handleFilterChange('minEngagement', e.target.value)}
                placeholder="e.g., 2.5"
                className="input-primary"
                min="0"
                max="100"
              />
            </div>
            
            {/* Sort By */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="input-primary"
              >
                <option value="similarity">Similarity Score</option>
                <option value="followers">Follower Count</option>
                <option value="engagement">Engagement Rate</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Results Grid */}
      {filteredResults.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredResults.map((influencer, index) => (
            <InfluencerCard
              key={influencer.id || index}
              influencer={influencer}
              showSimilarityScore={true}
            />
          ))}
        </div>
      ) : results.length > 0 ? (
        // No results after filtering
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Filter className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No results match your filters
          </h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your filter criteria to see more results.
          </p>
          <button
            onClick={clearFilters}
            className="btn-primary"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        // No results at all
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No similar influencers found
          </h3>
          <p className="text-gray-600 mb-4">
            Try searching with a different handle or description.
          </p>
          <Link to="/" className="btn-primary">
            Try Another Search
          </Link>
        </div>
      )}

      {/* Summary Stats */}
      {filteredResults.length > 0 && (
        <div className="mt-12 pt-8 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card p-4 text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mx-auto mb-2">
                <Users className="w-6 h-6 text-primary-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {formatFollowerCount(
                  Math.round(filteredResults.reduce((sum, inf) => sum + inf.follower_count, 0) / filteredResults.length)
                )}
              </div>
              <div className="text-sm text-gray-600">Avg. Followers</div>
            </div>
            
            <div className="card p-4 text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-2">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {(filteredResults.reduce((sum, inf) => sum + inf.engagement_rate, 0) / filteredResults.length).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Avg. Engagement</div>
            </div>
            
            <div className="card p-4 text-center">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-2">
                <SortDesc className="w-6 h-6 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {Math.round((filteredResults.reduce((sum, inf) => sum + (inf.similarity_score || 0), 0) / filteredResults.length) * 100)}%
              </div>
              <div className="text-sm text-gray-600">Avg. Similarity</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;