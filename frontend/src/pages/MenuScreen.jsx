import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../utils/config';
import './MenuScreen.css';

function MenuScreen({ user, onLogout }) {
  const [selectedMode, setSelectedMode] = useState(null);
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  // Fetch user stats for quick display
  useEffect(() => {
    fetchQuickStats();
  }, []);

  const fetchQuickStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        // No token available, user should be logged out
        onLogout();
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/user/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        // Token expired, trigger logout through proper flow
        onLogout();
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      // Don't set stats on error, component will show default values
    }
  };

  const menuOptions = [
    {
      id: 'practice',
      title: 'Wordle',
      description: 'Classic 5-letter word guessing game',
      icon: '🔤',
      color: '#10b981',
      available: true
    },
    {
      id: 'hangman',
      title: 'Hangle',
      description: 'Classic hangman word guessing game',
      icon: '🎪',
      color: '#e11d48',
      available: true
    },
    {
      id: 'morphle',
      title: 'Morphle',
      description: 'Transform words step by step',
      icon: '🔄',
      color: '#8b5cf6',
      available: true
    },
    {
      id: 'multiplayer',
      title: 'Multiplayer',
      description: 'Challenge friends in real-time battles',
      icon: '⚔️',
      color: '#f59e0b',
      available: true
    }
  ];

  const calculateWinRate = () => {
    if (!stats || stats.games_played === 0) return '-';
    return `${((stats.games_won / stats.games_played) * 100).toFixed(1)}%`;
  };

  return (
    <div className="menu-screen">
      <div className="menu-header">
        <div className="user-info">
          <div className="user-avatar">
            {user.profile_picture ? (
              <img src={user.profile_picture} alt={user.username} />
            ) : (
              <div className="avatar-placeholder">
                {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
              </div>
            )}
          </div>
          <div className="user-details">
            <h2>Welcome back, {user.username || 'Player'}!</h2>
            <p>Ready for your next word challenge?</p>
          </div>
        </div>

        <div className="header-actions">
          <button 
            className="profile-btn"
            onClick={() => navigate('/profile')}
            title="View Profile & Stats"
          >
            👤 Profile
          </button>
          
          <button 
            className="logout-btn"
            onClick={onLogout}
            title="Logout"
          >
            🚪 Logout
          </button>
        </div>
      </div>

      <div className="menu-content">
        <h1 className="menu-title">Choose Your Word Game</h1>
        
        <div className="game-modes">
          {menuOptions.map((mode) => (
            <div
              key={mode.id}
              className={`mode-card ${!mode.available ? 'disabled' : ''} ${selectedMode === mode.id ? 'selected' : ''}`}
              onClick={() => {
                if (mode.available) {
                  setSelectedMode(mode.id);
                  setTimeout(() => navigate(`/${mode.id}`), 200);
                }
              }}
              style={{ '--mode-color': mode.color }}
            >
              <div className="mode-icon">{mode.icon}</div>
              <div className="mode-content">
                <h3 className="mode-title">
                  {mode.title}
                  {mode.comingSoon && <span className="coming-soon">Coming Soon</span>}
                </h3>
                <p className="mode-description">{mode.description}</p>
              </div>
              {mode.available && (
                <div className="mode-arrow">→</div>
              )}
            </div>
          ))}
        </div>

        <div className="quick-stats">
          <div className="stat-item">
            <span className="stat-label">Games Played</span>
            <span className="stat-value">{stats?.games_played || '-'}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Win Rate</span>
            <span className="stat-value">{calculateWinRate()}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Best Streak</span>
            <span className="stat-value">{stats?.max_streak || '-'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MenuScreen;
