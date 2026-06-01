import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Return the response data if available, so we can access the custom envelope
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data);
    }
    // Generic fallback for network errors etc
    return Promise.reject({
      success: false,
      message: 'Network error or server unavailable',
      error_code: 'NETWORK_ERROR'
    });
  }
);

export default api;
