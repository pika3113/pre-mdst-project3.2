import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { rouletteService } from '../../services/rouletteService';
import LoadingSpinner from '../ui/LoadingSpinner';
import './RouletteGame.css';

function RouletteGame({ user }) {
  const [gameInfo, setGameInfo] = useState(null);
  const [bets, setBets] = useState([]);
  const [betAmount, setBetAmount] = useState(10);
  const [isSpinning, setIsSpinning] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [balance, setBalance] = useState(1000); // Starting balance
  const [message, setMessage] = useState('');
  const [selectedNumbers, setSelectedNumbers] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadGameInfo();
  }, []);

  const loadGameInfo = async () => {
    try {
      setIsLoading(true);
      const info = await rouletteService.getGameInfo(navigate);
      setGameInfo(info);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to load game info:', error);
      setMessage('Failed to load game information');
      setIsLoading(false);
    }
  };

  const removeBet = (index) => {
    const newBets = bets.filter((_, i) => i !== index);
    setBets(newBets);
  };

  const clearAllBets = () => {
    setBets([]);
    setMessage('All bets cleared');
  };

  const toggleNumberSelection = (number) => {
    setSelectedNumbers(prev => {
      if (prev.includes(number)) {
        return prev.filter(n => n !== number);
      } else {
        return [...prev, number].sort((a, b) => a - b);
      }
    });
  };

  const clearSelection = () => {
    setSelectedNumbers([]);
    setMessage('Selection cleared');
  };

  const detectBetType = (numbers) => {
    if (numbers.length === 0) {
      return { isValid: false, error: 'No numbers selected' };
    }

    const sortedNumbers = [...numbers].sort((a, b) => a - b);

    // Single number bet
    if (sortedNumbers.length === 1) {
      return {
        isValid: true,
        betType: 'single',
        selection: sortedNumbers,
        description: `Straight-up bet on ${sortedNumbers[0]}`,
        payout: '35:1'
      };
    }

    // Split bet (2 adjacent numbers)
    if (sortedNumbers.length === 2) {
      const [num1, num2] = sortedNumbers;
      
      // Check if numbers are adjacent horizontally or vertically
      const isHorizontalAdjacent = Math.abs(num1 - num2) === 1 && 
        Math.floor((num1 - 1) / 3) === Math.floor((num2 - 1) / 3);
      const isVerticalAdjacent = Math.abs(num1 - num2) === 3;
      const isZeroAdjacent = (num1 === 0 && [1, 2, 3].includes(num2));

      if (isHorizontalAdjacent || isVerticalAdjacent || isZeroAdjacent) {
        return {
          isValid: true,
          betType: 'double',
          selection: sortedNumbers,
          description: `Split bet on ${sortedNumbers.join('-')}`,
          payout: '17:1'
        };
      } else {
        return { isValid: false, error: 'Selected numbers are not adjacent for a split bet' };
      }
    }

    // Street bet (3 numbers in a row)
    if (sortedNumbers.length === 3) {
      const [num1, num2, num3] = sortedNumbers;
      
      // Check if it's a valid street (consecutive numbers in same row)
      if (num2 === num1 + 1 && num3 === num2 + 1 && 
          Math.floor((num1 - 1) / 3) === Math.floor((num3 - 1) / 3)) {
        return {
          isValid: true,
          betType: 'three',
          selection: sortedNumbers,
          description: `Street bet on ${sortedNumbers.join('-')}`,
          payout: '11:1'
        };
      } else {
        return { isValid: false, error: 'Selected numbers do not form a valid street bet' };
      }
    }

    // Corner bet (4 numbers in a square)
    if (sortedNumbers.length === 4) {
      const [num1, num2, num3, num4] = sortedNumbers;
      
      // Check if numbers form a 2x2 square
      const expectedPattern = [num1, num1 + 1, num1 + 3, num1 + 4];
      if (JSON.stringify(sortedNumbers) === JSON.stringify(expectedPattern) &&
          Math.floor((num1 - 1) / 3) === Math.floor((num2 - 1) / 3)) {
        return {
          isValid: true,
          betType: 'four',
          selection: sortedNumbers,
          description: `Corner bet on ${sortedNumbers.join('-')}`,
          payout: '8:1'
        };
      } else {
        return { isValid: false, error: 'Selected numbers do not form a valid corner bet' };
      }
    }

    // Six line bet (6 numbers in two rows)
    if (sortedNumbers.length === 6) {
      const [num1, num2, num3, num4, num5, num6] = sortedNumbers;
      
      // Check if it's two consecutive rows of 3
      const firstRow = [num1, num2, num3];
      const secondRow = [num4, num5, num6];
      
      if (num3 === num1 + 2 && num6 === num4 + 2 && num4 === num1 + 3 &&
          Math.floor((num1 - 1) / 3) === Math.floor((num3 - 1) / 3) &&
          Math.floor((num4 - 1) / 3) === Math.floor((num6 - 1) / 3)) {
        return {
          isValid: true,
          betType: 'six',
          selection: sortedNumbers,
          description: `Six line bet on ${sortedNumbers.join('-')}`,
          payout: '5:1'
        };
      } else {
        return { isValid: false, error: 'Selected numbers do not form a valid six line bet' };
      }
    }

    return { isValid: false, error: `Invalid bet pattern with ${sortedNumbers.length} numbers` };
  };

  const placeBet = () => {
    if (selectedNumbers.length === 0) {
      setMessage('Please select numbers to bet on');
      return;
    }

    if (betAmount <= 0) {
      setMessage('Bet amount must be positive');
      return;
    }

    if (betAmount > balance) {
      setMessage('Insufficient balance');
      return;
    }

    const betDetection = detectBetType(selectedNumbers);
    
    if (!betDetection.isValid) {
      setMessage(`Invalid bet: ${betDetection.error}`);
      return;
    }

    const bet = {
      bet_type: betDetection.betType,
      amount: betAmount,
      selection: betDetection.selection
    };

    setBets([...bets, bet]);
    setMessage(`${betDetection.description} placed: $${betAmount} (${betDetection.payout})`);
    setSelectedNumbers([]); // Clear selection after placing bet
  };

  const spinWheel = async () => {
    if (bets.length === 0) {
      setMessage('Please place at least one bet');
      return;
    }

    const totalBetAmount = bets.reduce((sum, bet) => sum + bet.amount, 0);
    if (totalBetAmount > balance) {
      setMessage('Total bets exceed available balance');
      return;
    }

    try {
      setIsSpinning(true);
      setMessage('Spinning...');
      
      // Clear any remaining selection
      setSelectedNumbers([]);
      
      // Simulate spinning animation delay
      setTimeout(async () => {
        try {
          const result = await rouletteService.playRoulette(bets, navigate);
          setLastResult(result);
          
          // Update balance
          const newBalance = balance + result.net_result;
          setBalance(newBalance);
          
          // Clear bets after spin
          setBets([]);
          
          if (result.net_result > 0) {
            setMessage(`🎉 Winner! Pocket ${result.pocket} (${result.color}). You won $${result.total_winnings}!`);
          } else if (result.net_result === 0) {
            setMessage(`No win this time. Pocket ${result.pocket} (${result.color}).`);
          } else {
            setMessage(`Better luck next time! Pocket ${result.pocket} (${result.color}). You lost $${Math.abs(result.net_result)}.`);
          }
          
          setIsSpinning(false);
        } catch (error) {
          console.error('Failed to spin wheel:', error);
          setMessage('Failed to spin wheel. Please try again.');
          setIsSpinning(false);
        }
      }, 2000);
    } catch (error) {
      console.error('Error spinning wheel:', error);
      setMessage('Error occurred while spinning');
      setIsSpinning(false);
    }
  };

  const addSingleNumberBet = (number) => {
    if (betAmount <= 0) {
      setMessage('Bet amount must be positive');
      return;
    }

    if (betAmount > balance) {
      setMessage('Insufficient balance');
      return;
    }

    const bet = {
      bet_type: 'single',
      amount: betAmount,
      selection: [number]
    };

    setBets([...bets, bet]);
    setMessage(`Single number bet on ${number}: $${betAmount}`);
  };

  const getDozensNumbers = (dozen) => {
    switch (dozen) {
      case 1: return Array.from({length: 12}, (_, i) => i + 1);
      case 2: return Array.from({length: 12}, (_, i) => i + 13);
      case 3: return Array.from({length: 12}, (_, i) => i + 25);
      default: return [];
    }
  };

  const addColumnBet = (columnNumbers) => {
    if (betAmount <= 0) {
      setMessage('Bet amount must be positive');
      return;
    }

    if (betAmount > balance) {
      setMessage('Insufficient balance');
      return;
    }

    const bet = {
      bet_type: 'column',
      amount: betAmount,
      selection: columnNumbers
    };

    setBets([...bets, bet]);
    setMessage(`Column bet added: $${betAmount}`);
  };

  const addDozenBet = (dozenNumbers) => {
    if (betAmount <= 0) {
      setMessage('Bet amount must be positive');
      return;
    }

    if (betAmount > balance) {
      setMessage('Insufficient balance');
      return;
    }

    const bet = {
      bet_type: 'dozens',
      amount: betAmount,
      selection: dozenNumbers
    };

    setBets([...bets, bet]);
    setMessage(`Dozen bet added: $${betAmount}`);
  };

  const addOutsideBet = (betType, selection) => {
    if (betAmount <= 0) {
      setMessage('Bet amount must be positive');
      return;
    }

    if (betAmount > balance) {
      setMessage('Insufficient balance');
      return;
    }

    const bet = {
      bet_type: betType,
      amount: betAmount,
      selection: selection
    };

    setBets([...bets, bet]);
    setMessage(`${betType} bet added: $${betAmount}`);
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading Roulette..." />;
  }

  if (!gameInfo) {
    return <div className="error-message">Failed to load game information</div>;
  }

  return (
    <div className="roulette-game">
      <div className="game-header">
        <h1>Roulette</h1>
        <div className="balance">Balance: ${balance}</div>
        <button 
          className="back-button"
          onClick={() => navigate('/menu')}
        >
          ← Back to Menu
        </button>
      </div>

      <div className="game-content">
        {/* Roulette Wheel */}
        <div className="wheel-section">
          <div className={`roulette-wheel ${isSpinning ? 'spinning' : ''}`}>
            <div className="wheel-center">
              {lastResult ? (
                <div className="result-display">
                  <div className="result-number">{lastResult.pocket}</div>
                  <div className="result-color">{lastResult.color}</div>
                </div>
              ) : (
                <div className="wheel-logo">🎯</div>
              )}
            </div>
          </div>
          <button 
            className="spin-button"
            onClick={spinWheel}
            disabled={isSpinning || bets.length === 0}
          >
            {isSpinning ? 'Spinning...' : 'Spin Wheel'}
          </button>
        </div>

        {/* Betting Table */}
        <div className="betting-section">
          <div className="bet-controls">
            <div className="bet-amount-selector">
              <label>Bet Amount:</label>
              <input 
                type="number" 
                value={betAmount} 
                onChange={(e) => setBetAmount(parseInt(e.target.value) || 0)}
                min="1"
                max={balance}
              />
            </div>
          </div>

          <div className="current-bet-display">
            <span className="current-bet-amount">Current Bet: ${betAmount}</span>
            <span className="bet-instructions">🎯 Select numbers on the table, then click "Place Bet" to bet!</span>
            {selectedNumbers.length > 0 && (
              <div className="selected-numbers">
                <span>Selected: {selectedNumbers.join(', ')}</span>
                <button className="clear-selection-btn" onClick={clearSelection}>Clear Selection</button>
              </div>
            )}
          </div>

          {/* Numbers Grid - Interactive Selection */}
          <div className="numbers-grid">
            <div className="roulette-table">
              <div className="zero-section">
                <button 
                  className={`number-button zero ${selectedNumbers.includes(0) ? 'selected' : ''}`}
                  onClick={() => toggleNumberSelection(0)}
                  title="Click to select/deselect 0"
                >
                  0
                </button>
              </div>
              
              <div className="main-table">
                {/* Row 1: 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36 */}
                <div className="number-row">
                  {[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36].map(number => (
                    <button
                      key={number}
                      className={`number-button ${gameInfo.wheel[number]} ${selectedNumbers.includes(number) ? 'selected' : ''}`}
                      onClick={() => toggleNumberSelection(number)}
                      title={`Click to select/deselect ${number}`}
                    >
                      {number}
                    </button>
                  ))}
                  <button 
                    className="column-bet-button" 
                    onClick={() => addColumnBet([3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36])}
                    title="Bet on 3rd Column (2:1 payout)"
                  >
                    2 to 1
                  </button>
                </div>

                {/* Row 2: 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35 */}
                <div className="number-row">
                  {[2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35].map(number => (
                    <button
                      key={number}
                      className={`number-button ${gameInfo.wheel[number]} ${selectedNumbers.includes(number) ? 'selected' : ''}`}
                      onClick={() => toggleNumberSelection(number)}
                      title={`Click to select/deselect ${number}`}
                    >
                      {number}
                    </button>
                  ))}
                  <button 
                    className="column-bet-button" 
                    onClick={() => addColumnBet([2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35])}
                    title="Bet on 2nd Column (2:1 payout)"
                  >
                    2 to 1
                  </button>
                </div>

                {/* Row 3: 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34 */}
                <div className="number-row">
                  {[1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34].map(number => (
                    <button
                      key={number}
                      className={`number-button ${gameInfo.wheel[number]} ${selectedNumbers.includes(number) ? 'selected' : ''}`}
                      onClick={() => toggleNumberSelection(number)}
                      title={`Click to select/deselect ${number}`}
                    >
                      {number}
                    </button>
                  ))}
                  <button 
                    className="column-bet-button" 
                    onClick={() => addColumnBet([1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34])}
                    title="Bet on 1st Column (2:1 payout)"
                  >
                    2 to 1
                  </button>
                </div>

                {/* Dozen bets */}
                <div className="dozen-bets">
                  <button 
                    className="dozen-bet-button" 
                    onClick={() => addDozenBet(getDozensNumbers(1))}
                    title="Bet on 1st Dozen: 1-12 (2:1 payout)"
                  >
                    1st 12
                  </button>
                  <button 
                    className="dozen-bet-button" 
                    onClick={() => addDozenBet(getDozensNumbers(2))}
                    title="Bet on 2nd Dozen: 13-24 (2:1 payout)"
                  >
                    2nd 12
                  </button>
                  <button 
                    className="dozen-bet-button" 
                    onClick={() => addDozenBet(getDozensNumbers(3))}
                    title="Bet on 3rd Dozen: 25-36 (2:1 payout)"
                  >
                    3rd 12
                  </button>
                </div>

                {/* Outside bets */}
                <div className="outside-bets">
                  <button 
                    className="outside-bet-button"
                    onClick={() => addOutsideBet('eighteens', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])}
                    title="Bet on 1-18 (1:1 payout)"
                  >
                    1 to 18
                  </button>
                  <button 
                    className="outside-bet-button"
                    onClick={() => addOutsideBet('evenodd', 'evens')}
                    title="Bet on Even Numbers (1:1 payout)"
                  >
                    EVEN
                  </button>
                  <button 
                    className="outside-bet-button red-bet"
                    onClick={() => addOutsideBet('color', 'red')}
                    title="Bet on Red (1:1 payout)"
                  >
                    ♦
                  </button>
                  <button 
                    className="outside-bet-button black-bet"
                    onClick={() => addOutsideBet('color', 'black')}
                    title="Bet on Black (1:1 payout)"
                  >
                    ♠
                  </button>
                  <button 
                    className="outside-bet-button"
                    onClick={() => addOutsideBet('evenodd', 'odds')}
                    title="Bet on Odd Numbers (1:1 payout)"
                  >
                    ODD
                  </button>
                  <button 
                    className="outside-bet-button"
                    onClick={() => addOutsideBet('eighteens', [19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36])}
                    title="Bet on 19-36 (1:1 payout)"
                  >
                    19 to 36
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="bet-actions">
            <button 
              className="place-bet-button" 
              onClick={placeBet}
              disabled={selectedNumbers.length === 0}
            >
              Place Bet (${betAmount})
            </button>
            <button className="clear-bets-button" onClick={clearAllBets}>
              Clear All Bets
            </button>
            {selectedNumbers.length > 0 && (
              <button className="clear-selection-button" onClick={clearSelection}>
                Clear Selection
              </button>
            )}
          </div>

          {/* Help Section */}
          <div className="betting-help">
            <h4>How to Bet</h4>
            <div className="help-content">
              <p><strong>Select numbers on the table and click "Place Bet":</strong></p>
              <ul>
                <li><strong>1 number:</strong> Straight-up bet (35:1)</li>
                <li><strong>2 adjacent numbers:</strong> Split bet (17:1)</li>
                <li><strong>3 numbers in a row:</strong> Street bet (11:1)</li>
                <li><strong>4 numbers in a square:</strong> Corner bet (8:1)</li>
                <li><strong>6 numbers in two rows:</strong> Six line bet (5:1)</li>
              </ul>
              <p><em>Outside bets (red/black, odd/even, etc.) can be placed directly with the buttons below.</em></p>
            </div>
          </div>
        </div>

        {/* Current Bets */}
        <div className="bets-section">
          <h3>Current Bets</h3>
          {bets.length === 0 ? (
            <p>No bets placed</p>
          ) : (
            <div className="bets-list">
              {bets.map((bet, index) => {
                // Format the selection display based on bet type
                let selectionDisplay = '';
                if (bet.bet_type === 'eighteens') {
                  if (Array.isArray(bet.selection) && bet.selection.length === 18) {
                    selectionDisplay = bet.selection[0] === 1 ? '1-18' : '19-36';
                  } else {
                    selectionDisplay = Array.isArray(bet.selection) ? bet.selection.join(', ') : bet.selection;
                  }
                } else if (bet.bet_type === 'dozens') {
                  if (Array.isArray(bet.selection) && bet.selection.length === 12) {
                    if (bet.selection[0] === 1) selectionDisplay = '1st 12 (1-12)';
                    else if (bet.selection[0] === 13) selectionDisplay = '2nd 12 (13-24)';
                    else if (bet.selection[0] === 25) selectionDisplay = '3rd 12 (25-36)';
                    else selectionDisplay = bet.selection.join(', ');
                  } else {
                    selectionDisplay = Array.isArray(bet.selection) ? bet.selection.join(', ') : bet.selection;
                  }
                } else if (bet.bet_type === 'column') {
                  if (Array.isArray(bet.selection) && bet.selection.length === 12) {
                    if (bet.selection.includes(1)) selectionDisplay = '1st Column';
                    else if (bet.selection.includes(2)) selectionDisplay = '2nd Column';
                    else if (bet.selection.includes(3)) selectionDisplay = '3rd Column';
                    else selectionDisplay = bet.selection.join(', ');
                  } else {
                    selectionDisplay = Array.isArray(bet.selection) ? bet.selection.join(', ') : bet.selection;
                  }
                } else if (bet.bet_type === 'color') {
                  selectionDisplay = bet.selection === 'red' ? 'Red' : 'Black';
                } else if (bet.bet_type === 'evenodd') {
                  selectionDisplay = bet.selection === 'evens' ? 'Even' : 'Odd';
                } else {
                  // For single, double, three, four, five, six bets - show the numbers
                  selectionDisplay = Array.isArray(bet.selection) ? bet.selection.join('-') : bet.selection;
                }

                return (
                  <div key={index} className="bet-item">
                    <span>{bet.bet_type}: ${bet.amount}</span>
                    <span>{selectionDisplay}</span>
                    <button onClick={() => removeBet(index)}>Remove</button>
                  </div>
                );
              })}
              <div className="total-bet">
                Total: ${bets.reduce((sum, bet) => sum + bet.amount, 0)}
              </div>
            </div>
          )}
        </div>
      </div>

      {message && (
        <div className="message-display">
          {message}
        </div>
      )}

      {/* Last Result */}
      {lastResult && (
        <div className="last-result">
          <h3>Last Result</h3>
          <div className="result-details">
            <p>Winning Number: {lastResult.pocket} ({lastResult.color})</p>
            <p>Total Winnings: ${lastResult.total_winnings}</p>
            <p>Net Result: {lastResult.net_result >= 0 ? '+' : ''}${lastResult.net_result}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default RouletteGame;
