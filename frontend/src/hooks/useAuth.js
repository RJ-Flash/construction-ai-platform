import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';

// Create context
const AuthContext = createContext();

// Authentication provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        // Fetch user profile
        const response = await axios.get(ENDPOINTS.AUTH.PROFILE, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Authentication error:', err);
        
        // Remove invalid token
        localStorage.removeItem('token');
        
        setError('Authentication failed. Please login again.');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      setLoading(true);
      
      // Request login
      const response = await axios.post(ENDPOINTS.AUTH.LOGIN, {
        username: email, // FastAPI OAuth2 expects 'username'
        password
      });
      
      // Save token
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      
      // Fetch user profile
      const userResponse = await axios.get(ENDPOINTS.AUTH.PROFILE, {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });
      
      setUser(userResponse.data);
      setIsAuthenticated(true);
      setError(null);
      
      return true;
    } catch (err) {
      console.error('Login error:', err);
      
      let errorMessage = 'Login failed';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMessage = err.response.data.detail;
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      setLoading(true);
      
      // Request registration
      await axios.post(ENDPOINTS.AUTH.REGISTER, userData);
      
      // Log in with new credentials
      return await login(userData.email, userData.password);
    } catch (err) {
      console.error('Registration error:', err);
      
      let errorMessage = 'Registration failed';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMessage = err.response.data.detail;
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  // Update user profile
  const updateProfile = async (userData) => {
    try {
      setLoading(true);
      
      const response = await axios.put(ENDPOINTS.AUTH.PROFILE, userData);
      
      setUser(response.data);
      return true;
    } catch (err) {
      console.error('Profile update error:', err);
      
      let errorMessage = 'Failed to update profile';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMessage = err.response.data.detail;
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Clear error
  const clearError = () => {
    setError(null);
  };

  // Context value
  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    clearError
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
