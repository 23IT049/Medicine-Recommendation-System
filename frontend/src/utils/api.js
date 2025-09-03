import axios from 'axios';

// Create axios instance with default config
export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  timeout: 30000, // Increase timeout to 30 seconds to prevent connection issues
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 errors globally
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ML Prediction API
export const mlApi = {
  predict: async (symptoms, isAuthenticated = false) => {
    const endpoint = isAuthenticated ? '/ml/predict-authenticated' : '/ml/predict';
    const response = await api.post(endpoint, { symptoms });
    return response.data;
  },

  getSymptoms: async () => {
    const response = await api.get('/ml/symptoms/list');
    return response.data;
  },

  searchSymptoms: async (query, limit = 10) => {
    const response = await api.get(`/ml/symptoms/search?q=${query}&limit=${limit}`);
    return response.data;
  },

  getDiseases: async () => {
    const response = await api.get('/ml/diseases/list');
    return response.data;
  },

  validateSymptoms: async (symptoms) => {
    const response = await api.post('/ml/validate-symptoms', { symptoms });
    return response.data;
  },

  getModelInfo: async () => {
    const response = await api.get('/ml/model/info');
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/ml/health');
    return response.data;
  },
};

// Auth API
export const authApi = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  demoLogin: async () => {
    const response = await api.post('/auth/demo-login', {
      email: 'demo@medicine.com',
      password: 'demo123'
    });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/auth/profile', userData);
    return response.data;
  },

  validateToken: async () => {
    const response = await api.get('/auth/validate-token');
    return response.data;
  },
};

// Health API
export const healthApi = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
