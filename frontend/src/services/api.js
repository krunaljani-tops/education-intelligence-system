import axios from 'axios';

// Dynamic API base URL resolution:
// 1. Browser custom override in localStorage (if set by user)
// 2. Build-time VITE_API_URL environment variable (if configured in Netlify)
// 3. Fallback to relative '/api' (proxied by Vite locally and by Netlify edge proxy to Render in cloud)
export const getApiBaseUrl = () => {
  const custom = typeof window !== 'undefined' ? localStorage.getItem('edu_api_url') : null;
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/+$/, '');
  }
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/+$/, '');
  }
  return '/api';
};

export const setApiBaseUrl = (url) => {
  if (url && url.trim()) {
    localStorage.setItem('edu_api_url', url.trim().replace(/\/+$/, ''));
  } else {
    localStorage.removeItem('edu_api_url');
  }
};

const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to dynamically attach base URL and JWT token
api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl();
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Response interceptor to handle unauthenticated responses safely
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear invalid credentials without infinite reload loops
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

// ----------------- Auth API -----------------
export const authService = {
  login: async (username, password) => {
    const res = await api.post('/auth/login', { username, password });
    return res.data;
  },
  register: async (userData) => {
    const res = await api.post('/auth/register', userData);
    return res.data;
  },
  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },
  getUsers: async () => {
    const res = await api.get('/auth/users');
    return res.data;
  }
};

// Helper to clean query parameters (removes undefined, null, empty strings)
const cleanParams = (params = {}) => {
  const cleaned = {};
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '' && value !== 'undefined' && value !== 'null') {
      cleaned[key] = value;
    }
  }
  return cleaned;
};

// ----------------- Dashboard API -----------------
export const dashboardService = {
  getOverview: async (filters = {}) => {
    const res = await api.get('/dashboard/overview', { params: cleanParams(filters) });
    return res.data;
  }
};

// ----------------- Students API -----------------
export const studentService = {
  getStudents: async (params = {}) => {
    const res = await api.get('/students', { params: cleanParams(params) });
    return res.data;
  },
  getStudent: async (studentId) => {
    const res = await api.get(`/students/${studentId}`);
    return res.data;
  },
  getStudentPerformance: async (studentId) => {
    const res = await api.get(`/students/${studentId}/performance`);
    return res.data;
  }
};

// ----------------- Enrollments API -----------------
export const enrollmentService = {
  getEnrollments: async (params = {}) => {
    const res = await api.get('/enrollments', { params: cleanParams(params) });
    return res.data;
  },
  getCourseAnalysis: async () => {
    const res = await api.get('/enrollments/course-analysis');
    return res.data;
  }
};

// ----------------- Attendance API -----------------
export const attendanceService = {
  getAttendance: async (params = {}) => {
    const res = await api.get('/attendance', { params: cleanParams(params) });
    return res.data;
  },
  getSummary: async () => {
    const res = await api.get('/attendance/summary');
    return res.data;
  }
};

// ----------------- Assessments API -----------------
export const assessmentService = {
  getAssessments: async (params = {}) => {
    const res = await api.get('/assessments', { params: cleanParams(params) });
    return res.data;
  },
  getSummary: async () => {
    const res = await api.get('/assessments/summary');
    return res.data;
  }
};

// ----------------- Finance API -----------------
export const financeService = {
  getFees: async (params = {}) => {
    const res = await api.get('/fees', { params: cleanParams(params) });
    return res.data;
  },
  getSummary: async () => {
    const res = await api.get('/fees/summary');
    return res.data;
  }
};

// ----------------- Multi-Agent AI API -----------------
export const agentService = {
  triggerAnalysis: async (title = 'Comprehensive Education Intelligence Run') => {
    const res = await api.post(`/agents/analyze?title=${encodeURIComponent(title)}`);
    return res.data;
  },
  getStatus: async (analysisId) => {
    const res = await api.get(`/agents/status/${analysisId}`);
    return res.data;
  },
  getLogs: async (analysisId) => {
    const res = await api.get(`/agents/logs/${analysisId}`);
    return res.data;
  }
};

// ----------------- Chatbot API -----------------
export const chatService = {
  ask: async (query, history = []) => {
    const res = await api.post('/chat/ask', { query, conversation_history: history });
    return res.data;
  }
};

// ----------------- Recommendations & Approvals API -----------------
export const recommendationService = {
  getRecommendations: async (params = {}) => {
    const res = await api.get('/recommendations', { params: cleanParams(params) });
    return res.data;
  },
  approve: async (id, comments = '') => {
    const res = await api.post(`/recommendations/${id}/approve`, { comments });
    return res.data;
  },
  reject: async (id, comments = '') => {
    const res = await api.post(`/recommendations/${id}/reject`, { comments });
    return res.data;
  },
  getHistory: async () => {
    const res = await api.get('/recommendations/history');
    return res.data;
  }
};

// ----------------- Reports API -----------------
export const reportService = {
  generateReport: async (analysisId = null, title = 'Comprehensive Education Intelligence Report') => {
    const res = await api.post('/reports/generate', { analysis_id: analysisId, report_title: title });
    return res.data;
  },
  listReports: async () => {
    const res = await api.get('/reports');
    return res.data;
  },
  getDownloadUrl: (reportId) => {
    return `${getApiBaseUrl()}/reports/${reportId}/download`;
  }
};

// ----------------- Datasets API -----------------
export const datasetService = {
  getValidation: async (filename = null) => {
    const res = await api.get(`/datasets/validation${filename ? `?filename=${filename}` : ''}`);
    return res.data;
  },
  getPreview: async (filename = null) => {
    const res = await api.get(`/datasets/preview${filename ? `?filename=${filename}` : ''}`);
    return res.data;
  },
  importDataset: async (filename = null) => {
    const res = await api.post(`/datasets/import${filename ? `?filename=${filename}` : ''}`);
    return res.data;
  },
  listDatasets: async () => {
    const res = await api.get('/datasets');
    return res.data;
  },
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  }
};

// ----------------- History API -----------------
export const historyService = {
  listHistory: async () => {
    const res = await api.get('/history');
    return res.data;
  },
  getHistoryDetail: async (analysisId) => {
    const res = await api.get(`/history/${analysisId}`);
    return res.data;
  }
};

export default api;
