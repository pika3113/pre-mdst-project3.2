import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./styles/App.css";
import LandingPage from "./pages/LandingPage";
import MenuScreen from "./pages/MenuScreen";
import ProfileScreen from "./pages/ProfileScreen";
import HistoryScreen from "./pages/HistoryScreen";
import PracticeGame from "./components/game/PracticeGame";
import MultiplayerGame from "./components/game/MultiplayerGame";
import GoogleCallback from "./components/auth/GoogleCallback";
import LoadingSpinner from "./components/ui/LoadingSpinner";
import { useAuth } from "./hooks/useAuth";

// Component to handle authentication logic
function AuthenticatedApp() {
  const { 
    user, 
    isLoading, 
    handleAuthSuccess, 
    handleAuthError, 
    handleLogout, 
    handleUserUpdate,
    isAuthenticated 
  } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Initializing..." />;
  }

  // Routes for authenticated users
  if (isAuthenticated) {
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
