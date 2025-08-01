import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authUtils } from '../../services/authService';
import './MorphleGame.css';

function MorphleGame({ user }) {
  const navigate = useNavigate();
  
  // API call utility with auth handling
  const apiCall = async (endpoint, options = {}) => {
    return await authUtils.apiCall(endpoint, options, navigate);
  };
  
  // Game state
  const [gameState, setGameState] = useState('menu'); // 'menu', 'playing', 'completed', 'loading'
  const [currentGame, setCurrentGame] = useState(null);
  const [currentWord, setCurrentWord] = useState('');
  const [targetWord, setTargetWord] = useState('');
  const [userInput, setUserInput] = useState('');
  const [moveCount, setMoveCount] = useState(0);
  const [hintCost, setHintCost] = useState(10);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info'); // 'success', 'error', 'info', 'warning'
  const [gameStats, setGameStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Timer effect
  useEffect(() => {
    let interval;
    if (gameState === 'playing' && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    }
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [gameState, startTime]);

  const startNewGame = async (difficulty) => {
    setLoading(true);
    setMessage('');
    
    try {
      const response = await apiCall('/api/morphle/start', {
        method: 'POST',
        body: JSON.stringify({ difficulty }),
      });
      setCurrentGame(response);
      setCurrentWord(response.start_word);
      setTargetWord(response.target_word);
      setMoveCount(0);
      setHintCost(response.hint_cost);
      setUserInput('');
      setGameState('playing');
      setStartTime(Date.now());
      setElapsedTime(0);
      setMessage(`Transform "${response.start_word.toUpperCase()}" into "${response.target_word.toUpperCase()}" in ${response.ideal_steps} steps!`);
      setMessageType('info');
    } catch (error) {
      setMessage(error.message);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const submitMove = async () => {
    if (!userInput.trim() || !currentGame) return;
    
    setLoading(true);
    try {
      const response = await apiCall('/api/morphle/move', {
        method: 'POST',
        body: JSON.stringify({ 
          game_id: currentGame.game_id, 
          move: userInput.trim() 
        }),
      });
      
      if (response.success) {
        setCurrentWord(response.current_word);
        setMoveCount(response.move_count);
        setUserInput('');
        
        if (response.is_complete) {
          setGameState('completed');
          const stats = await apiCall(`/api/morphle/game/${currentGame.game_id}/completion`);
          setGameStats(stats);
          setMessage('Congratulations! You completed the puzzle!');
          setMessageType('success');
        } else {
          setMessage('Great move! Keep going!');
          setMessageType('success');
        }
      } else {
        setMessage(response.message);
        setMessageType('error');
      }
    } catch (error) {
      setMessage(error.message);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const getHint = async () => {
    if (!currentGame) return;
    
    setLoading(true);
    try {
      const response = await apiCall('/api/morphle/hint', {
        method: 'POST',
        body: JSON.stringify({ game_id: currentGame.game_id }),
      });
      
      if (response.hint) {
        setMessage(`Hint: Try "${response.hint.toUpperCase()}" (Cost: $${response.cost})`);
        setMessageType('warning');
        setHintCost(hintCost + 10); // Approximate increment
      } else {
        setMessage(response.message);
        setMessageType('info');
      }
    } catch (error) {
      setMessage(error.message);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const resetGame = () => {
    setGameState('menu');
    setCurrentGame(null);
    setCurrentWord('');
    setTargetWord('');
    setUserInput('');
    setMoveCount(0);
    setHintCost(10);
    setMessage('');
    setGameStats(null);
    setStartTime(null);
    setElapsedTime(0);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && userInput.trim() && !loading) {
      submitMove();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Menu screen
  if (gameState === 'menu') {
    return (
      <div className="morphle-game">
        <div className="game-header">
          <h1>🔄 Morphle</h1>
          <div className="user-info">
            Welcome, {user?.name || user?.username || 'Player'}!
          </div>
        </div>

        <div className="game-controls">
          <button 
            onClick={() => navigate('/menu')} 
            className="back-btn"
          >
            ← Back to Menu
          </button>
        </div>

        <div className="difficulty-selection">
          <div className="difficulty-content">
            <h2>Choose Your Challenge</h2>
            <p>Transform one word into another by changing one letter at a time!</p>
            
            <div className="difficulty-options">
              <button 
                onClick={() => startNewGame('easy')} 
                className="difficulty-btn easy"
                disabled={loading}
              >
                <div className="difficulty-icon">🌱</div>
                <h3>Easy</h3>
                <p>4 letters • $30 reward</p>
              </button>
              
              <button 
                onClick={() => startNewGame('normal')} 
                className="difficulty-btn normal"
                disabled={loading}
              >
                <div className="difficulty-icon">⚡</div>
                <h3>Normal</h3>
                <p>5 letters • $40 reward</p>
              </button>
              
              <button 
                onClick={() => startNewGame('hard')} 
                className="difficulty-btn hard"
                disabled={loading}
              >
                <div className="difficulty-icon">🔥</div>
                <h3>Hard</h3>
                <p>6 letters • $50 reward</p>
              </button>
            </div>

            <div className="game-rules">
              <h3>How to Play:</h3>
              <ul>
                <li>🔄 Transform the start word into the target word</li>
                <li>📝 Change only one letter at a time</li>
                <li>✅ Each step must be a valid English word</li>
                <li>⏱️ Faster completion = time bonus!</li>
                <li>💡 Use hints if you get stuck (for a cost)</li>
                <li>🏆 Perfect runs get streak bonuses!</li>
              </ul>
            </div>
          </div>
        </div>

        {loading && <div className="loading">Starting game...</div>}
      </div>
    );
  }

  // Game playing screen
  if (gameState === 'playing') {
    return (
      <div className="morphle-game">
        <div className="game-header">
          <h1>🔄 Morphle</h1>
          <div className="game-info">
            <div className="info-item">
              <span className="label">Time:</span>
              <span className="value">{formatTime(elapsedTime)}</span>
            </div>
            <div className="info-item">
              <span className="label">Moves:</span>
              <span className="value">{moveCount}</span>
            </div>
            <div className="info-item">
              <span className="label">Target:</span>
              <span className="value">{currentGame?.ideal_steps || 0}</span>
            </div>
          </div>
        </div>

        <div className="game-board">
          <div className="word-display">
            <div className="current-word">
              <label>Current Word:</label>
              <div className="word">{currentWord.toUpperCase()}</div>
            </div>
            
            <div className="arrow">→</div>
            
            <div className="target-word">
              <label>Target Word:</label>
              <div className="word">{targetWord.toUpperCase()}</div>
            </div>
          </div>

          <div className="input-section">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value.toLowerCase())}
              onKeyPress={handleKeyPress}
              placeholder="Enter your next word..."
              className="word-input"
              maxLength={currentGame?.word_length || 5}
              disabled={loading}
            />
            
            <div className="action-buttons">
              <button
                onClick={submitMove}
                disabled={!userInput.trim() || loading}
                className="submit-btn"
              >
                {loading ? 'Submitting...' : 'Submit Move'}
              </button>
              
              <button
                onClick={getHint}
                disabled={loading}
                className="hint-btn"
              >
                💡 Hint (${hintCost})
              </button>
            </div>
          </div>

          {message && (
            <div className={`game-message ${messageType}`}>
              {message}
            </div>
          )}
        </div>

        <div className="game-controls">
          <button onClick={resetGame} className="quit-btn">
            🏃 Quit Game
          </button>
        </div>
      </div>
    );
  }

  // Game completed screen
  if (gameState === 'completed') {
    return (
      <div className="morphle-game">
        <div className="game-header">
          <h1>🎉 Puzzle Complete!</h1>
        </div>

        <div className="completion-stats">
          <div className="stats-content">
            <div className="celebration-icon">🏆</div>
            
            <h2>Congratulations!</h2>
            <p>You successfully transformed "{currentGame?.start_word.toUpperCase()}" into "{targetWord.toUpperCase()}"!</p>

            {gameStats && (
              <div className="stats-breakdown">
                <div className="stat-row">
                  <span>Time:</span>
                  <span>{formatTime(gameStats.duration)}</span>
                </div>
                <div className="stat-row">
                  <span>Moves:</span>
                  <span>{gameStats.move_count}</span>
                </div>
                <div className="stat-row">
                  <span>Target:</span>
                  <span>{gameStats.ideal_steps}</span>
                </div>
                <div className="stat-divider"></div>
                <div className="stat-row">
                  <span>Base Reward:</span>
                  <span>${gameStats.base_reward}</span>
                </div>
                {gameStats.time_bonus > 0 && (
                  <div className="stat-row bonus">
                    <span>Time Bonus:</span>
                    <span>+${gameStats.time_bonus}</span>
                  </div>
                )}
                {gameStats.streak_bonus > 0 && (
                  <div className="stat-row bonus">
                    <span>Perfect Streak:</span>
                    <span>+${gameStats.streak_bonus}</span>
                  </div>
                )}
                <div className="stat-divider"></div>
                <div className="stat-row total">
                  <span>Total Earnings:</span>
                  <span>${gameStats.total_earnings}</span>
                </div>
              </div>
            )}

            {gameStats?.ideal_path && (
              <div className="ideal-path">
                <h3>Optimal Path:</h3>
                <div className="path-display">
                  {gameStats.ideal_path.map((word, index) => (
                    <span key={index} className="path-word">
                      {word.toUpperCase()}
                      {index < gameStats.ideal_path.length - 1 && ' → '}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="completion-actions">
              <button onClick={resetGame} className="play-again-btn">
                🔄 Play Again
              </button>
              <button onClick={() => navigate('/menu')} className="menu-btn">
                🏠 Back to Menu
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default MorphleGame;
