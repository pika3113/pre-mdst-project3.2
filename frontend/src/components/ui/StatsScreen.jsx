import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../utils/config';
import './StatsScreen.css';

function StatsScreen({ user }) {
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('personal');
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
    fetchLeaderboard();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/user/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/leaderboard`);
      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data.leaderboard.slice(0, 10)); // Top 10
      }
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const mockStats = {
    gamesPlayed: 47,
    gamesWon: 32,
    winRate: 68,
    currentStreak: 5,
    maxStreak: 12,
    averageGuesses: 4.2,
    difficulty: {
      easy: { played: 15, won: 14 },
      medium: { played: 25, won: 16 },
      hard: { played: 7, won: 2 }
    }
  };

  const mockLeaderboard = [
    { rank: 1, name: 'WordMaster2024', wins: 156, winRate: 89 },
    { rank: 2, name: 'GuessGenius', wins: 142, winRate: 85 },
    { rank: 3, name: 'LetterLegend', wins: 138, winRate: 82 },
    { rank: 4, name: user?.name || 'You', wins: 32, winRate: 68, isUser: true },
    { rank: 5, name: 'WordWizard', wins: 128, winRate: 76 },
  ];

  const displayStats = stats || mockStats;
  const displayLeaderboard = leaderboard.length > 0 ? leaderboard : mockLeaderboard;

  if (loading && !stats) {
    return (
      <div className="stats-screen loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your stats...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="stats-screen">
      <div className="stats-header">
        <button 
          className="back-btn"
          onClick={() => navigate('/menu')}
        >
          ← Back to Menu
        </button>
        
        <h1>Your Wordle Journey</h1>
        
        <div className="tab-switcher">
          <button 
            className={`tab-btn ${activeTab === 'personal' ? 'active' : ''}`}
            onClick={() => setActiveTab('personal')}
          >
            📊 Personal Stats
          </button>
          <button 
            className={`tab-btn ${activeTab === 'leaderboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('leaderboard')}
          >
            🏆 Leaderboard
          </button>
        </div>
      </div>

      <div className="stats-content">
        {activeTab === 'personal' ? (
          <div className="personal-stats">
            <div className="stats-overview">
              <div className="stat-card primary">
                <div className="stat-icon">🎯</div>
                <div className="stat-info">
                  <span className="stat-value">{displayStats.total_games || displayStats.gamesPlayed || 0}</span>
                  <span className="stat-label">Games Played</span>
                </div>
              </div>
              
              <div className="stat-card success">
                <div className="stat-icon">✅</div>
                <div className="stat-info">
                  <span className="stat-value">{displayStats.win_rate || displayStats.winRate || 0}%</span>
                  <span className="stat-label">Win Rate</span>
                </div>
              </div>
              
              <div className="stat-card warning">
                <div className="stat-icon">🔥</div>
                <div className="stat-info">
                  <span className="stat-value">{displayStats.streak || displayStats.currentStreak || 0}</span>
                  <span className="stat-label">Current Streak</span>
                </div>
              </div>
              
              <div className="stat-card info">
                <div className="stat-icon">⭐</div>
                <div className="stat-info">
                  <span className="stat-value">{displayStats.max_streak || displayStats.maxStreak || 0}</span>
                  <span className="stat-label">Best Streak</span>
                </div>
              </div>
            </div>

            <div className="detailed-stats">
              <div className="difficulty-breakdown">
                <h3>Performance by Difficulty</h3>
                <div className="difficulty-stats">
                  {Object.entries(displayStats.difficulty_stats || displayStats.difficulty || {}).map(([difficulty, data]) => (
                    <div key={difficulty} className="difficulty-stat">
                      <div className="difficulty-header">
                        <span className={`difficulty-badge ${difficulty}`}>
                          {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                        </span>
                        <span className="difficulty-rate">
                          {Math.round(((data.wins || data.won) / (data.total_games || data.played)) * 100) || 0}% win rate
                        </span>
                      </div>
                      <div className="difficulty-bar">
                        <div 
                          className="difficulty-fill"
                          style={{ width: `${((data.wins ?? data.won ?? 0) / (data.total_games ?? data.played ?? 1)) * 100}%` }}
                        ></div>
                      </div>
                      <div className="difficulty-numbers">
                        {data.wins ?? data.won ?? 0}/{data.total_games ?? data.played ?? 0} games won
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="guess-distribution">
                <h3>Guess Distribution</h3>
                <div className="distribution-bars">
                  {[1, 2, 3, 4, 5, 6].map(guesses => (
                    <div key={guesses} className="distribution-row">
                      <span className="guess-number">{guesses}</span>
                      <div className="distribution-bar">
                        <div 
                          className="distribution-fill"
                          style={{ width: `${Math.random() * 80 + 10}%` }}
                        >
                          <span className="distribution-count">
                            {Math.floor(Math.random() * 15) + 1}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="leaderboard">
            <div className="leaderboard-header">
              <h3>🏆 Global Leaderboard</h3>
              <p>Compete with players worldwide</p>
            </div>
            
            <div className="leaderboard-list">
              {displayLeaderboard.map((player, index) => (
                <div 
                  key={index} 
                  className={`leaderboard-item ${player.isUser ? 'user-entry' : ''}`}
                >
                  <div className="player-rank">
                    {player.rank <= 3 ? (
                      <span className={`rank-medal rank-${player.rank}`}>
                        {player.rank === 1 ? '🥇' : player.rank === 2 ? '🥈' : '🥉'}
                      </span>
                    ) : (
                      <span className="rank-number">#{player.rank}</span>
                    )}
                  </div>
                  
                  <div className="player-info">
                    <span className="player-name">{player.name}</span>
                    {player.isUser && <span className="you-badge">You</span>}
                  </div>
                  
                  <div className="player-stats">
                    <span className="player-wins">{player.wins} wins</span>
                    <span className="player-rate">{player.winRate}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default StatsScreen;
