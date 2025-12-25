import axios from 'axios';
import { getAccessToken, getRefreshToken, setTokens, clearTokens, isTokenExpired } from '../utils/token';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    let token = getAccessToken();

    if (token && isTokenExpired(token)) {
      // Try to refresh token
      const refreshToken = getRefreshToken();
      if (refreshToken && !isTokenExpired(refreshToken)) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = response.data;
          setTokens(access_token, refresh_token);
          token = access_token;
        } catch {
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(new Error('Session expired'));
        }
      } else {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(new Error('Session expired'));
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearTokens();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
