import axios from 'axios';

// API base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens (future implementation)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface Contact {
  id: number;
  full_name: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  title?: string;
  company_name?: string;
  company_domain?: string;
  linkedin_url?: string;
  contact_grade?: 'A' | 'B' | 'C' | 'D' | 'F';
  prospect_score?: number;
  data_quality_score?: number;
  decision_maker_score?: number;
  enrichment_status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  company?: Company;
}

export interface Company {
  id: number;
  name: string;
  domain?: string;
  industry?: string;
  employee_count?: number;
  headquarters_location?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: 'active' | 'paused' | 'completed' | 'archived';
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface Signal {
  id: number;
  company_id: number;
  signal_type: string;
  title: string;
  description?: string;
  source: string;
  source_url?: string;
  relevance_score: number;
  impact_score: number;
  timing_score: number;
  signal_date: string;
  detected_at: string;
  company?: Company;
}

export interface Task {
  id: number;
  contact_id: number;
  title: string;
  description?: string;
  channel: 'email' | 'linkedin' | 'phone' | 'direct_mail';
  priority: number;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  recommended_date?: string;
  due_date?: string;
  completed_date?: string;
  created_at: string;
  updated_at: string;
  contact?: Contact;
}

export interface UploadBatch {
  id: number;
  project_id: number;
  filename: string;
  total_records: number;
  processed_records: number;
  successful_records: number;
  failed_records: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
}

// API functions
export const projectsApi = {
  getAll: () => api.get<Project[]>('/projects'),
  getById: (id: number) => api.get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) => api.post<Project>('/projects', data),
  update: (id: number, data: Partial<Project>) => api.put<Project>(`/projects/${id}`, data),
  delete: (id: number) => api.delete(`/projects/${id}`),
  getStats: (id: number) => api.get(`/projects/${id}/stats`),
};

export const contactsApi = {
  getAll: (params?: any) => api.get<Contact[]>('/contacts', { params }),
  getById: (id: number) => api.get<Contact>(`/contacts/${id}`),
  create: (data: Partial<Contact>) => api.post<Contact>('/contacts', data),
  update: (id: number, data: Partial<Contact>) => api.put<Contact>(`/contacts/${id}`, data),
  delete: (id: number) => api.delete(`/contacts/${id}`),
  enrich: (id: number) => api.post(`/contacts/${id}/enrich`),
  score: (id: number) => api.post(`/contacts/${id}/score`),
  bulkEnrich: (contactIds: number[]) => api.post('/contacts/bulk-enrich', { contact_ids: contactIds }),
  getTopProspects: (projectId: number, limit = 10) => 
    api.get<Contact[]>(`/contacts/project/${projectId}/top-prospects`, { params: { limit } }),
};

export const companiesApi = {
  getAll: (params?: any) => api.get<Company[]>('/companies', { params }),
  getById: (id: number) => api.get<Company>(`/companies/${id}`),
  create: (data: Partial<Company>) => api.post<Company>('/companies', data),
  update: (id: number, data: Partial<Company>) => api.put<Company>(`/companies/${id}`, data),
  delete: (id: number) => api.delete(`/companies/${id}`),
  getContacts: (id: number, params?: any) => api.get<Contact[]>(`/companies/${id}/contacts`, { params }),
  getSignals: (id: number, params?: any) => api.get<Signal[]>(`/companies/${id}/signals`, { params }),
  enrich: (id: number) => api.post(`/companies/${id}/enrich`),
  detectSignals: (id: number) => api.post(`/companies/${id}/detect-signals`),
  searchByDomain: (domain: string) => api.get(`/companies/search/domain/${domain}`),
};

export const signalsApi = {
  getAll: (params?: any) => api.get<Signal[]>('/signals', { params }),
  getById: (id: number) => api.get<Signal>(`/signals/${id}`),
  create: (data: Partial<Signal>) => api.post<Signal>('/signals', data),
  delete: (id: number) => api.delete(`/signals/${id}`),
  getTrendingTypes: (daysBack = 7) => api.get(`/signals/trending/types`, { params: { days_back: daysBack } }),
  getRecentHighImpact: (params?: any) => api.get<Signal[]>('/signals/recent/high-impact', { params }),
  getDashboardSummary: (daysBack = 7) => api.get(`/signals/dashboard/summary`, { params: { days_back: daysBack } }),
};

export const tasksApi = {
  getAll: (params?: any) => api.get<Task[]>('/tasks', { params }),
  getById: (id: number) => api.get<Task>(`/tasks/${id}`),
  create: (data: Partial<Task>) => api.post<Task>('/tasks', data),
  update: (id: number, data: Partial<Task>) => api.put<Task>(`/tasks/${id}`, data),
  delete: (id: number) => api.delete(`/tasks/${id}`),
  complete: (id: number) => api.post<Task>(`/tasks/${id}/complete`),
  generateForContact: (contactId: number) => api.post(`/tasks/contact/${contactId}/generate`),
  getPendingForProject: (projectId: number, limit = 50) => 
    api.get<Task[]>(`/tasks/project/${projectId}/pending`, { params: { limit } }),
  getDashboardStats: (params?: any) => api.get('/tasks/dashboard/stats', { params }),
  getTodaysTasks: (params?: any) => api.get<Task[]>('/tasks/upcoming/today', { params }),
};

export const uploadApi = {
  uploadCsv: (file: File, projectId: number) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId.toString());
    
    return api.post('/upload/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getBatch: (batchId: number) => api.get<UploadBatch>(`/upload/batches/${batchId}`),
  getProjectBatches: (projectId: number, params?: any) => 
    api.get<UploadBatch[]>(`/upload/batches/project/${projectId}`, { params }),
  deleteBatch: (batchId: number) => api.delete(`/upload/batches/${batchId}`),
};

export const dashboardApi = {
  getProjectDashboard: (projectId: number) => api.get(`/dashboard/project/${projectId}`),
  getOverview: (params?: any) => api.get('/dashboard/overview', { params }),
  getRecentActivity: (params?: any) => api.get('/dashboard/activity/recent', { params }),
  getTrendMetrics: (params?: any) => api.get('/dashboard/metrics/trends', { params }),
  getProspectLeaderboard: (params?: any) => api.get('/dashboard/leaderboard/prospects', { params }),
};