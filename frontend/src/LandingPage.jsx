import React, { useState } from 'react';
import AuthModal from './AuthModal';
import './LandingPage.css';

function LandingPage({ onAuthSuccess }) {
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <div className="landing-page">
      <div className="landing-background">
        <div className="landing-content">
          <div className="landing-header">
            <h1 className="landing-title">Wordle Multiplayer</h1>
            <p className="landing-subtitle">
              Challenge friends, climb leaderboards, and master the art of word guessing
            </p>
          </div>

          <div className="landing-features">
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Practice Mode</h3>
              <p>Hone your skills with unlimited solo games</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🏆</div>
              <h3>Multiplayer Battles</h3>
              <p>Race against friends in real-time word battles</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Global Leaderboards</h3>
              <p>Track your progress and compete worldwide</p>
            </div>
          </div>

          <div className="landing-actions">
            <button 
              className="get-started-btn"
              onClick={() => setShowAuthModal(true)}
            >
              Get Started
            </button>
            
            <p className="auth-hint">
              Sign in to save your progress and compete with friends
            </p>
          </div>
        </div>

        <div className="landing-decoration">
          <div className="word-grid-demo">
            <div className="demo-row">
              <span className="demo-letter correct">W</span>
              <span className="demo-letter correct">O</span>
              <span className="demo-letter correct">R</span>
              <span className="demo-letter correct">D</span>
              <span className="demo-letter correct">S</span>
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
