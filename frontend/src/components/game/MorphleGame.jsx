import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MorphleGame.css';

function MorphleGame({ user }) {
  const navigate = useNavigate();

  return (
    <div className="morphle-game">
      <div className="game-header">
        <h1>Mophle Game</h1>
        <div className="user-info">
          Welcome, {user?.name || user?.username || 'Player'}!
        </div>
      </div>

      <div className="game-controls">
        <button 
          onClick={() => navigate('/menu')} 
          className="back-btn"
        >
          Back to Menu
        </button>
      </div>

      <div className="coming-soon">
        <div className="coming-soon-content">
          <div className="icon">🔄</div>
          <h2>Mophle Coming Soon!</h2>
          <p>Transform words step by step in this exciting new word game.</p>
          <p>We're working hard to bring you this amazing experience.</p>
          
          <div className="features">
            <h3>What to expect:</h3>
            <ul>
              <li>🔄 Transform one word into another</li>
              <li>📝 Change one letter at a time</li>
              <li>🎯 Multiple difficulty levels</li>
              <li>⏱️ Time challenges</li>
              <li>🏆 Score tracking</li>
            </ul>
          </div>

          <div className="cta">
            <p>In the meantime, try our other games:</p>
            <div className="game-buttons">
              <button 
                onClick={() => navigate('/practice')} 
                className="game-btn wordle-btn"
              >
                🔤 Play Wordle
              </button>
              <button 
                onClick={() => navigate('/hangman')} 
                className="game-btn hangman-btn"
              >
                🎪 Play Hangle
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MorphleGame;
