// API configuration

// Development API URL
const DEV_API_URL = 'http://localhost:8000';

// Production API URL
const PROD_API_URL = 'https://api.construction-ai-platform.com';

// Use production URL in production environment, development URL otherwise
export const API_BASE_URL = 
  process.env.NODE_ENV === 'production' ? PROD_API_URL : DEV_API_URL;

// Default request timeout in milliseconds
export const DEFAULT_TIMEOUT = 30000;

// API endpoints
export const ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/users',
    PROFILE: '/api/v1/users/me',
  },
  
  // Project endpoints
  PROJECTS: {
    LIST: '/api/v1/projects',
    DETAILS: (id) => `/api/v1/projects/${id}`,
    CREATE: '/api/v1/projects',
    UPDATE: (id) => `/api/v1/projects/${id}`,
    DELETE: (id) => `/api/v1/projects/${id}`,
    DOCUMENTS: (id) => `/api/v1/projects/${id}/documents`,
    ELEMENTS: (id) => `/api/v1/projects/${id}/elements`,
    QUOTES: (id) => `/api/v1/projects/${id}/quotes`,
  },
  
  // Document endpoints
  DOCUMENTS: {
    UPLOAD: '/api/v1/documents/upload',
    ANALYZE: '/api/v1/documents/analyze',
  },
  
  // Quote endpoints
  QUOTES: {
    LIST: '/api/v1/quotes',
    DETAILS: (id) => `/api/v1/quotes/${id}`,
    CREATE: '/api/v1/quotes',
    UPDATE: (id) => `/api/v1/quotes/${id}`,
    DELETE: (id) => `/api/v1/quotes/${id}`,
    ITEMS: (id) => `/api/v1/quotes/${id}/items`,
    GENERATE: (id) => `/api/v1/quotes/${id}/generate-from-elements`,
  },
};

// Create API request headers with authentication token
export const createAuthHeaders = (token) => {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
};

// Handle API errors
export const handleApiError = (error) => {
  let errorMessage = 'An unexpected error occurred';
  
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    if (error.response.data && error.response.data.detail) {
      errorMessage = error.response.data.detail;
    } else {
      errorMessage = `Error ${error.response.status}: ${error.response.statusText}`;
    }
  } else if (error.request) {
    // The request was made but no response was received
    errorMessage = 'No response received from server';
  }
  
  return errorMessage;
};
