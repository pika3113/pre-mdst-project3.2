import React, { useState } from 'react';
import AuthModal from '../components/auth/AuthModal';
import './LandingPage.css';

function LandingPage({ onAuthSuccess }) {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [hoveredGame, setHoveredGame] = useState(null);

  const games = [
    {
      id: 'wordle',
      title: 'Wordle',
      subtitle: 'Guess the 5-letter word',
      description: 'The classic word-guessing game that started it all. Use clues to find the hidden word in 6 tries!',
      icon: '🔤',
      color: 'linear-gradient(135deg, #6aaa64 0%, #5a9a54 100%)',
      demo: ['W', 'O', 'R', 'D', 'S'],
      demoColors: ['correct', 'correct', 'correct', 'correct', 'correct'],
      difficulty: 'Medium',
      players: '1,247',
      badge: 'CLASSIC'
    },
    {
      id: 'hangman',
      title: 'Hangle',
      subtitle: 'Save the stick figure',
      description: 'Guess letters to reveal the hidden word before the drawing is complete. Every wrong guess adds a line!',
      icon: '🎪',
      color: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)',
      demo: ['H', 'A', 'N', 'G', '_'],
      demoColors: ['correct', 'correct', 'correct', 'correct', 'absent'],
      difficulty: 'Easy',
      players: '892',
      badge: 'CLASSIC'
    },
    {
      id: 'morphle',
      title: 'Morphle',
      subtitle: 'Morph words into words',
      description: 'Transform one word into another by changing one letter at a time. Create chains of valid words!',
      icon: '🔄',
      color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      demo: ['M', 'O', 'R', 'P', 'H'],
      demoColors: ['present', 'present', 'correct', 'present', 'present'],
      difficulty: 'Hard',
      players: '456',
      badge: 'NEW'
    }
  ];

  const handleGameClick = (gameId) => {
    if (!showAuthModal) {
      setShowAuthModal(true);
    }
  };

  return (
    <div className="landing-page">
      <div className="landing-background">
        {/* Animated background elements */}
        <div className="bg-decoration">
          <div className="floating-letters">
            {['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map((letter, i) => (
              <span key={i} className={`floating-letter letter-${i}`}>{letter}</span>
            ))}
          </div>
        </div>

        <div className="landing-content">
          {/* Header Section */}
          <div className="landing-header">
            <h1 className="landing-title">
              Word<span className="title-accent">Games</span> Hub
            </h1>
            <p className="landing-subtitle">
              Master the art of words with our collection of brain-teasing games.
              <br />
              Challenge yourself, compete with friends, and climb the leaderboards!
            </p>
          </div>

          {/* Games Grid */}
          <div className="games-grid">
            {games.map((game) => (
              <div 
                key={game.id}
                className={`game-card ${hoveredGame === game.id ? 'hovered' : ''}`}
                onMouseEnter={() => setHoveredGame(game.id)}
                onMouseLeave={() => setHoveredGame(null)}
                onClick={() => handleGameClick(game.id)}
                style={{ '--game-color': game.color }}
              >
                <div className="game-card-inner">
                  {/* Game Badge */}
                  <div className="game-badge">{game.badge}</div>
                  
                  {/* Game Icon */}
                  <div className="game-icon">{game.icon}</div>
                  
                  {/* Game Info */}
                  <div className="game-info">
                    <h3 className="game-title">{game.title}</h3>
                    <p className="game-subtitle">{game.subtitle}</p>
                    <p className="game-description">{game.description}</p>
                  </div>

                  {/* Game Demo */}
                  <div className="game-demo">
                    <div className="demo-word">
                      {game.demo.map((letter, i) => (
                        <span 
                          key={i} 
                          className={`demo-letter ${game.demoColors[i]}`}
                          style={{ animationDelay: `${i * 0.1}s` }}
                        >
                          {letter}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Game Stats */}
                  {/* <div className="game-stats">
                    <div className="stat">
                      <span className="stat-label">Difficulty</span>
                      <span className="stat-value">{game.difficulty}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Playing Now</span>
                      <span className="stat-value">{game.players}</span>
                    </div>
                  </div> */}

                  {/* Play Button */}
                  {/* <div className="game-action">
                    <button className="play-btn">
                      <span>Play Now</span>
                      <div className="btn-glow"></div>
                    </button>
                  </div> */}
                  
                </div>

                {/* Hover Effect */}
                <div className="card-glow"></div>
              </div>
            ))}
          </div>

          {/* Bottom Section */}
          <div className="landing-bottom">
            <div className="features-grid">
              <div className="feature-item">
                <div className="feature-icon">🏆</div>
                <span>Global Leaderboards</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">📊</div>
                <span>Progress Tracking</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🎯</div>
                <span>Daily Challenges</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">👥</div>
                <span>Multiplayer Modes</span>
              </div>
            </div>

            <div className="auth-prompt">
              <p>Ready to start your word journey?</p>
              <button 
                className="get-started-btn"
                onClick={() => setShowAuthModal(true)}
              >
                <span>Sign In to Play</span>
                <div className="btn-shine"></div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onAuthSuccess={(userData) => {
          setShowAuthModal(false);
          onAuthSuccess(userData);
        }}
      />
    </div>
  );
}

export default LandingPage;
