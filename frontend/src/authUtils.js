import { API_BASE_URL } from './config';

// Authentication utility functions
export const authUtils = {
  // Make authenticated API calls with automatic token expiry handling
  async apiCall(endpoint, options = {}, navigate = null) {
    const token = localStorage.getItem('access_token');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...options.headers
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        // Handle token expiry - 401 Unauthorized
        if (response.status === 401) {
          this.handleTokenExpiry(navigate);
          return null; // Return null to indicate auth failure
        }
        
        // Handle server errors (maintain compatibility with existing error handling)
        if (response.status === 502 || response.status >= 500) {
          throw new Error('Connection error');
        }
        
        const errorData = await response.json();
        // Create an error with the detail message (maintain compatibility)
        const error = new Error(errorData.detail || 'Server error');
        error.status = response.status;
        error.data = errorData;
        throw error;
      }
      
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      if (error.message === 'Failed to fetch') {
        throw new Error('Connection error');
      }
      
      throw error;
    }
  },

  // Handle token expiry
  handleTokenExpiry(navigate = null) {
    // Clear expired token and user data
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    
    // Show user-friendly message
    alert('Your session has expired. Please log in again.');
    
    // Redirect to login page if navigate function is provided
    if (navigate) {
      navigate('/');
    } else {
      // Fallback: reload the page which should redirect to login
      window.location.href = '/';
    }
  },

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    return !!(token && user);
  },

  // Get current user data
  getCurrentUser() {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        return JSON.parse(userData);
      } catch (error) {
        console.error('Error parsing user data:', error);
        return null;
      }
    }
    return null;
  },

  // Logout user
  logout(navigate = null) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    
    if (navigate) {
      navigate('/');
    } else {
      window.location.href = '/';
    }
  }
};

export default authUtils;
