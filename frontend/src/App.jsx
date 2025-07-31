import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./App.css";
import LandingPage from "./LandingPage";
import MenuScreen from "./MenuScreen";
import ProfileScreen from "./ProfileScreen"; // Add this import
import HistoryScreen from "./HistoryScreen"; // Add this import
import PracticeGame from "./PracticeGame";
import MultiplayerGame from "./MultiplayerGame";
import GoogleCallback from "./GoogleCallback";

// Component to handle authentication logic
function AuthenticatedApp() {
  const [user, setUser] = useState(null);
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
  }, []);

  // Add useEffect to debug user state changes
  useEffect(() => {
    console.log('User state changed:', user);
  }, [user]);

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

  // handler for user profile updates
  const handleUserUpdate = (updatedUser) => {
    setUser(updatedUser);
  };

  // Routes for authenticated users
  if (user) {
    return (
      <Routes>
        <Route path="/" element={<Navigate to="/menu" replace />} />
        <Route path="/menu" element={<MenuScreen user={user} onLogout={handleLogout} />} />
        <Route path="/profile" element={<ProfileScreen user={user} onUserUpdate={handleUserUpdate} />} />
        <Route path="/profile/gamehistory" element={<HistoryScreen user={user} />} />
        <Route path="/practice" element={<PracticeGame user={user} />} />
        <Route path="/multiplayer" element={<MultiplayerGame user={user} />} />
        <Route path="*" element={<Navigate to="/menu" replace />} />
      </Routes>
    );
  }

  // Routes for unauthenticated users
  return (
    <Routes>
      <Route path="/" element={<LandingPage onAuthSuccess={handleAuthSuccess} />} />
      <Route path="/auth/google/callback" element={<GoogleCallback onAuthSuccess={handleAuthSuccess} onAuthError={handleAuthError} />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthenticatedApp />
    </Router>
  );
}

export default App;
