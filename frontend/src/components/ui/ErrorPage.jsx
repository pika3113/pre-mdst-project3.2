import React from 'react';
import './ErrorPage.css';

function ErrorPage({ onRetry }) {
  return (
    <div className="error-page">
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <h1 className="error-title">Connection Lost</h1>
        <p className="error-message">
          Unable to connect to the game server. Please check your connection and try again.
        </p>
        <div className="error-actions">
          <button className="retry-button" onClick={onRetry}>
            Try Again
          </button>
        </div>
        <div className="error-details">
          <p>If the problem persists:</p>
          <ul>
            <li>Check if the backend server is running</li>
            <li>Verify your network connection</li>
            <li>Try refreshing your browser</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ErrorPage;
