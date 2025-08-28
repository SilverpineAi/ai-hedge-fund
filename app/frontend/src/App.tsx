import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './providers/ThemeProvider';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { ProjectDetail } from './pages/ProjectDetail';
import { Contacts } from './pages/Contacts';
import { Companies } from './pages/Companies';
import { Signals } from './pages/Signals';
import { Tasks } from './pages/Tasks';
import { Upload } from './pages/Upload';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="sales-intelligence-theme">
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/projects/:projectId" element={<ProjectDetail />} />
              <Route path="/contacts" element={<Contacts />} />
              <Route path="/companies" element={<Companies />} />
              <Route path="/signals" element={<Signals />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/upload" element={<Upload />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}