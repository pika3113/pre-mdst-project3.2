import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from './config';
import './PracticeGame.css';

const MAX_GUESSES = 6;

function PracticeGame({ user }) {
  const [difficulty, setDifficulty] = useState('medium');
  const [wordLength, setWordLength] = useState(5);
  const [grid, setGrid] = useState([]);
  const [colors, setColors] = useState([]);
  const [currentRow, setCurrentRow] = useState(0);
  const [currentCol, setCurrentCol] = useState(0);
  const [isGameOver, setIsGameOver] = useState(false);
  const [message, setMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasConnectionError, setHasConnectionError] = useState(false);
  const navigate = useNavigate();

  // Initialize empty grids based on word length
  const initializeGrids = (length) => {
    const emptyGrid = Array(MAX_GUESSES).fill(null).map(() => Array(length).fill(''));
    const emptyColorGrid = Array(MAX_GUESSES).fill(null).map(() => Array(length).fill('white'));
    setGrid(emptyGrid);
    setColors(emptyColorGrid);
  };

  // API call utility
  const apiCall = async (endpoint, options = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const token = localStorage.getItem('access_token');
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      };
      
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        if (response.status === 502 || response.status >= 500) {
          setHasConnectionError(true);
          throw new Error('Connection error');
        }
        
        const errorData = await response.json();
        // Create an error with the detail message
        const error = new Error(errorData.detail || 'Server error');
        error.status = response.status;
        error.data = errorData;
        throw error;
      }
      
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError' || error.message === 'Failed to fetch') {
        setHasConnectionError(true);
        throw new Error('Connection error');
      }
      
      throw error;
    }
  };

  // Start a new game
  const startNewGame = async (newDifficulty = difficulty) => {
    setIsLoading(true);
    setDifficulty(newDifficulty);
    setHasConnectionError(false);
    
    try {
      const data = await apiCall(`/new-game/${newDifficulty}`, {
        method: 'POST',
        body: JSON.stringify({}),
      });

      setSessionId(data.session_id);
      setWordLength(data.word_length);
      initializeGrids(data.word_length);
      setCurrentRow(0);
      setCurrentCol(0);
      setIsGameOver(false);
      setMessage('');
    } catch (error) {
      console.error('Error starting new game:', error);
      if (!hasConnectionError) {
        setMessage('Failed to start new game. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Submit a guess
  const submitGuess = async (guess) => {
    if (!sessionId) return;

    try {
      const data = await apiCall(`/guess/${sessionId}`, {
        method: 'POST',
        body: JSON.stringify({
          guess: guess
        }),
      });

      // Update colors - the backend returns 'cells' with color codes
      const newColors = [...colors];
      newColors[currentRow] = data.cells.map(colorCode => {
        if (colorCode === "#1fdb0dff") return 'correct';
        if (colorCode === "#e4c53aff") return 'present';
        if (colorCode === "#d71717ff") return 'absent';
        return 'white';
      });
      setColors(newColors);

      if (data.won) {
        setMessage('🎉 Congratulations! You guessed it!');
        setIsGameOver(true);
      } else if (data.game_over) {
        setMessage(data.message || `Game over! The word was: ${data.word || 'unknown'}`);
        setIsGameOver(true);
      } else {
        setCurrentRow(currentRow + 1);
        setCurrentCol(0);
      }
    } catch (error) {
      console.error('Error submitting guess:', error);
      
      // Check if it's a validation error (400 status) with specific message
      if (error.message && error.message.includes('not a valid word')) {
        // Clear the current row and show invalid word message
        const newGrid = [...grid];
        newGrid[currentRow] = Array(wordLength).fill('');
        setGrid(newGrid);
        setCurrentCol(0);
        setMessage('Invalid word! Please try again.');
        setTimeout(() => setMessage(''), 2000);
      } else {
        setMessage('Error submitting guess. Please try again.');
      }
    }
  };

  // Handle keyboard input
  const handleKeyPress = useCallback((event) => {
    if (isGameOver || isLoading) return;

    const key = event.key.toLowerCase();

    if (key === 'enter') {
      // Submit guess
      const guess = grid[currentRow].join('').toLowerCase();
      if (guess.length === wordLength) {
        submitGuess(guess);
      } else {
        setMessage('Please complete the word before submitting.');
        setTimeout(() => setMessage(''), 2000);
      }
    } else if (key === 'backspace') {
      // Delete letter
      if (currentCol > 0) {
        const newGrid = [...grid];
        newGrid[currentRow][currentCol - 1] = '';
        setGrid(newGrid);
        setCurrentCol(currentCol - 1);
      }
    } else if (/^[a-z]$/.test(key) && currentCol < wordLength) {
      // Add letter
      const newGrid = [...grid];
      newGrid[currentRow][currentCol] = key.toUpperCase();
      setGrid(newGrid);
      setCurrentCol(currentCol + 1);
    }
  }, [currentRow, currentCol, grid, isGameOver, isLoading, wordLength]);

  // Set up keyboard listeners
  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  // Start initial game
  useEffect(() => {
    startNewGame();
  }, []);

  if (hasConnectionError) {
    return (
      <div className="practice-game error-state">
        <div className="error-content">
          <h2>Connection Error</h2>
          <p>Unable to connect to the game server. Please check your connection and try again.</p>
          <div className="error-actions">
            <button onClick={() => startNewGame()} className="retry-btn">
              🔄 Retry
            </button>
            <button onClick={() => navigate('/menu')} className="menu-btn">
              ← Back to Menu
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="practice-game">
      <div className="game-header">
        <button 
          className="back-btn"
          onClick={() => navigate('/menu')}
        >
          ← Back to Menu
        </button>
        
        <div className="game-info">
          <h1>Practice Mode</h1>
          <div className="difficulty-selector">
            {['easy', 'medium', 'hard'].map(diff => (
              <button
                key={diff}
                className={`difficulty-btn ${difficulty === diff ? 'active' : ''}`}
                onClick={() => startNewGame(diff)}
                disabled={isLoading}
              >
                {diff.charAt(0).toUpperCase() + diff.slice(1)}
              </button>
            ))}
          </div>
        </div>

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
          <span className="user-name">{user.name}</span>
        </div>
      </div>

      <div className="game-content">
        {isLoading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Starting new game...</p>
          </div>
        ) : (
          <>
            <div className="wordle-grid">
              {grid.map((row, rowIndex) => (
                <div key={rowIndex} className="grid-row">
                  {row.map((letter, colIndex) => (
                    <div
                      key={colIndex}
                      className={`grid-cell ${colors[rowIndex][colIndex]} ${
                        rowIndex === currentRow && colIndex === currentCol ? 'active' : ''
                      }`}
                    >
                      {letter}
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {message && (
              <div className={`game-message ${isGameOver ? 'game-over' : ''}`}>
                {message}
              </div>
            )}

            {isGameOver && (
              <div className="game-actions">
                <button onClick={() => startNewGame()} className="new-game-btn">
                  🎮 Play Again
                </button>
                <button onClick={() => navigate('/stats')} className="stats-btn">
                  📊 View Stats
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="game-instructions">
        <p>
          <strong>How to play:</strong> Guess the {wordLength}-letter word in {MAX_GUESSES} tries. 
          Type letters and press Enter to submit. Colors will help guide your next guess!
        </p>
      </div>
    </div>
  );
}

export default PracticeGame;
