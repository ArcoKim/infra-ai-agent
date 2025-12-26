import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { AuthState, LoginRequest, RegisterRequest } from '../types/auth';
import { authApi } from '../api/auth';
import { setTokens, clearTokens, getAccessToken, getRefreshToken, isTokenExpired } from '../utils/token';

interface AuthContextType extends AuthState {
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const initAuth = useCallback(async () => {
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();

    if (!accessToken || !refreshToken) {
      setState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    // Check if tokens are valid
    if (isTokenExpired(accessToken) && isTokenExpired(refreshToken)) {
      clearTokens();
      setState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    try {
      const user = await authApi.getCurrentUser();
      setState({
        user,
        accessToken,
        refreshToken,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to restore auth session:', error);
      clearTokens();
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  const login = async (data: LoginRequest) => {
    const response = await authApi.login(data);
    setTokens(response.access_token, response.refresh_token);
    setState({
      user: response.user,
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  const register = async (data: RegisterRequest) => {
    const response = await authApi.register(data);
    setTokens(response.access_token, response.refresh_token);
    setState({
      user: response.user,
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Log but don't block logout on API failure
      console.warn('Logout API call failed:', error);
    }
    clearTokens();
    setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
