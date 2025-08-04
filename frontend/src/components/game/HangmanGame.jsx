import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../utils/config';
import { authUtils } from '../../services/authService';
import gameDebugManager from '../../utils/debugUtils';
import './HangmanGame.css';

function HangmanGame({ user }) {
  const [difficulty, setDifficulty] = useState('medium');
  const [gameId, setGameId] = useState(null);
  const [displayWord, setDisplayWord] = useState('');
  const [remainingGuesses, setRemainingGuesses] = useState(0);
  const [guessedLetters, setGuessedLetters] = useState([]);
  const [currentGuess, setCurrentGuess] = useState('');
  const [wordGuess, setWordGuess] = useState('');
  const [isGameOver, setIsGameOver] = useState(false);
  const [isWon, setIsWon] = useState(false);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [hasConnectionError, setHasConnectionError] = useState(false);
  const [showWordGuessInput, setShowWordGuessInput] = useState(false);
  const [wordLength, setWordLength] = useState(0);
  const [revealedWord, setRevealedWord] = useState(null);
  const navigate = useNavigate();

  // API call utility with auth handling
  const apiCall = async (endpoint, options = {}) => {
    return await authUtils.apiCall(endpoint, options, navigate);
  };

  // Start a new hangman game
  const startNewGame = async (newDifficulty = difficulty) => {
    setIsLoading(true);
    setDifficulty(newDifficulty);
    setHasConnectionError(false);
    
    try {
      const data = await apiCall(`/api/hangman/start`, {
        method: 'POST',
        body: JSON.stringify({ difficulty: newDifficulty }),
      });

      if (data === null) return; // Auth failure, user will be redirected

      console.info(`Hangman: Started ${newDifficulty} game (${data.word_length} letters)`);
      
      setGameId(data.game_id);
      setDisplayWord(data.display_word);
      setRemainingGuesses(data.remaining_guesses);
      setGuessedLetters(data.guessed_letters);
      setWordLength(data.word_length);
      setIsGameOver(data.is_game_over);
      setIsWon(data.is_won);
      setMessage('');
      setCurrentGuess('');
      setWordGuess('');
      setShowWordGuessInput(false);
      setRevealedWord(null);
      
      setIsLoading(false);
    } catch (error) {
      console.error('Hangman: Failed to start game', error);
      setHasConnectionError(true);
      setMessage('Failed to start game. Please try again.');
      setIsLoading(false);
    }
  };

  // Submit a letter guess
  const submitLetterGuess = async () => {
    if (!currentGuess || currentGuess.length !== 1 || !gameId) return;

    try {
      const data = await apiCall(`/api/hangman/guess`, {
        method: 'POST',
        body: JSON.stringify({ 
          game_id: gameId, 
          guess: currentGuess.toLowerCase() 
        }),
      });

      if (data === null) return;

      setDisplayWord(data.display_word);
      setRemainingGuesses(data.remaining_guesses);
      setGuessedLetters(data.guessed_letters);
      setIsGameOver(data.is_game_over);
      setIsWon(data.is_won);
      setMessage(data.message);
      setCurrentGuess('');
      
      if (data.is_game_over && data.word) {
        setRevealedWord(data.word);
      }
      
    } catch (error) {
      console.error('Hangman: Letter guess failed', error);
      setMessage('Failed to submit guess. Please try again.');
    }
  };

  // Submit a word guess
  const submitWordGuess = async () => {
    if (!wordGuess || !gameId) return;

    try {
      const data = await apiCall(`/api/hangman/guess-word`, {
        method: 'POST',
        body: JSON.stringify({ 
          game_id: gameId, 
          word_guess: wordGuess.toLowerCase() 
        }),
      });

      if (data === null) return;

      setDisplayWord(data.display_word);
      setRemainingGuesses(data.remaining_guesses);
      setGuessedLetters(data.guessed_letters);
      setIsGameOver(data.is_game_over);
      setIsWon(data.is_won);
      setMessage(data.message);
      setWordGuess('');
      setShowWordGuessInput(false);
      
      if (data.is_game_over && data.word) {
        setRevealedWord(data.word);
      }
      
    } catch (error) {
      console.error('Hangman: Word guess failed', error);
      setMessage('Failed to submit word guess. Please try again.');
    }
  };

  // Get a hint
  const getHint = async () => {
    if (!gameId || isGameOver) return;

    try {
      const data = await apiCall(`/api/hangman/hint`, {
        method: 'POST',
        body: JSON.stringify({ game_id: gameId }),
      });

      if (data === null) return;

      setDisplayWord(data.display_word);
      setGuessedLetters(data.guessed_letters);
      setIsGameOver(data.is_game_over);
      setIsWon(data.is_won);
      setMessage(data.message);
      
      if (data.is_game_over && data.word) {
        setRevealedWord(data.word);
      }
      
    } catch (error) {
      console.error('Hangman: Hint request failed', error);
      setMessage('Failed to get hint. Please try again.');
    }
  };

  // Handle keyboard input
  const handleKeyPress = useCallback((event) => {
    if (isGameOver) return;

    const key = event.key.toLowerCase();
    
    if (key === 'enter') {
      if (showWordGuessInput) {
        submitWordGuess();
      } else {
        submitLetterGuess();
      }
    } else if (key === 'escape') {
      setShowWordGuessInput(false);
      setWordGuess('');
    } else if (key === 'backspace') {
      if (showWordGuessInput) {
        setWordGuess(prev => prev.slice(0, -1));
      } else {
        setCurrentGuess('');
      }
    } else if (/^[a-z]$/.test(key)) {
      if (showWordGuessInput) {
        setWordGuess(prev => prev + key);
      } else if (!guessedLetters.includes(key)) {
        setCurrentGuess(key);
      }
    }
  }, [isGameOver, showWordGuessInput, submitLetterGuess, submitWordGuess, guessedLetters]);

  // Console command to reveal answer (development only)
  const revealAnswer = async () => {
    // Temporarily removing dev check for testing
    // if (!import.meta.env.DEV) {
    //   console.warn('Debug commands are only available in development mode');
    //   return;
    // }

    if (!gameId) {
      console.warn('Hangman Debug: No active game session');
      return;
    }

    try {
      const data = await apiCall(`/api/hangman/debug/answer/${gameId}`);
      if (data === null) return; // Auth failure

      console.log('HANGMAN ANSWER:', data.answer);
      console.info('Game Info:', {
        answer: data.answer,
        gameId: data.game_id,
        difficulty: data.difficulty,
        wordLength: data.word_length,
        remainingGuesses: data.remaining_guesses
      });
      
    } catch (error) {
      console.error('Hangman Debug: Failed to retrieve answer', error);
    }
  };

  // Set up debug console commands
  useEffect(() => {
    // Register with universal debug manager
    if (gameId) {
      gameDebugManager.setActiveGame('hangman', { gameId, difficulty });
    }

    // Set up debug commands (temporarily always enabled for testing)
    window.revealHangmanAnswer = revealAnswer;
    
    return () => {
      if (window.hasOwnProperty('revealHangmanAnswer')) delete window.revealHangmanAnswer;
      if (!gameId) gameDebugManager.clearActiveGame();
    };
  }, [gameId]);

  // Initialize game on component mount
  useEffect(() => {
    startNewGame();
  }, []);

  // Add keyboard event listener
  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  // Generate alphabet buttons
  const generateAlphabet = () => {
    const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
    return alphabet.map(letter => (
      <button
        key={letter}
        className={`alphabet-btn ${guessedLetters.includes(letter) ? 'used' : ''}`}
        onClick={() => {
          if (!guessedLetters.includes(letter) && !isGameOver) {
            setCurrentGuess(letter);
          }
        }}
        disabled={guessedLetters.includes(letter) || isGameOver}
      >
        {letter.toUpperCase()}
      </button>
    ));
  };

  // Generate hangman drawing based on wrong guesses
  const getHangmanDrawing = () => {
    const maxGuesses = Math.max(5, 8 - difficulty.length); // Approximate based on difficulty
    const wrongGuesses = maxGuesses - remainingGuesses;
    
    const parts = [
      '  +---+',
      '  |   |',
      '  |   ' + (wrongGuesses > 0 ? 'O' : ''),
      '  |  ' + (wrongGuesses > 2 ? '/' : ' ') + (wrongGuesses > 1 ? '|' : '') + (wrongGuesses > 3 ? '\\' : ''),
      '  |  ' + (wrongGuesses > 4 ? '/' : '') + ' ' + (wrongGuesses > 5 ? '\\' : ''),
      '  |',
      '======'
    ];
    
    return parts.join('\n');
  };

  if (isLoading) {
    return (
      <div className="hangman-game loading">
        <div className="loading-spinner">Loading Hangle...</div>
      </div>
    );
  }

  if (hasConnectionError) {
    return (
      <div className="hangman-game error">
        <div className="error-message">
          <h2>Connection Error</h2>
          <p>Unable to connect to the game server.</p>
          <button onClick={() => startNewGame()} className="retry-btn">
            Retry
          </button>
          <button onClick={() => navigate('/menu')} className="back-btn">
            Back to Menu
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="hangman-game">
      <div className="game-header">
        <h1>Hangle</h1>
        <div className="user-info">
          Welcome, {user?.name || user?.username || 'Player'}!
        </div>
      </div>

      <div className="game-controls">
        <div className="difficulty-selector">
          <label>Difficulty:</label>
          <select 
            value={difficulty} 
            onChange={(e) => setDifficulty(e.target.value)}
            //disabled={isGameOver}
          >
            <option value="easy">Easy (4-5 letters, 8 guesses)</option>
            <option value="medium">Medium (6-7 letters, 7 guesses)</option>
            <option value="hard">Hard (8 letters, 6 guesses)</option>
            <option value="extreme">Extreme (9+ letters, 5 guesses)</option>
          </select>
        </div>
        
        <button 
          onClick={() => startNewGame(difficulty)} 
          className="new-game-btn"
        >
          New Game
        </button>
        
        <button 
          onClick={() => navigate('/menu')} 
          className="back-btn"
        >
          Back to Menu
        </button>
      </div>

      <div className="game-area">
        <div className="hangman-display">
          <pre className="hangman-ascii">{getHangmanDrawing()}</pre>
        </div>

        <div className="game-info">
          <div className="word-display">
            <h2>{displayWord}</h2>
            <p>Word Length: {wordLength} letters</p>
            {revealedWord && (
              <p className="revealed-word">The word was: <strong>{revealedWord}</strong></p>
            )}
          </div>
          
          <div className="game-status">
            <p>Remaining Guesses: <span className="remaining-count">{remainingGuesses}</span></p>
            <p>Difficulty: <span className="difficulty-badge">{difficulty}</span></p>
          </div>

          {message && (
            <div className={`message ${isGameOver ? (isWon ? 'success' : 'failure') : 'info'}`}>
              {message}
            </div>
          )}
        </div>
      </div>

      <div className="input-area">
        {!showWordGuessInput ? (
          <div className="letter-input">
            <h3>Guess a Letter:</h3>
            <div className="current-guess">
              <input
                type="text"
                value={currentGuess}
                onChange={(e) => {
                  const value = e.target.value.toLowerCase();
                  if (value.length <= 1 && /^[a-z]*$/.test(value)) {
                    setCurrentGuess(value);
                  }
                }}
                placeholder="Enter a letter"
                maxLength={1}
                disabled={isGameOver}
                className="guess-input"
              />
              <button 
                onClick={submitLetterGuess} 
                disabled={!currentGuess || isGameOver}
                className="submit-btn"
              >
                Guess Letter
              </button>
            </div>
            
            <div className="game-actions">
              <button 
                onClick={() => setShowWordGuessInput(true)} 
                disabled={isGameOver}
                className="word-guess-btn"
              >
                Guess Whole Word
              </button>
              
              <button 
                onClick={getHint} 
                disabled={isGameOver}
                className="hint-btn"
              >
                Get Hint
              </button>
            </div>
          </div>
        ) : (
          <div className="word-input">
            <h3>Guess the Word:</h3>
            <div className="word-guess">
              <input
                type="text"
                value={wordGuess}
                onChange={(e) => setWordGuess(e.target.value.toLowerCase())}
                placeholder="Enter the complete word"
                disabled={isGameOver}
                className="word-input-field"
              />
              <button 
                onClick={submitWordGuess} 
                disabled={!wordGuess || isGameOver}
                className="submit-btn"
              >
                Guess Word
              </button>
              <button 
                onClick={() => {
                  setShowWordGuessInput(false);
                  setWordGuess('');
                }} 
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
            <p className="word-guess-warning">
              Warning: Wrong word guess costs 2 guesses!
            </p>
          </div>
        )}
      </div>

      <div className="alphabet-section">
        <h3>Letters:</h3>
        <div className="alphabet-grid">
          {generateAlphabet()}
        </div>
        {guessedLetters.length > 0 && (
          <div className="guessed-letters">
            <p>Guessed: {guessedLetters.join(', ').toUpperCase()}</p>
          </div>
        )}
      </div>

      {isGameOver && (
        <div className="game-over">
          <h2>{isWon ? 'Congratulations! 🎉' : 'Game Over 😞'}</h2>
          <button onClick={() => startNewGame(difficulty)} className="play-again-btn">
            Play Again
          </button>
        </div>
      )}
    </div>
  );
}

export default HangmanGame;
