/**
 * API service for Morphle game
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class MorphleApiService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/morphle`;
  }

  async makeRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async startGame(difficulty) {
    return this.makeRequest('/start', {
      method: 'POST',
      body: JSON.stringify({ difficulty }),
    });
  }

  async submitMove(gameId, move) {
    return this.makeRequest('/move', {
      method: 'POST',
      body: JSON.stringify({ 
        game_id: gameId, 
        move: move 
      }),
    });
  }

  async getHint(gameId) {
    return this.makeRequest('/hint', {
      method: 'POST',
      body: JSON.stringify({ game_id: gameId }),
    });
  }

  async getGameState(gameId) {
    return this.makeRequest(`/game/${gameId}/state`);
  }

  async getCompletionStats(gameId) {
    return this.makeRequest(`/game/${gameId}/completion`);
  }
}

export const morphleApi = new MorphleApiService();
