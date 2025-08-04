import { API_BASE_URL } from '../utils/config';

class BalanceService {
  async getBalance() {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/balance/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to get balance:', error);
      throw error;
    }
  }

  async getTransactionHistory(limit = 50) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/balance/history?limit=${limit}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to get transaction history:', error);
      throw error;
    }
  }

  async getLeaderboard(limit = 10) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/balance/leaderboard?limit=${limit}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to get leaderboard:', error);
      throw error;
    }
  }
}

export const balanceService = new BalanceService();
