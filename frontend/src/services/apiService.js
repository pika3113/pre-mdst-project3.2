/**
 * API Service Module
 * Centralized API communication layer for the Wordle game
 */

import { API_BASE_URL } from '../utils/config';

/**
 * Base API request handler with error handling and token management
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} Response data
 */
export const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
        ...options.headers
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      if (response.status === 401) {
        // Handle token expiry
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/';
        return null;
      }
      
      if (response.status === 502 || response.status >= 500) {
        throw new Error('Connection error');
      }
      
      const errorData = await response.json();
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
    
    throw error;
  }
};

/**
 * Game API methods
 */
export const gameAPI = {
  // Start a new game
  startGame: (difficulty) => apiRequest('/start_game', {
    method: 'POST',
    body: JSON.stringify({ difficulty })
  }),

  // Submit a guess
  submitGuess: (gameId, guess) => apiRequest('/submit_guess', {
    method: 'POST',
    body: JSON.stringify({ game_id: gameId, guess })
  }),

  // Get game state
  getGameState: (gameId) => apiRequest(`/game_state/${gameId}`),

  // Get word lists by difficulty
  getWordLists: () => apiRequest('/word_lists'),

  // Validate a word
  validateWord: (word, difficulty) => apiRequest('/validate_word', {
    method: 'POST',
    body: JSON.stringify({ word, difficulty })
  })
};

/**
 * Statistics API methods
 */
export const statsAPI = {
  // Get user statistics
  getUserStats: () => apiRequest('/api/user/stats'),

  // Get game history
  getGameHistory: (limit = 20) => apiRequest(`/game_history?limit=${limit}`),

  // Get detailed statistics
  getDetailedStats: () => apiRequest('/detailed_stats')
};

/**
 * User API methods
 */
export const userAPI = {
  // Get user profile
  getProfile: () => apiRequest('/profile'),

  // Update user profile
  updateProfile: (profileData) => apiRequest('/profile', {
    method: 'PUT',
    body: JSON.stringify(profileData)
  }),

  // Change password
  changePassword: (currentPassword, newPassword) => apiRequest('/change_password', {
    method: 'POST',
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  })
};

/**
 * Authentication API methods
 */
export const authAPI = {
  // Login with email/password
  login: (username, password) => apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),

  // Register new user
  register: (userData) => apiRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),

  // Google OAuth login
  googleLogin: (credential) => apiRequest('/api/auth/google', {
    method: 'POST',
    body: JSON.stringify({ credential })
  }),

  // Logout
  logout: () => apiRequest('/api/auth/logout', {
    method: 'POST'
  }),

  // Verify token
  verifyToken: () => apiRequest('/api/auth/verify-token')
};
