import React from 'react';
import { Users, TrendingUp, Hash, ExternalLink } from 'lucide-react';

const InfluencerCard = ({ influencer, showSimilarityScore = false }) => {
  const {
    handle,
    bio,
    follower_count,
    engagement_rate,
    niche_tags,
    profile_pic_url,
    similarity_score
  } = influencer;

  // Format follower count for display
  const formatFollowerCount = (count) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  // Parse niche tags
  const tags = niche_tags ? niche_tags.split(',').filter(tag => tag.trim()) : [];

  // Get similarity color based on score
  const getSimilarityColor = (score) => {
    if (score >= 0.9) return 'bg-green-500';
    if (score >= 0.8) return 'bg-blue-500';
    if (score >= 0.7) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  return (
    <div className="card p-6 hover:shadow-lg transition-all duration-300 animate-slide-up">
      {/* Header with profile info */}
      <div className="flex items-start space-x-4 mb-4">
        {/* Profile Picture */}
        <div className="relative flex-shrink-0">
          {profile_pic_url ? (
            <img
              src={profile_pic_url}
              alt={`${handle} profile`}
              className="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
              onError={(e) => {
                e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(handle)}&background=random&color=fff&size=64`;
              }}
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-lg">
              {handle.charAt(0).toUpperCase()}
            </div>
          )}
          
          {/* Similarity score badge */}
          {showSimilarityScore && similarity_score && (
            <div className="absolute -top-2 -right-2 bg-white rounded-full p-1 shadow-md">
              <div className={`w-6 h-6 rounded-full ${getSimilarityColor(similarity_score)} flex items-center justify-center`}>
                <span className="text-xs font-bold text-white">
                  {Math.round(similarity_score * 100)}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Profile Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              @{handle}
            </h3>
            <ExternalLink className="w-4 h-4 text-gray-400 hover:text-primary-600 cursor-pointer transition-colors" />
          </div>
          
          {/* Stats */}
          <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4" />
              <span className="font-medium">{formatFollowerCount(follower_count)}</span>
            </div>
            
            {engagement_rate > 0 && (
              <div className="flex items-center space-x-1">
                <TrendingUp className="w-4 h-4" />
                <span className="font-medium">{engagement_rate.toFixed(1)}%</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bio */}
      {bio && (
        <div className="mb-4">
          <p className="text-gray-700 text-sm leading-relaxed line-clamp-3">
            {bio}
          </p>
        </div>
      )}

      {/* Niche Tags */}
      {tags.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200"
              >
                <Hash className="w-3 h-3 mr-1" />
                {tag.trim()}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                +{tags.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Similarity Score Bar */}
      {showSimilarityScore && similarity_score && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Similarity</span>
            <span className="text-sm font-bold text-primary-600">
              {Math.round(similarity_score * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full similarity-bar transition-all duration-500"
              style={{ width: `${similarity_score * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex space-x-2">
          <button className="flex-1 btn-primary text-sm py-2">
            View Profile
          </button>
          <button className="btn-secondary text-sm py-2 px-3">
            <Users className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InfluencerCard;