import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Sparkles, Users, TrendingUp, Hash } from 'lucide-react';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const SearchPage = () => {
  const navigate = useNavigate();
  const [searchType, setSearchType] = useState('handle'); // 'handle' or 'bio'
  const [searchValue, setSearchValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Add influencer form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [addFormData, setAddFormData] = useState({
    handle: '',
    bio: '',
    captions: '',
    follower_count: '',
    engagement_rate: '',
    niche_tags: '',
    profile_pic_url: ''
  });

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchValue.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const searchData = {
        top_k: 10
      };

      if (searchType === 'handle') {
        searchData.seed_handle = searchValue.replace('@', '');
      } else {
        searchData.seed_bio = searchValue;
      }

      const results = await apiService.findLookalikes(searchData);
      
      // Navigate to results page with data
      navigate('/results', { 
        state: { 
          results,
          searchQuery: searchValue,
          searchType 
        } 
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddInfluencer = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const influencerData = {
        handle: addFormData.handle.replace('@', ''),
        bio: addFormData.bio || null,
        captions: addFormData.captions ? addFormData.captions.split('\\n').filter(c => c.trim()) : [],
        follower_count: parseInt(addFormData.follower_count) || 0,
        engagement_rate: parseFloat(addFormData.engagement_rate) || 0.0,
        niche_tags: addFormData.niche_tags ? addFormData.niche_tags.split(',').map(t => t.trim()).filter(t => t) : [],
        profile_pic_url: addFormData.profile_pic_url || null
      };

      await apiService.addInfluencer(influencerData);
      
      // Reset form and show success
      setAddFormData({
        handle: '',
        bio: '',
        captions: '',
        follower_count: '',
        engagement_rate: '',
        niche_tags: '',
        profile_pic_url: ''
      });
      setShowAddForm(false);
      
      // Optionally show success message
      alert(`Successfully added influencer @${influencerData.handle}!`);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner size="xl" text="Processing your request..." />;
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl mb-6">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Find Your Perfect Influencer Match
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Discover similar influencers using AI-powered embeddings. Search by handle or describe your ideal influencer profile.
        </p>

        {/* Feature highlights */}
        <div className="flex justify-center space-x-8 mb-12">
          <div className="flex items-center space-x-2 text-gray-600">
            <Users className="w-5 h-5 text-primary-600" />
            <span className="text-sm font-medium">AI-Powered Matching</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-600">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <span className="text-sm font-medium">Real-time Results</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-600">
            <Hash className="w-5 h-5 text-primary-600" />
            <span className="text-sm font-medium">Niche Filtering</span>
          </div>
        </div>
      </div>

      {/* Search Form */}
      <div className="card p-8 mb-8">
        <form onSubmit={handleSearch} className="space-y-6">
          {/* Search Type Toggle */}
          <div className="flex justify-center">
            <div className="bg-gray-100 p-1 rounded-lg inline-flex">
              <button
                type="button"
                onClick={() => setSearchType('handle')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  searchType === 'handle'
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Search by Handle
              </button>
              <button
                type="button"
                onClick={() => setSearchType('bio')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  searchType === 'bio'
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Search by Description
              </button>
            </div>
          </div>

          {/* Search Input */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            
            {searchType === 'handle' ? (
              <input
                type="text"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Enter influencer handle (e.g., @username)"
                className="input-primary pl-10 text-lg h-14"
                required
              />
            ) : (
              <textarea
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Describe your ideal influencer (e.g., 'fitness enthusiast who posts workout routines and nutrition tips')"
                className="input-primary pl-10 text-lg min-h-[100px] pt-4"
                required
              />
            )}
          </div>

          {/* Search Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={!searchValue.trim() || isLoading}
              className="btn-primary px-8 py-3 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Search className="w-5 h-5 mr-2" />
              Find Lookalikes
            </button>
          </div>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-8">
          <ErrorMessage
            title="Search Failed"
            message={error}
            onRetry={() => setError(null)}
          />
        </div>
      )}

      {/* Add Influencer Section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Add New Influencer</h2>
            <p className="text-gray-600 text-sm">Expand the database with new influencer profiles</p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>{showAddForm ? 'Cancel' : 'Add Influencer'}</span>
          </button>
        </div>

        {showAddForm && (
          <form onSubmit={handleAddInfluencer} className="space-y-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Handle *
                </label>
                <input
                  type="text"
                  value={addFormData.handle}
                  onChange={(e) => setAddFormData({...addFormData, handle: e.target.value})}
                  placeholder="username (without @)"
                  className="input-primary"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Profile Picture URL
                </label>
                <input
                  type="url"
                  value={addFormData.profile_pic_url}
                  onChange={(e) => setAddFormData({...addFormData, profile_pic_url: e.target.value})}
                  placeholder="https://..."
                  className="input-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bio
              </label>
              <textarea
                value={addFormData.bio}
                onChange={(e) => setAddFormData({...addFormData, bio: e.target.value})}
                placeholder="Influencer bio/description"
                className="input-primary min-h-[80px]"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sample Captions
              </label>
              <textarea
                value={addFormData.captions}
                onChange={(e) => setAddFormData({...addFormData, captions: e.target.value})}
                placeholder="Sample post captions (separate with \\n)"
                className="input-primary min-h-[80px]"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Follower Count
                </label>
                <input
                  type="number"
                  value={addFormData.follower_count}
                  onChange={(e) => setAddFormData({...addFormData, follower_count: e.target.value})}
                  placeholder="0"
                  className="input-primary"
                  min="0"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Engagement Rate (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={addFormData.engagement_rate}
                  onChange={(e) => setAddFormData({...addFormData, engagement_rate: e.target.value})}
                  placeholder="0.0"
                  className="input-primary"
                  min="0"
                  max="100"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Niche Tags
                </label>
                <input
                  type="text"
                  value={addFormData.niche_tags}
                  onChange={(e) => setAddFormData({...addFormData, niche_tags: e.target.value})}
                  placeholder="fitness, lifestyle, tech"
                  className="input-primary"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!addFormData.handle.trim() || isLoading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Influencer
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default SearchPage;