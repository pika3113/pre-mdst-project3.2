import React, { useState, useEffect } from "react";
import "./Stats.css";

function Stats({ isOpen, onClose }) {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (isOpen) {
      fetchStats();
      fetchHistory();
    }
  }, [isOpen]);

  const fetchStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/stats");
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch("http://localhost:8000/history");
      const data = await response.json();
      setHistory(data.games);
    } catch (error) {
      console.error("Error fetching history:", error);
    } finally {
      setLoading(false);
    }
  };

  const resetStats = async () => {
    if (window.confirm("Are you sure you want to reset all statistics? This cannot be undone.")) {
      try {
        await fetch("http://localhost:8000/reset-stats", { method: "POST" });
        fetchStats();
        fetchHistory();
      } catch (error) {
        console.error("Error resetting stats:", error);
      }
    }
  };

  if (!isOpen) return null;

  if (loading) {
    return (
      <div className="stats-overlay">
        <div className="stats-modal">
          <div className="loading">Loading statistics...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="stats-overlay">
      <div className="stats-modal">
        <div className="stats-header">
          <h2>Statistics</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="stats-tabs">
          <button 
            className={activeTab === "overview" ? "active" : ""} 
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </button>
          <button 
            className={activeTab === "distribution" ? "active" : ""} 
            onClick={() => setActiveTab("distribution")}
          >
            Guess Distribution
          </button>
          <button 
            className={activeTab === "history" ? "active" : ""} 
            onClick={() => setActiveTab("history")}
          >
            History
          </button>
        </div>

        <div className="stats-content">
          {activeTab === "overview" && (
            <div className="overview-tab">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-number">{stats?.total_games || 0}</div>
                  <div className="stat-label">Games Played</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats?.win_rate || 0}%</div>
                  <div className="stat-label">Win Rate</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats?.streak || 0}</div>
                  <div className="stat-label">Current Streak</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats?.max_streak || 0}</div>
                  <div className="stat-label">Max Streak</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats?.average_guesses || 0}</div>
                  <div className="stat-label">Avg Guesses</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">{stats?.wins || 0}</div>
                  <div className="stat-label">Games Won</div>
                </div>
              </div>

              {stats?.difficulty_stats && Object.keys(stats.difficulty_stats).length > 0 && (
                <div className="difficulty-stats">
                  <h3>By Difficulty</h3>
                  {Object.entries(stats.difficulty_stats).map(([difficulty, diffStats]) => (
                    <div key={difficulty} className="difficulty-row">
                      <span className="difficulty-name">{difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</span>
                      <span className="difficulty-stat">{diffStats.total_games} games</span>
                      <span className="difficulty-stat">{diffStats.win_rate}% win rate</span>
                      <span className="difficulty-stat">{diffStats.average_guesses} avg guesses</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "distribution" && (
            <div className="distribution-tab">
              <h3>Guess Distribution</h3>
              <div className="distribution-chart">
                {Object.entries(stats?.guess_distribution || {}).map(([guesses, count]) => {
                  const maxCount = Math.max(...Object.values(stats?.guess_distribution || {}));
                  const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                  
                  return (
                    <div key={guesses} className="distribution-row">
                      <span className="guess-number">{guesses}</span>
                      <div className="distribution-bar">
                        <div 
                          className="distribution-fill" 
                          style={{ width: `${percentage}%` }}
                        ></div>
                        <span className="distribution-count">{count}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === "history" && (
            <div className="history-tab">
              <h3>Recent Games</h3>
              <div className="history-list">
                {history.length === 0 ? (
                  <p>No games played yet!</p>
                ) : (
                  history.map((game, index) => (
                    <div key={index} className={`history-item ${game.won ? 'won' : 'lost'}`}>
                      <div className="history-word">{game.word}</div>
                      <div className="history-details">
                        <span className="history-difficulty">{game.difficulty}</span>
                        <span className="history-guesses">{game.guesses} guesses</span>
                        <span className={`history-result ${game.won ? 'won' : 'lost'}`}>
                          {game.won ? '✓' : '✗'}
                        </span>
                      </div>
                      <div className="history-date">
                        {new Date(game.timestamp).toLocaleDateString()}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="stats-footer">
          <button className="reset-btn" onClick={resetStats}>
            Reset Statistics
          </button>
        </div>
      </div>
    </div>
  );
}

export default Stats;
