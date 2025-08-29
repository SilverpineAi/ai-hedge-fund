import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Users, Zap } from 'lucide-react';

const Header = () => {
  const location = useLocation();
  
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Influencer Lookalike</h1>
              <p className="text-xs text-gray-500 -mt-1">AI-Powered Discovery</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                location.pathname === '/'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Search className="w-4 h-4" />
              <span className="font-medium">Search</span>
            </Link>
            
            <div className="flex items-center space-x-2 px-3 py-2 text-gray-500">
              <Users className="w-4 h-4" />
              <span className="text-sm">Find Lookalikes</span>
            </div>
          </nav>

          {/* Mobile menu button */}
          <button className="md:hidden p-2 rounded-lg hover:bg-gray-100">
            <Search className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;