import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './MenuScreen.css';

function MenuScreen({ user, onLogout }) {
  const [selectedMode, setSelectedMode] = useState(null);
  const navigate = useNavigate();

  const menuOptions = [
    {
      id: 'practice',
      title: 'Practice Mode',
      description: 'Play solo games to improve your skills',
      icon: '🎯',
      color: '#10b981',
      available: true
    },
    {
      id: 'multiplayer',
      title: 'Multiplayer',
      description: 'Challenge friends in real-time battles',
      icon: '⚔️',
      color: '#f59e0b',
      available: true
    },
    {
      id: 'tournament',
      title: 'Tournaments',
      description: 'Compete in organized events',
      icon: '🏆',
      color: '#8b5cf6',
      available: false,
      comingSoon: true
    }
  ];

  return (
    <div className="menu-screen">
      <div className="menu-header">
        <div className="user-info">
          <div className="user-avatar">
            {user.picture ? (
              <img src={user.picture} alt={user.name} />
            ) : (
              <div className="avatar-placeholder">
                {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </div>
            )}
          </div>
          <div className="user-details">
            <h2>Welcome back, {user.name || 'Player'}!</h2>
            <p>Ready for your next word challenge?</p>
          </div>
        </div>

        <div className="header-actions">
          <button 
            className="stats-btn"
            onClick={() => navigate('/stats')}
          >
            📊 Stats
          </button>
          
          <button 
            className="logout-btn"
            onClick={onLogout}
          >
            🚪 Logout
          </button>
        </div>
      </div>

      <div className="menu-content">
        <h1 className="menu-title">Choose Your Game Mode</h1>
        
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
            <span className="stat-value">-</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Win Rate</span>
            <span className="stat-value">-</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Best Streak</span>
            <span className="stat-value">-</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MenuScreen;
