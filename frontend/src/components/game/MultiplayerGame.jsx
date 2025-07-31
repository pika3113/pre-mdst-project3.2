import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './MultiplayerGame.css';

function MultiplayerGame({ user }) {
  const [gameMode, setGameMode] = useState('lobby'); // lobby, queue, game
  const navigate = useNavigate();

  const handleCreateRoom = () => {
    // TODO: Implement room creation
    console.log('Creating room...');
  };

  const handleJoinRoom = () => {
    // TODO: Implement room joining
    console.log('Joining room...');
  };

  const handleQuickPlay = () => {
    // TODO: Implement matchmaking
    setGameMode('queue');
    setTimeout(() => {
      // Simulate finding a match
      setGameMode('game');
    }, 3000);
  };

  if (gameMode === 'queue') {
    return (
      <div className="multiplayer-game">
        <div className="queue-screen">
          <div className="queue-content">
            <div className="queue-spinner"></div>
            <h2>Finding an opponent...</h2>
            <p>Please wait while we match you with another player</p>
            <button 
              className="cancel-btn"
              onClick={() => setGameMode('lobby')}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (gameMode === 'game') {
    return (
      <div className="multiplayer-game">
        <div className="multiplayer-content">
          <div className="game-header">
            <button onClick={() => navigate('/menu')} className="back-btn">
              ← Back to Menu
            </button>
            <h1>Multiplayer Battle</h1>
          </div>
          
          <div className="battle-arena">
            <div className="player-section">
              <div className="player-info">
                <div className="player-avatar">
                  {user.picture ? (
                    <img src={user.picture} alt={user.name} />
                  ) : (
                    <div className="avatar-placeholder">
                      {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                    </div>
                  )}
                </div>
                <h3>{user.name || 'You'}</h3>
              </div>
              
              <div className="game-grid">
                {/* Player's game grid would go here */}
                <div className="coming-soon-overlay">
                  <h3>🚧 Under Construction</h3>
                  <p>Multiplayer battles coming soon!</p>
                </div>
              </div>
            </div>

            <div className="vs-divider">
              <div className="vs-text">VS</div>
            </div>

            <div className="opponent-section">
              <div className="player-info">
                <div className="player-avatar">
                  <div className="avatar-placeholder">O</div>
                </div>
                <h3>Opponent</h3>
              </div>
              
              <div className="game-grid">
                {/* Opponent's game grid would go here */}
                <div className="coming-soon-overlay">
                  <h3>🎮 Real-time Battles</h3>
                  <p>Race against friends to solve the word first!</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="multiplayer-game">
      <div className="multiplayer-lobby">
        <div className="lobby-header">
          <button onClick={() => navigate('/menu')} className="back-btn">
            ← Back to Menu
          </button>
          <h1>Multiplayer Lobby</h1>
        </div>

        <div className="lobby-content">
          <div className="multiplayer-modes">
            <div className="mode-card" onClick={handleQuickPlay}>
              <div className="mode-icon">⚡</div>
              <h3>Quick Play</h3>
              <p>Get matched with a random opponent instantly</p>
              <div className="mode-status available">Ready to play</div>
            </div>

            <div className="mode-card disabled" onClick={handleCreateRoom}>
              <div className="mode-icon">🏠</div>
              <h3>Create Room</h3>
              <p>Create a private room and invite friends</p>
              <div className="mode-status coming-soon">Coming Soon</div>
            </div>

            <div className="mode-card disabled" onClick={handleJoinRoom}>
              <div className="mode-icon">🚪</div>
              <h3>Join Room</h3>
              <p>Enter a room code to join friends</p>
              <div className="mode-status coming-soon">Coming Soon</div>
            </div>
          </div>

          <div className="lobby-info">
            <div className="info-section">
              <h3>🏆 How Multiplayer Works</h3>
              <ul>
                <li>Both players get the same word to guess</li>
                <li>First to solve it wins the round</li>
                <li>Gain points for wins and climb the leaderboard</li>
                <li>Challenge friends in private rooms</li>
              </ul>
            </div>

            <div className="online-players">
              <h3>🌍 Players Online</h3>
              <div className="player-count">
                <span className="count-number">42</span>
                <span className="count-label">players online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MultiplayerGame;
