import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, getRefreshToken, setTokens, clearTokens, isTokenExpired } from '../utils/token';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token refresh state management to prevent race conditions
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

const handleAuthFailure = () => {
  clearTokens();
  window.location.href = '/login';
};

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    let token = getAccessToken();

    if (token && isTokenExpired(token)) {
      const refreshToken = getRefreshToken();

      if (!refreshToken || isTokenExpired(refreshToken)) {
        handleAuthFailure();
        return Promise.reject(new Error('Session expired'));
      }

      if (isRefreshing) {
        // Wait for the ongoing refresh to complete
        return new Promise<InternalAxiosRequestConfig>((resolve, reject) => {
          failedQueue.push({
            resolve: (newToken: string) => {
              config.headers.Authorization = `Bearer ${newToken}`;
              resolve(config);
            },
            reject: (err: Error) => {
              reject(err);
            },
          });
        });
      }

      isRefreshing = true;

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token } = response.data;
        setTokens(access_token, refresh_token);
        token = access_token;
        processQueue(null, access_token);
      } catch (error) {
        const refreshError = error instanceof Error ? error : new Error('Token refresh failed');
        processQueue(refreshError, null);
        handleAuthFailure();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      handleAuthFailure();
    }
    return Promise.reject(error);
  }
);

export default api;
