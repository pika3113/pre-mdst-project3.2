import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../utils/config';
import { authUtils } from '../../services/authService';
import gameDebugManager from '../../utils/debugUtils';
import './WordleGame.css';

const MAX_GUESSES = 6;

function WordleGame({ user }) {
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

  // API call utility with auth handling
  const apiCall = async (endpoint, options = {}) => {
    return await authUtils.apiCall(endpoint, options, navigate);
  };

  // Start a new game
  const startNewGame = async (newDifficulty = difficulty) => {
    setIsLoading(true);
    setDifficulty(newDifficulty);
    setHasConnectionError(false);
    
    try {
      const data = await apiCall(`/api/wordle/start`, {
        method: 'POST',
        body: JSON.stringify({ difficulty: newDifficulty }),
      });

      if (data === null) return; // Auth failure, user will be redirected

      console.info(`Wordle: Started ${newDifficulty} game (${data.word_length} letters)`);
      
      setSessionId(data.game_id);
      setWordLength(data.word_length);
      initializeGrids(data.word_length);
      setCurrentRow(0);
      setCurrentCol(0);
      setIsGameOver(false);
      setMessage('');
    } catch (error) {
      console.error('Wordle: Failed to start game', error);
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
      const data = await apiCall(`/api/wordle/guess`, {
        method: 'POST',
        body: JSON.stringify({
          game_id: sessionId,
          guess: guess
        }),
      });

      if (data === null) return; // Auth failure, user will be redirected

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
        setMessage('Congratulations! You guessed it!');
        setIsGameOver(true);
      } else if (data.game_over) {
        setMessage(data.message || `Game over! The word was: ${data.word || 'unknown'}`);
        setIsGameOver(true);
      } else {
        setCurrentRow(currentRow + 1);
        setCurrentCol(0);
      }
    } catch (error) {
      console.error('Wordle: Guess submission failed', error);
      
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

  // Console command to reveal answer (development only)
  const revealAnswer = async () => {
    // Temporarily removing dev check for testing
    // if (!import.meta.env.DEV) {
    //   console.warn('Debug commands are only available in development mode');
    //   return;
    // }

    if (!sessionId) {
      console.warn('Wordle Debug: No active game session');
      return;
    }

    try {
      const data = await apiCall(`/api/wordle/debug/answer/${sessionId}`);
      if (data === null) return; // Auth failure

      console.log('WORDLE ANSWER:', data.answer);
      console.info('Game Info:', {
        answer: data.answer,
        gameId: data.game_id,
        difficulty: data.difficulty,
        wordLength: data.word_length,
        guessesRemaining: MAX_GUESSES - currentRow
      });
      
    } catch (error) {
      console.error('Wordle Debug: Failed to retrieve answer', error);
    }
  };

  // Set up debug console commands (development only)
  useEffect(() => {
    // Register with universal debug manager
    if (sessionId) {
      gameDebugManager.setActiveGame('wordle', { sessionId, difficulty });
    }

    // Set up debug commands (temporarily always enabled for testing)
    window.revealWordleAnswer = revealAnswer;

    return () => {
      if (window.hasOwnProperty('revealWordleAnswer')) delete window.revealWordleAnswer;
      if (!sessionId) gameDebugManager.clearActiveGame();
    };
  }, [sessionId]);

  if (hasConnectionError) {
    return (
      <div className="wordle-game error-state">
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
    <div className="wordle-game">
      <div className="game-header">
        <button 
          className="back-btn"
          onClick={() => navigate('/menu')}
        >
          ← Back to Menu
        </button>
        
        <div className="game-info">
          <h1>Wordle</h1>
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
                  Play Again
                </button>
                <button onClick={() => {
                  // Set a flag to indicate legitimate navigation to stats
                  sessionStorage.setItem('allowStatsAccess', 'true');
                  navigate('/profile?tab=stats');
                }} className="stats-btn">
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

export default WordleGame;
