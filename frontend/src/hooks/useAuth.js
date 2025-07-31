import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Custom hook for managing authentication state and operations
 * Centralizes authentication logic for better reusability
 */
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Check for existing authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  // Authentication handlers
  const handleAuthSuccess = (userData) => {
    console.log('handleAuthSuccess called with:', userData);
    setUser(userData);
    console.log('About to navigate to /menu');
    navigate('/menu');
    // Clear URL parameters after successful Google auth
    if (window.location.search) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const handleAuthError = (error) => {
    console.error('Auth error:', error);
    navigate('/');
    // Clear URL parameters after failed Google auth
    if (window.location.search) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/');
  };

  // Handler for user profile updates
  const handleUserUpdate = (updatedUser) => {
    setUser(updatedUser);
    // Update localStorage as well
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  return {
    user,
    isLoading,
    handleAuthSuccess,
    handleAuthError,
    handleLogout,
    handleUserUpdate,
    isAuthenticated: !!user
  };
};
