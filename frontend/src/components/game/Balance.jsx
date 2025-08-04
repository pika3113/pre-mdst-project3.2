import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { balanceService } from '../../services/balanceService';
import LoadingSpinner from '../ui/LoadingSpinner';
import './Balance.css';

function Balance({ user }) {
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('balance');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadBalanceData();
  }, []);

  const loadBalanceData = async () => {
    try {
      setIsLoading(true);
      const [balanceInfo, transactionHistory, leaderboardData] = await Promise.all([
        balanceService.getBalance(),
        balanceService.getTransactionHistory(50),
        balanceService.getLeaderboard(10)
      ]);
      
      setBalance(balanceInfo);
      setTransactions(transactionHistory.transactions);
      setLeaderboard(leaderboardData.leaderboard);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to load balance data:', error);
      setMessage('Failed to load balance information');
      setIsLoading(false);
    }
  };

  const formatAmount = (amount) => {
    return amount >= 0 ? `+$${amount}` : `-$${Math.abs(amount)}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getTransactionIcon = (type) => {
    const icons = {
      'game_win': '🎉',
      'roulette_win': '🎰',
      'roulette_bet': '🎲',
      'bonus': '💰',
      'penalty': '⚠️'
    };
    return icons[type] || '📝';
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading balance..." />;
  }

  return (
    <div className="balance-page">
      <div className="balance-header">
        <h1>Your Wallet</h1>
        <button 
          className="back-button"
          onClick={() => navigate('/menu')}
        >
          ← Back to Menu
        </button>
      </div>

      <div className="balance-tabs">
        <button 
          className={`tab-button ${activeTab === 'balance' ? 'active' : ''}`}
          onClick={() => setActiveTab('balance')}
        >
          Balance
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Transaction History
        </button>
        <button 
          className={`tab-button ${activeTab === 'leaderboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('leaderboard')}
        >
          Leaderboard
        </button>
      </div>

      <div className="balance-content">
        {activeTab === 'balance' && (
          <div className="balance-overview">
            <div className="balance-card">
              <h2>Current Balance</h2>
              <div className="balance-amount">${balance?.balance || 0}</div>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Earned</h3>
                <div className="stat-value">${balance?.total_earned || 0}</div>
              </div>
              <div className="stat-card">
                <h3>Total Spent</h3>
                <div className="stat-value">${balance?.total_spent || 0}</div>
              </div>
              <div className="stat-card">
                <h3>Net Gain</h3>
                <div className="stat-value">
                  ${(balance?.total_earned || 0) - (balance?.total_spent || 0)}
                </div>
              </div>
            </div>

            <div className="earning-info">
              <h3>How to Earn Money</h3>
              <div className="earning-methods">
                <div className="earning-method">
                  <span className="game-icon">📝</span>
                  <div>
                    <strong>Wordle:</strong> $50 base reward
                    <ul>
                      <li>Easy: 1.0x multiplier</li>
                      <li>Medium: 1.2x multiplier</li>
                      <li>Hard: 1.5x multiplier</li>
                      <li>Perfect score bonus: +$25</li>
                    </ul>
                  </div>
                </div>
                <div className="earning-method">
                  <span className="game-icon">G</span>
                  <div>
                    <strong>Hangman:</strong> $30 base reward
                    <ul>
                      <li>Easy: 1.0x multiplier</li>
                      <li>Medium: 1.3x multiplier</li>
                      <li>Hard: 1.6x multiplier</li>
                      <li>Perfect score bonus: +$15</li>
                    </ul>
                  </div>
                </div>
                <div className="earning-method">
                  <span className="game-icon">🔤</span>
                  <div>
                    <strong>Morphle:</strong> $40 base reward
                    <ul>
                      <li>Easy: 1.0x multiplier</li>
                      <li>Medium: 1.4x multiplier</li>
                      <li>Hard: 1.8x multiplier</li>
                      <li>Perfect score bonus: +$20</li>
                    </ul>
                  </div>
                </div>
                <div className="earning-method">
                  <span className="game-icon">🎰</span>
                  <div>
                    <strong>Roulette:</strong> Gambling game
                    <ul>
                      <li>Win big or lose it all!</li>
                      <li>Use earned money to place bets</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="transaction-history">
            <h2>Recent Transactions</h2>
            {transactions.length === 0 ? (
              <p>No transactions yet. Start playing games to earn money!</p>
            ) : (
              <div className="transactions-list">
                {transactions.map((transaction, index) => (
                  <div key={index} className={`transaction-item ${transaction.amount >= 0 ? 'positive' : 'negative'}`}>
                    <div className="transaction-icon">
                      {getTransactionIcon(transaction.transaction_type)}
                    </div>
                    <div className="transaction-details">
                      <div className="transaction-description">
                        {transaction.description || transaction.transaction_type}
                      </div>
                      <div className="transaction-meta">
                        {transaction.game_type && (
                          <span className="game-type">{transaction.game_type}</span>
                        )}
                        <span className="transaction-date">
                          {formatDate(transaction.created_at)}
                        </span>
                      </div>
                    </div>
                    <div className={`transaction-amount ${transaction.amount >= 0 ? 'positive' : 'negative'}`}>
                      {formatAmount(transaction.amount)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div className="leaderboard">
            <h2>Top Players</h2>
            {leaderboard.length === 0 ? (
              <p>No leaderboard data available.</p>
            ) : (
              <div className="leaderboard-list">
                {leaderboard.map((player, index) => (
                  <div key={index} className="leaderboard-item">
                    <div className="player-rank">#{index + 1}</div>
                    <div className="player-info">
                      <div className="player-name">{player.username}</div>
                      <div className="player-stats">
                        Total Earned: ${player.total_earned}
                      </div>
                    </div>
                    <div className="player-balance">${player.balance}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {message && (
        <div className="message-display">
          {message}
        </div>
      )}
    </div>
  );
}

export default Balance;
