import { API_BASE_URL } from '../utils/config';
import { authUtils } from './authService';

/**
 * Roulette Game Service
 * Handles all API calls for the roulette game
 */
class RouletteService {
  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/roulette`;
  }

  /**
   * Play a round of roulette
   * @param {Array} bets - Array of bet objects
   * @param {Function} navigate - Navigation function for auth errors
   * @returns {Promise<Object>} Game result
   */
  async playRoulette(bets, navigate) {
    try {
      const response = await authUtils.apiCall(
        '/api/roulette/play',
        {
          method: 'POST',
          body: JSON.stringify({ bets }),
        },
        navigate
      );
      return response;
    } catch (error) {
      console.error('Failed to play roulette:', error);
      throw error;
    }
  }

  /**
   * Get roulette game information
   * @param {Function} navigate - Navigation function for auth errors
   * @returns {Promise<Object>} Game information
   */
  async getGameInfo(navigate) {
    try {
      const response = await authUtils.apiCall(
        '/api/roulette/info',
        { method: 'GET' },
        navigate
      );
      return response;
    } catch (error) {
      console.error('Failed to get roulette info:', error);
      throw error;
    }
  }

  /**
   * Get game status
   * @param {Function} navigate - Navigation function for auth errors
   * @returns {Promise<Object>} Game status
   */
  async getGameStatus(navigate) {
    try {
      const response = await authUtils.apiCall(
        '/api/roulette/',
        { method: 'GET' },
        navigate
      );
      return response;
    } catch (error) {
      console.error('Failed to get roulette status:', error);
      throw error;
    }
  }
}

export const rouletteService = new RouletteService();
