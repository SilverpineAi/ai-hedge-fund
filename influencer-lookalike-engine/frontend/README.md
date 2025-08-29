# Frontend Application

React frontend for the Influencer Lookalike Engine with modern UI and responsive design.

## 🏗️ Architecture

```
React Application
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.jsx       # Navigation header
│   │   ├── InfluencerCard.jsx  # Influencer display card
│   │   ├── LoadingSpinner.jsx  # Loading states
│   │   └── ErrorMessage.jsx    # Error handling
│   ├── pages/              # Main application pages
│   │   ├── SearchPage.jsx   # Search and add influencers
│   │   └── ResultsPage.jsx  # Display search results
│   ├── services/           # API communication
│   │   └── api.js          # Backend API service
│   ├── App.js              # Main application component
│   ├── index.js            # Application entry point
│   └── index.css           # Global styles with Tailwind
└── public/                 # Static assets
```

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Docker Development

```bash
# Development with hot reloading
docker-compose -f docker-compose.dev.yml up frontend

# Production build
docker build -t influencer-frontend .
docker run -p 3000:80 influencer-frontend
```

## 🎨 UI Components

### Header Component
- **Navigation**: Search and results navigation
- **Branding**: Logo and application title
- **Responsive**: Mobile-friendly hamburger menu

### InfluencerCard Component
```jsx
<InfluencerCard 
  influencer={influencerData}
  showSimilarityScore={true}
/>
```

**Features:**
- Profile picture with fallback avatar
- Follower count formatting (1K, 1M)
- Engagement rate display
- Niche tags with hashtags
- Similarity score visualization
- Action buttons for profile viewing

### LoadingSpinner Component
```jsx
<LoadingSpinner 
  size="lg" 
  text="Finding similar influencers..." 
/>
```

### ErrorMessage Component
```jsx
<ErrorMessage
  title="Search Failed"
  message="Unable to connect to server"
  onRetry={() => handleRetry()}
/>
```

## 📱 Pages

### SearchPage (`/`)

**Features:**
- **Dual Search Mode**: Search by handle or description
- **Add Influencer Form**: Expandable form to add new influencers
- **Input Validation**: Real-time validation and error handling
- **Loading States**: Smooth loading indicators during API calls

**Form Fields:**
- Handle (required)
- Bio text
- Sample captions
- Follower count
- Engagement rate
- Niche tags
- Profile picture URL

### ResultsPage (`/results`)

**Features:**
- **Results Grid**: Responsive card layout
- **Advanced Filters**: Follower range, engagement rate, sorting
- **Summary Statistics**: Average metrics across results
- **Similarity Scoring**: Visual similarity indicators
- **Empty States**: Helpful messages when no results found

**Filters:**
- Minimum/Maximum followers
- Minimum engagement rate
- Sort by similarity, followers, or engagement

## 🎨 Styling & Design

### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        }
      }
    }
  }
}
```

### Custom CSS Classes

```css
/* Utility classes in index.css */
.btn-primary {
  @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
}

.card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200;
}

.input-primary {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500;
}
```

### Responsive Design

- **Mobile First**: Designed for mobile devices
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Grid Layouts**: Responsive grid that adapts to screen size
- **Touch Friendly**: Large touch targets for mobile interaction

## 🔌 API Integration

### API Service (`services/api.js`)

```javascript
import { apiService } from './services/api';

// Add influencer
const result = await apiService.addInfluencer(influencerData);

// Find lookalikes
const results = await apiService.findLookalikes({
  seed_handle: 'username',
  top_k: 10
});

// Health check
const health = await apiService.checkHealth();
```

**Features:**
- **Axios Instance**: Pre-configured with base URL and headers
- **Error Handling**: Automatic error parsing and user-friendly messages
- **Request/Response Logging**: Debug information in development
- **Timeout Handling**: 30-second timeout for all requests

### Error Handling

```javascript
try {
  const results = await apiService.findLookalikes(searchData);
  navigate('/results', { state: { results } });
} catch (error) {
  setError(error.message); // User-friendly error message
}
```

## 🚀 State Management

### React Hooks Usage

```javascript
// Search page state
const [searchType, setSearchType] = useState('handle');
const [searchValue, setSearchValue] = useState('');
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);

// Results page state  
const [results, setResults] = useState([]);
const [filteredResults, setFilteredResults] = useState([]);
const [filters, setFilters] = useState({
  minFollowers: '',
  maxFollowers: '',
  minEngagement: '',
  sortBy: 'similarity'
});
```

### Navigation State

```javascript
// Pass data between pages
navigate('/results', { 
  state: { 
    results,
    searchQuery: searchValue,
    searchType 
  } 
});

// Access navigation state
const location = useLocation();
const { results, searchQuery } = location.state || {};
```

## 🧪 Testing

### Component Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### Example Test
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import SearchPage from '../pages/SearchPage';

test('renders search form', () => {
  render(<SearchPage />);
  
  const searchInput = screen.getByPlaceholderText(/enter influencer handle/i);
  const searchButton = screen.getByText(/find lookalikes/i);
  
  expect(searchInput).toBeInTheDocument();
  expect(searchButton).toBeInTheDocument();
});

test('switches between search modes', () => {
  render(<SearchPage />);
  
  const bioSearchButton = screen.getByText(/search by description/i);
  fireEvent.click(bioSearchButton);
  
  const textarea = screen.getByPlaceholderText(/describe your ideal influencer/i);
  expect(textarea).toBeInTheDocument();
});
```

## 🎯 Performance Optimization

### Code Splitting

```javascript
// Lazy load pages
const SearchPage = lazy(() => import('./pages/SearchPage'));
const ResultsPage = lazy(() => import('./pages/ResultsPage'));

// Wrap with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<SearchPage />} />
    <Route path="/results" element={<ResultsPage />} />
  </Routes>
</Suspense>
```

### Image Optimization

```javascript
// Fallback avatars for missing profile pictures
const handleImageError = (e) => {
  e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(handle)}&background=random`;
};

<img
  src={profile_pic_url}
  alt={`${handle} profile`}
  onError={handleImageError}
  className="w-16 h-16 rounded-full object-cover"
/>
```

### Debounced Search

```javascript
import { useDebounce } from 'use-debounce';

const [searchValue, setSearchValue] = useState('');
const [debouncedValue] = useDebounce(searchValue, 500);

useEffect(() => {
  if (debouncedValue) {
    performSearch(debouncedValue);
  }
}, [debouncedValue]);
```

## 🔧 Configuration

### Environment Variables

```bash
# .env.local
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=false
REACT_APP_VERSION=1.0.0
```

### Build Configuration

```javascript
// package.json build scripts
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "build:analyze": "npm run build && npx bundle-analyzer build/static/js/*.js",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

## 🚀 Deployment

### Production Build

```bash
# Create optimized production build
npm run build

# Serve static files
npx serve -s build -l 3000
```

### Docker Production

```dockerfile
# Multi-stage build for optimized image
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
# nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/;
    }

    # Static file caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Error**
   ```
   Network Error: Unable to connect to backend
   ```
   - Check backend is running on port 8000
   - Verify REACT_APP_API_URL environment variable
   - Check CORS configuration in backend

2. **Build Errors**
   ```
   Module not found: Can't resolve 'component'
   ```
   - Check import paths are correct
   - Ensure all dependencies are installed
   - Clear node_modules and reinstall

3. **Styling Issues**
   ```
   Tailwind classes not applying
   ```
   - Verify tailwind.config.js content paths
   - Check @tailwind directives in index.css
   - Restart development server

### Debug Mode

```javascript
// Enable debug logging
if (process.env.REACT_APP_DEBUG === 'true') {
  console.log('Debug mode enabled');
  // Additional debug information
}
```

## 📱 Mobile Optimization

### Touch Interactions

```css
/* Touch-friendly button sizing */
.btn-touch {
  min-height: 44px;
  min-width: 44px;
}

/* Prevent zoom on input focus (iOS) */
input[type="text"], textarea {
  font-size: 16px;
}
```

### Responsive Images

```javascript
// Responsive profile pictures
<img
  src={profile_pic_url}
  alt={`${handle} profile`}
  className="w-12 h-12 sm:w-16 sm:h-16 rounded-full object-cover"
  loading="lazy"
/>
```

### Mobile Navigation

```javascript
// Mobile-friendly header
const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

return (
  <header className="bg-white shadow-sm">
    <div className="container mx-auto px-4">
      <div className="flex items-center justify-between h-16">
        <Logo />
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex">
          <NavigationLinks />
        </nav>
        
        {/* Mobile Menu Button */}
        <button 
          className="md:hidden"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          <Menu />
        </button>
      </div>
    </div>
  </header>
);
```