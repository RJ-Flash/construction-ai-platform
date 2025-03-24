// API Configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: `${API_URL}/auth/login`,
    REGISTER: `${API_URL}/auth/register`,
    LOGOUT: `${API_URL}/auth/logout`,
    REFRESH: `${API_URL}/auth/refresh`,
    PROFILE: `${API_URL}/auth/profile`
  },
  
  // Projects endpoints
  PROJECTS: {
    LIST: `${API_URL}/projects`,
    CREATE: `${API_URL}/projects`,
    DETAILS: (id) => `${API_URL}/projects/${id}`,
    UPDATE: (id) => `${API_URL}/projects/${id}`,
    DELETE: (id) => `${API_URL}/projects/${id}`,
    DOCUMENTS: (id) => `${API_URL}/projects/${id}/documents`,
    ELEMENTS: (id) => `${API_URL}/projects/${id}/elements`,
    QUOTES: (id) => `${API_URL}/projects/${id}/quotes`,
    STATS: (id) => `${API_URL}/projects/${id}/stats`
  },
  
  // Documents endpoints
  DOCUMENTS: {
    LIST: `${API_URL}/documents`,
    UPLOAD: `${API_URL}/documents/upload`,
    DETAILS: (id) => `${API_URL}/documents/${id}`,
    DELETE: (id) => `${API_URL}/documents/${id}`,
    ANALYZE: `${API_URL}/documents/analyze`,
    ELEMENTS: (id) => `${API_URL}/documents/${id}/elements`
  },
  
  // Elements endpoints
  ELEMENTS: {
    LIST: `${API_URL}/elements`,
    CREATE: `${API_URL}/elements`,
    DETAILS: (id) => `${API_URL}/elements/${id}`,
    UPDATE: (id) => `${API_URL}/elements/${id}`,
    DELETE: (id) => `${API_URL}/elements/${id}`,
    RELATED: (id) => `${API_URL}/elements/${id}/related`
  },
  
  // Quotes endpoints
  QUOTES: {
    LIST: `${API_URL}/quotes`,
    CREATE: `${API_URL}/quotes`,
    DETAILS: (id) => `${API_URL}/quotes/${id}`,
    UPDATE: (id) => `${API_URL}/quotes/${id}`,
    DELETE: (id) => `${API_URL}/quotes/${id}`,
    UPDATE_STATUS: (id) => `${API_URL}/quotes/${id}/status`,
    PDF: (id) => `${API_URL}/quotes/${id}/pdf`
  },
  
  // Users endpoints
  USERS: {
    LIST: `${API_URL}/users`,
    DETAILS: (id) => `${API_URL}/users/${id}`,
    UPDATE: (id) => `${API_URL}/users/${id}`,
    DELETE: (id) => `${API_URL}/users/${id}`
  },
  
  // Settings endpoints
  SETTINGS: {
    GENERAL: `${API_URL}/settings/general`,
    ORGANIZATION: `${API_URL}/settings/organization`,
    PRICING: `${API_URL}/settings/pricing`
  }
};

export default ENDPOINTS;