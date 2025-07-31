import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../utils/config';
import { authUtils } from '../services/authService';
import './ProfileScreen.css';

function ProfileScreen({ user, onUserUpdate }) {
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    profile_picture: user?.profile_picture || ''
  });
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statsError, setStatsError] = useState('');
  const [activeTab, setActiveTab] = useState('profile');
  const navigate = useNavigate();
  const location = useLocation();

  // Handle URL parameters for tab selection
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const tabParam = urlParams.get('tab');
    
    // Check if this is a direct access to stats tab
    if (tabParam === 'stats') {
      const allowStatsAccess = sessionStorage.getItem('allowStatsAccess');
      
      if (!allowStatsAccess) {
        // Redirect unauthorized direct access to stats back to profile tab
        navigate('/profile', { replace: true });
        return;
      } else {
        // Clear the flag after use
        sessionStorage.removeItem('allowStatsAccess');
      }
    }
    
    if (tabParam && (tabParam === 'profile' || tabParam === 'stats')) {
      setActiveTab(tabParam);
    }
  }, [location.search, navigate]);

  // Helper function to format date in SGT timezone
  const formatDateSGT = (timestamp) => {
    // The timestamp is already in SGT format from the backend
    // So we just need to parse it and display it properly
    const date = new Date(timestamp + '+08:00'); // Explicitly specify SGT offset
    return date.toLocaleDateString('en-SG', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  // Calculate derived stats
  const calculateWinRate = () => {
    if (!stats || !stats.total_games || stats.total_games === 0) return 0;
    return Math.round((stats.wins / stats.total_games) * 100);
  };

  const getAverageGuesses = () => {
    if (!stats || !stats.wins || stats.wins === 0) return 0;
    return (stats.average_guesses || 0).toFixed(1);
  };

  // Calculate stats from game history
  const calculateStatsFromHistory = (games) => {
    if (!games || games.length === 0) {
      return {
        total_games: 0,
        wins: 0,
        streak: 0,
        max_streak: 0,
        average_guesses: 0,
        difficulty_stats: {},
        guess_distribution: {}
      };
    }

    const wins = games.filter(game => game.won).length;
    const totalGames = games.length;
    
    // Calculate current streak
    let currentStreak = 0;
    for (let i = games.length - 1; i >= 0; i--) {
      if (games[i].won) {
        currentStreak++;
      } else {
        break;
      }
    }

    // Calculate max streak
    let maxStreak = 0;
    let tempStreak = 0;
    games.forEach(game => {
      if (game.won) {
        tempStreak++;
        maxStreak = Math.max(maxStreak, tempStreak);
      } else {
        tempStreak = 0;
      }
    });

    // Calculate average guesses for won games
    const wonGames = games.filter(game => game.won);
    const totalGuesses = wonGames.reduce((sum, game) => sum + (game.guesses || 0), 0);
    const averageGuesses = wonGames.length > 0 ? totalGuesses / wonGames.length : 0;

    // Calculate guess distribution
    const guessDistribution = {};
    wonGames.forEach(game => {
      const guesses = game.guesses || 0;
      guessDistribution[guesses] = (guessDistribution[guesses] || 0) + 1;
    });

    // Calculate difficulty stats
    const difficultyStats = {};
    games.forEach(game => {
      const diff = game.difficulty || 'unknown';
      if (!difficultyStats[diff]) {
        difficultyStats[diff] = {
          total_games: 0,
          wins: 0,
          total_guesses: 0
        };
      }
      difficultyStats[diff].total_games++;
      if (game.won) {
        difficultyStats[diff].wins++;
        difficultyStats[diff].total_guesses += (game.guesses || 0);
      }
    });

    // Add average_guesses to difficulty stats
    Object.keys(difficultyStats).forEach(diff => {
      const stats = difficultyStats[diff];
      stats.average_guesses = stats.wins > 0 ? stats.total_guesses / stats.wins : 0;
    });

    return {
      total_games: totalGames,
      wins: wins,
      streak: currentStreak,
      max_streak: maxStreak,
      average_guesses: averageGuesses,
      difficulty_stats: difficultyStats,
      guess_distribution: guessDistribution
    };
  };

  // API call wrapper with auth token and expiry handling
  const apiCall = async (endpoint, options = {}) => {
    return await authUtils.apiCall(endpoint, options, navigate);
  };

  // Fetch user stats and history
  useEffect(() => {
    if (activeTab === 'stats') {
      fetchStats();
      fetchHistory();
    }
  }, [activeTab]);

  const fetchStats = async () => {
    try {
      setStatsLoading(true);
      setStatsError('');
      
      try {
        // Try to get stats from backend first
        const data = await apiCall('/api/user/stats');
        if (data === null) return; // Auth failure, user will be redirected
        setStats(data);
        return; // Successfully got stats from backend
      } catch (error) {
        console.log('Stats endpoint error, attempting to calculate from history...');
      }
      
      // Always try to calculate from history as fallback
      try {
        const historyData = await apiCall('/history');
        if (historyData === null) return; // Auth failure, user will be redirected
        const games = historyData.games || historyData || [];
        
        if (games.length === 0) {
          setStats({
            total_games: 0,
            wins: 0,
            streak: 0,
            max_streak: 0,
            average_guesses: 0,
            difficulty_stats: {},
            guess_distribution: {}
          });
        } else {
          const calculatedStats = calculateStatsFromHistory(games);
          setStats(calculatedStats);
        }
      } catch (historyError) {
        console.error('Failed to get history for stats calculation:', historyError);
        setStatsError(`Failed to load statistics: ${historyError.message || 'Unknown error'}`);
        setStats(null);
      }
    } catch (error) {
      console.error('Error in fetchStats:', error);
      setStatsError(`Error loading statistics: ${error.message || 'Unknown error'}`);
      setStats(null);
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const data = await apiCall('/history');
      if (data === null) return; // Auth failure, user will be redirected
      setHistory(data.games || data || []); // Handle different response formats
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const handleInputChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleProfilePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file size must be less than 5MB');
        return;
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }

      const reader = new FileReader();
      reader.onload = (event) => {
        setProfileData({
          ...profileData,
          profile_picture: event.target.result
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const updatedUser = await apiCall('/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      });

      if (updatedUser === null) return; // Auth failure, user will be redirected

      localStorage.setItem('user', JSON.stringify(updatedUser));
      onUserUpdate(updatedUser);
      setSuccess('Profile updated successfully!');
    } catch (error) {
      setError(error.detail || error.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const resetStats = async () => {
    if (window.confirm("Are you sure you want to reset all statistics? This cannot be undone.")) {
      try {
        const result = await apiCall('/reset-stats', { method: "POST" });
        if (result === null) return; // Auth failure, user will be redirected
        
        fetchStats();
        fetchHistory();
        setSuccess('Statistics reset successfully!');
      } catch (error) {
        setError('Failed to reset statistics');
      }
    }
  };

  return (
    <div className="profile-screen">
      <button 
        className="back-to-menu"
        onClick={() => navigate('/menu')}
      >
        ← Back to Menu
      </button>

      <div className="profile-header">
        <h1>Profile</h1>
        <div className="profile-tabs">
          <button 
            className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Settings
          </button>
          <button 
            className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
            onClick={() => setActiveTab('stats')}
          >
            Statistics
          </button>
        </div>
      </div>

      {/* Profile Settings Tab */}
      {activeTab === 'profile' && (
        <div className="profile-content">
          <div className="profile-picture-section">
            <div className="current-picture">
              {profileData.profile_picture ? (
                <img 
                  src={profileData.profile_picture} 
                  alt="Profile" 
                  className="profile-img"
                />
              ) : (
                <div className="profile-placeholder">
                  {profileData.username?.charAt(0)?.toUpperCase() || 'U'}
                </div>
              )}
            </div>
            <div className="picture-upload">
              <label htmlFor="profile-picture" className="upload-btn">
                Change Picture
              </label>
              <input
                id="profile-picture"
                type="file"
                accept="image/*"
                onChange={handleProfilePictureChange}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={profileData.username}
                onChange={handleInputChange}
                required
                minLength={3}
                maxLength={20}
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={profileData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <button type="submit" className="update-btn" disabled={loading}>
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
          </form>
        </div>
      )}

      {/* Statistics Tab */}
      {activeTab === 'stats' && (
        <div className="stats-content">
          {statsLoading ? (
            <div className="loading-stats">Loading statistics...</div>
          ) : statsError ? (
            <div className="stats-error">
              <h3>Error Loading Statistics</h3>
              <p>{statsError}</p>
              <button onClick={fetchStats} className="retry-btn">
                Retry
              </button>
            </div>
          ) : stats ? (
            <>
              {/* Overview Stats */}
              <div className="stats-overview">
                <div className="stat-card">
                  <div className="stat-number">{stats.total_games || 0}</div>
                  <div className="stat-label">Games Played</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{calculateWinRate()}%</div>
                  <div className="stat-label">Win Rate</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats.streak || 0}</div>
                  <div className="stat-label">Current Streak</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats.max_streak || 0}</div>
                  <div className="stat-label">Best Streak</div>
                </div>
              </div>

              {/* Detailed Stats */}
              <div className="detailed-stats">
                <h3>📈 Game Details</h3>
                <div className="stat-row">
                  <span>🏆 Games Won</span>
                  <span>{stats.wins || 0}</span>
                </div>
                <div className="stat-row">
                  <span>❌ Games Lost</span>
                  <span>{(stats.total_games || 0) - (stats.wins || 0)}</span>
                </div>
                <div className="stat-row">
                  <span>🎯 Average Guesses</span>
                  <span>{getAverageGuesses()}</span>
                </div>
                <div className="stat-row">
                  <span>⏱️ Total Time Played</span>
                  <span>{stats.total_time || 'N/A'}</span>
                </div>
              </div>

              {/* Difficulty Stats */}
              {stats.difficulty_stats && Object.keys(stats.difficulty_stats).length > 0 && (
                <div className="difficulty-stats">
                  <h3>📊 Performance by Difficulty</h3>
                  {Object.entries(stats.difficulty_stats).map(([difficulty, diffStats]) => (
                    <div key={difficulty} className="difficulty-row">
                      <div className={`difficulty-name ${difficulty}`}>
                        {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                      </div>
                      <div className="difficulty-details">
                        <div className="difficulty-stat">
                          <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                            {diffStats.total_games || 0}
                          </div>
                          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Games</div>
                        </div>
                        <div className="difficulty-stat">
                          <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                            {diffStats.total_games > 0 
                              ? Math.round((diffStats.wins / diffStats.total_games) * 100)
                              : 0}%
                          </div>
                          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Win Rate</div>
                        </div>
                        <div className="difficulty-stat">
                          <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                            {(diffStats.average_guesses || 0).toFixed(1)}
                          </div>
                          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Avg Guesses</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Guess Distribution */}
              {stats.guess_distribution && Object.keys(stats.guess_distribution).length > 0 && (
                <div className="guess-distribution">
                  <h3>📊 Guess Distribution</h3>
                  {Object.entries(stats.guess_distribution).map(([guesses, count]) => {
                    const maxCount = Math.max(...Object.values(stats.guess_distribution));
                    const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    
                    return (
                      <div key={guesses} className="distribution-row">
                        <span className="guess-number">{guesses}</span>
                        <div className="distribution-bar">
                          <div 
                            className="distribution-fill"
                            style={{ width: `${percentage}%` }}
                          >
                            <span className="distribution-count">{count}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Recent Games History */}
              {history.length > 0 && (
                <div className="history-section">
                  <h3>🎮 Recent Games</h3>
                  <div className="history-list">
                    {history.slice(0, 3).map((game, index) => (
                      <div key={index} className={`history-item ${game.won ? 'won' : 'lost'}`}>
                        <div className="history-word">{game.word}</div>
                        <div className="history-details">
                          <div className={`history-difficulty ${game.difficulty}`}>
                            {game.difficulty}
                          </div>
                          <div className="history-guesses">{game.guesses} guesses</div>
                          <div className={`history-result ${game.won ? 'won' : 'lost'}`}>
                            {game.won ? '✓' : '✗'}
                          </div>
                        </div>
                        <div className="history-date">
                          {formatDateSGT(game.timestamp)}
                        </div>
                      </div>
                    ))}
                  </div>
                  {history.length > 3 && (
                    <button 
                      className="view-full-history-btn"
                      onClick={() => navigate('/profile/gamehistory')}
                    >
                      📝 View All {history.length} Games
                    </button>
                  )}
                </div>
              )}

              {/* Reset Stats Button */}
              <div className="stats-actions">
                <button className="reset-stats-btn" onClick={resetStats}>
                  🗑️ Reset All Statistics
                </button>
              </div>
            </>
          ) : (
            <div className="no-stats">
              <h3>📊 No Statistics Available</h3>
              <p>Start playing some games to see your statistics!</p>
              <button onClick={fetchStats} className="retry-btn">
                🔄 Refresh Statistics
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ProfileScreen;