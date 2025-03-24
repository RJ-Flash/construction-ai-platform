import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { toast } from 'sonner'

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const { response } = error
    
    // Handle specific HTTP errors
    if (response) {
      const status = response.status
      
      // Authentication error
      if (status === 401) {
        // Clear local storage and redirect to login
        localStorage.removeItem('user')
        localStorage.removeItem('token')
        
        // Only redirect if not already on auth pages
        const currentPath = window.location.pathname
        if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
          window.location.href = '/login'
          toast.error('Session expired. Please login again.')
        }
      }
      
      // Forbidden error
      else if (status === 403) {
        toast.error('You do not have permission to access this resource.')
      }
      
      // Server error
      else if (status >= 500) {
        toast.error('Server error. Please try again later.')
      }
      
      // Other client errors
      else if (status >= 400) {
        const errorMessage = response.data?.detail || 'An error occurred.'
        toast.error(errorMessage)
      }
    } 
    // Network or other errors
    else {
      toast.error('Network error. Please check your connection and try again.')
    }
    
    return Promise.reject(error)
  }
)

// Generic request function with types
export const request = async <T = any>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await api(config)
    return response.data
  } catch (error) {
    throw error
  }
}

// API functions for authentication
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email) // FastAPI OAuth2 expects username field
    formData.append('password', password)
    
    return request({
      url: '/auth/login',
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  register: async (userData: { email: string, password: string, full_name: string }) => {
    return request({
      url: '/auth/register',
      method: 'POST',
      data: userData
    })
  },
  
  getCurrentUser: async () => {
    return request({
      url: '/users/me',
      method: 'GET'
    })
  }
}

export default api
