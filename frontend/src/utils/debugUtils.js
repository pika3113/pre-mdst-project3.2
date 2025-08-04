/**
 * Universal Debug Utilities for Game Development
 * 
 * Provides a unified debug interface for all games in the application.
 * Usage: In browser console, type `answer = true` to reveal the current game's answer
 */

class GameDebugManager {
  constructor() {
    this.activeGame = null;
    this.gameType = null;
    this.setupGlobalCommands();
  }

  setupGlobalCommands() {
    // Setting up debug commands (temporarily always enabled for testing)
    console.log('Debug: Setting up global commands, DEV mode:', import.meta.env.DEV);
    
    // Universal answer command
    Object.defineProperty(window, 'answer', {
      get: () => 'Set answer=true to reveal the current game\'s answer!',
      set: (value) => {
        if (value === true) {
          this.revealCurrentGameAnswer();
          return; // Don't return the value to avoid console logging "true"
        }
      },
      configurable: true
    });

    // Direct game-specific commands for convenience
    window.getAnswer = () => this.revealCurrentGameAnswer();
    window.debugGame = () => this.showDebugInfo();
    console.log('Debug: Global commands set up successfully');
  }

  setActiveGame(gameType, gameData) {
    this.activeGame = gameData;
    this.gameType = gameType;
    console.info(`Debug: Active game set to ${gameType}`);
  }

  clearActiveGame() {
    this.activeGame = null;
    this.gameType = null;
  }

  async revealCurrentGameAnswer() {
    if (!this.activeGame || !this.gameType) {
      console.warn('Debug: No active game detected. Start a game first!');
      return;
    }

    try {
      switch (this.gameType.toLowerCase()) {
        case 'wordle':
          if (window.revealWordleAnswer) {
            await window.revealWordleAnswer();
          } else {
            console.error('Wordle debug function not available');
          }
          break;
          
        case 'hangman':
          if (window.revealHangmanAnswer) {
            await window.revealHangmanAnswer();
          } else {
            console.error('Hangman debug function not available');
          }
          break;
          
        case 'morphle':
          if (window.revealMorphleAnswer) {
            await window.revealMorphleAnswer();
          } else {
            console.error('Morphle debug function not available');
          }
          break;
          
        default:
          console.warn(`Debug: Game type "${this.gameType}" not supported`);
      }
    } catch (error) {
      console.error('Debug: Failed to reveal answer', error);
    }
  }

  showDebugInfo() {
    if (!import.meta.env.DEV) {
      console.warn('Debug commands are only available in development mode');
      return;
    }
    
    if (!this.activeGame || !this.gameType) {
      console.warn('Debug: No active game detected');
      return;
    }

    console.group('Game Debug Info');
    console.log('Game Type:', this.gameType);
    console.log('Game Data:', this.activeGame);
    console.log('Available Commands:');
    console.log('  - answer = true  (reveal answer)');
    console.log('  - getAnswer()    (reveal answer)');
    console.log('  - debugGame()    (show this info)');
    console.groupEnd();
  }

  // Cleanup method
  destroy() {
    if (window.hasOwnProperty('answer')) delete window.answer;
    if (window.hasOwnProperty('getAnswer')) delete window.getAnswer;
    if (window.hasOwnProperty('debugGame')) delete window.debugGame;
  }
}

// Create global instance
const gameDebugManager = new GameDebugManager();

export default gameDebugManager;
