import axios from 'axios';

// Replace with your FastAPI backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the JWT token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken'); // Or sessionStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration/invalidity
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If the error is 401 Unauthorized and not from the /token endpoint itself,
    // it likely means the token is expired or invalid.
    if (error.response && error.response.status === 401 && error.config.url !== '/token') {
      console.error('Unauthorized request. Token might be expired or invalid. Redirecting to login...');
      // Clear token and redirect to login
      localStorage.removeItem('accessToken');
      // Using window.location for simplicity, but in a real app,
      // you might use a router navigation for smoother UX.
      window.location.href = '/login'; 
    }
    return Promise.reject(error);
  }
);

export default api;