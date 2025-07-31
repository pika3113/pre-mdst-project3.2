import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../utils/config';
import './HistoryScreen.css';

function HistoryScreen({ user }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('date'); // 'date', 'difficulty', 'result'
  const [filterBy, setFilterBy] = useState('all'); // 'all', 'won', 'lost'
  const [currentPage, setCurrentPage] = useState(1);
  const gamesPerPage = 10;
  const navigate = useNavigate();

  // Helper function to format date in SGT timezone
  const formatDateSGT = (timestamp) => {
    // The timestamp is already in SGT format from the backend
    // So we just need to parse it and display it properly
    const date = new Date(timestamp + '+08:00'); // Explicitly specify SGT offset
    return date.toLocaleString('en-SG', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  // API call wrapper with auth token
  const apiCall = async (endpoint, options = {}) => {
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
        const errorData = await response.json();
        throw errorData;
      }
      
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError' || error.message === 'Failed to fetch') {
        throw new Error('Connection error');
      }
      
      throw error;
    }
  };

  // Fetch game history
  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('Fetching full history from:', `${API_BASE_URL}/history`);
      const data = await apiCall('/history');
      console.log('History response:', data);
      setHistory(data.games || data || []);
    } catch (error) {
      console.error('Error fetching history:', error);
      setError(`Error loading game history: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Sort and filter games
  const getFilteredAndSortedGames = () => {
    let filteredGames = [...history];

    // Filter by result
    if (filterBy === 'won') {
      filteredGames = filteredGames.filter(game => game.won);
    } else if (filterBy === 'lost') {
      filteredGames = filteredGames.filter(game => !game.won);
    }

    // Sort games
    filteredGames.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.timestamp) - new Date(a.timestamp); // Newest first
        case 'difficulty':
          const difficultyOrder = { easy: 1, medium: 2, hard: 3 };
          return (difficultyOrder[a.difficulty] || 4) - (difficultyOrder[b.difficulty] || 4);
        case 'result':
          if (a.won === b.won) return 0;
          return a.won ? -1 : 1; // Won games first
        default:
          return 0;
      }
    });

    return filteredGames;
  };

  const filteredAndSortedGames = getFilteredAndSortedGames();
  const totalPages = Math.ceil(filteredAndSortedGames.length / gamesPerPage);
  const startIndex = (currentPage - 1) * gamesPerPage;
  const currentGames = filteredAndSortedGames.slice(startIndex, startIndex + gamesPerPage);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [sortBy, filterBy]);

  if (loading) {
    return (
      <div className="history-screen">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading game history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-screen">
      <button 
        className="back-to-profile"
        onClick={() => navigate('/profile')}
      >
        ← Back to Profile
      </button>

      <div className="history-header">
        <h1>🎮 Game History</h1>
        <p>Complete record of all your Wordle games</p>
      </div>

      {error ? (
        <div className="error-state">
          <h3>Error Loading History</h3>
          <p>{error}</p>
          <button onClick={fetchHistory} className="retry-btn">
            🔄 Retry
          </button>
        </div>
      ) : history.length === 0 ? (
        <div className="no-history">
          <h3>📊 No Game History</h3>
          <p>Start playing some games to see your history!</p>
          <button onClick={() => navigate('/practice')} className="play-btn">
            🎮 Play Practice Game
          </button>
        </div>
      ) : (
        <>
          <div className="history-controls">
            <div className="control-group">
              <label>Sort by:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="date">Date (Newest First)</option>
                <option value="difficulty">Difficulty</option>
                <option value="result">Result (Won First)</option>
              </select>
            </div>
            
            <div className="control-group">
              <label>Filter by:</label>
              <select value={filterBy} onChange={(e) => setFilterBy(e.target.value)}>
                <option value="all">All Games</option>
                <option value="won">Won Games</option>
                <option value="lost">Lost Games</option>
              </select>
            </div>

            <div className="history-stats">
              <span className="stat">
                Total: {filteredAndSortedGames.length} games
              </span>
              <span className="stat">
                Won: {filteredAndSortedGames.filter(g => g.won).length}
              </span>
              <span className="stat">
                Lost: {filteredAndSortedGames.filter(g => !g.won).length}
              </span>
            </div>
          </div>

          <div className="history-content">
            <div className="history-list">
              {currentGames.map((game, index) => (
                <div key={startIndex + index} className={`history-item ${game.won ? 'won' : 'lost'}`}>
                  <div className="game-number">
                    #{filteredAndSortedGames.length - startIndex - index}
                  </div>
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

            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  className="page-btn"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  ← Previous
                </button>
                
                <div className="page-info">
                  Page {currentPage} of {totalPages}
                </div>
                
                <button 
                  className="page-btn"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next →
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default HistoryScreen;
