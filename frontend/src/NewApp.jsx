import React, { useState, useEffect } from "react";
import "./App.css";
import LandingPage from "./LandingPage";
import MenuScreen from "./MenuScreen";
import StatsScreen from "./StatsScreen";
import PracticeGame from "./PracticeGame";
import MultiplayerGame from "./MultiplayerGame";
import GoogleCallback from "./GoogleCallback";

function App() {
  const [currentScreen, setCurrentScreen] = useState('landing'); // landing, menu, stats, practice, multiplayer
  const [user, setUser] = useState(null);
  const [isGoogleCallback, setIsGoogleCallback] = useState(false);

  // Check for Google OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const currentPath = window.location.pathname;
    
    console.log('App.jsx - Checking for Google OAuth callback:', {
      code: code ? 'present' : 'missing',
      currentPath: currentPath,
      fullURL: window.location.href
    });
    
    // Only set callback flag if we have a code and are on the callback path
    // This prevents the callback from triggering on other pages with code params
    if (code && (currentPath === '/auth/google/callback' || 
                 (currentPath === '/' && window.location.search.includes('code=')))) {
      console.log('App.jsx - Setting isGoogleCallback to true');
      setIsGoogleCallback(true);
    }
  }, []);

  // Check for existing authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setCurrentScreen('menu');
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  // Authentication handlers
  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setCurrentScreen('menu');
    setIsGoogleCallback(false);
    // Clear URL parameters after successful Google auth
    if (window.location.search) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const handleAuthError = (error) => {
    setIsGoogleCallback(false);
    console.error('Auth error:', error);
    // Clear URL parameters after failed Google auth
    if (window.location.search) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    setCurrentScreen('landing');
  };

  const handleNavigate = (screen) => {
    setCurrentScreen(screen);
  };

  // Handle Google OAuth callback
  if (isGoogleCallback) {
    return (
      <GoogleCallback 
        onAuthSuccess={handleAuthSuccess}
        onAuthError={handleAuthError}
      />
    );
  }

  // Main app routing
  if (!user) {
    return (
      <LandingPage onAuthSuccess={handleAuthSuccess} />
    );
  }

  switch (currentScreen) {
    case 'menu':
      return (
        <MenuScreen 
          user={user}
          onLogout={handleLogout}
          onNavigate={handleNavigate}
        />
      );
    
    case 'stats':
      return (
        <StatsScreen 
          user={user}
          onNavigate={handleNavigate}
        />
      );
    
    case 'practice':
      return (
        <PracticeGame 
          user={user}
          onNavigate={handleNavigate}
        />
      );
    
    case 'multiplayer':
      return (
        <MultiplayerGame 
          user={user}
          onNavigate={handleNavigate}
        />
      );
    
    default:
      return (
        <MenuScreen 
          user={user}
          onLogout={handleLogout}
          onNavigate={handleNavigate}
        />
      );
  }
}

export default App;
