import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import Stats from "./Stats";

const MAX_GUESSES = 6;

function Wordle() {
  const [difficulty, setDifficulty] = useState("medium"); // easy = 4, medium = 5, hard = 6
  const [wordLength, setWordLength] = useState(5);
  const [grid, setGrid] = useState([]);
  const [colors, setColors] = useState([]);
  const [currentRow, setCurrentRow] = useState(0);
  const [currentCol, setCurrentCol] = useState(0);
  const [isGameOver, setIsGameOver] = useState(false);
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showStats, setShowStats] = useState(false);

  // Initialize empty grids based on word length
  const initializeGrids = (length) => {
    const emptyGrid = Array(MAX_GUESSES).fill(null).map(() => Array(length).fill(""));
    const emptyColorGrid = Array(MAX_GUESSES).fill(null).map(() => Array(length).fill("white"));
    setGrid(emptyGrid);
    setColors(emptyColorGrid);
  };

  // Start a new game
  const startNewGame = async (newDifficulty = difficulty) => {
    setIsLoading(true);
    setDifficulty(newDifficulty);
    try {
      const res = await fetch(`http://localhost:8000/new-game/${newDifficulty}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });

      if (!res.ok) {
        const err = await res.json();
        setMessage(err.detail || "Error starting new game");
        return;
      }

      const data = await res.json();
      setSessionId(data.session_id);
      setWordLength(data.word_length);
      initializeGrids(data.word_length);
      setCurrentRow(0);
      setCurrentCol(0);
      setIsGameOver(false);
      setMessage("");
    } catch (err) {
      setMessage("Network error starting game");
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize game on component mount
  useEffect(() => {
    startNewGame();
  }, []);

  const updateGrid = (row, col, letter) => {
    setGrid((prev) => {
      const newGrid = prev.map((r) => r.slice());
      newGrid[row][col] = letter;
      return newGrid;
    });
  };

  const updateColors = (row, colorRow) => {
    setColors((prev) => {
      const newColors = prev.map((r) => r.slice());
      newColors[row] = colorRow;
      return newColors;
    });
  };

  const onKeyDown = useCallback(
    async (e) => {
      if (isGameOver || !sessionId) return;

      const key = e.key.toUpperCase();

      if (key === "BACKSPACE") {
        if (currentCol > 0) {
          updateGrid(currentRow, currentCol - 1, "");
          setCurrentCol(currentCol - 1);
        }
        return;
      }

      if (key === "ENTER") {
        if (currentCol !== wordLength) {
          setMessage(`Word must be ${wordLength} letters!`);
          return;
        }

        const guess = grid[currentRow].join("");

        try {
          const res = await fetch(`http://localhost:8000/guess/${sessionId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ guess }),
          });

          if (!res.ok) {
            const err = await res.json();
            setMessage(err.detail || "Error submitting guess");
            // If it's a word validation error, clear the current row after showing the message
            if (err.detail && err.detail.includes("not a valid word")) {
              // Clear the current row
              setTimeout(() => {
                for (let i = 0; i < wordLength; i++) {
                  updateGrid(currentRow, i, "");
                }
                setCurrentCol(0);
                // Clear the error message after a short delay
                setTimeout(() => setMessage(""), 2000);
              }, 1000);
            }
            return;
          }

          const data = await res.json();
          updateColors(currentRow, data.cells);

          if (data.won) {
            setMessage("You win!");
            setIsGameOver(true);
          } else if (data.game_over) {
            setMessage(data.message || "Game Over!");
            setIsGameOver(true);
          } else {
            setCurrentRow(currentRow + 1);
            setCurrentCol(0);
            setMessage("");
          }
        } catch (err) {
          setMessage("Network error");
        }

        return;
      }

      if (/^[A-Z]$/.test(key)) {
        if (currentCol < wordLength) {
          updateGrid(currentRow, currentCol, key.toLowerCase());
          setCurrentCol(currentCol + 1);
        }
      }
    },
    [currentCol, currentRow, isGameOver, grid, sessionId, wordLength]
  );

  useEffect(() => {
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onKeyDown]);

  return (
    <div className="wordle-container">
      {isLoading ? (
        <div className="loading">Starting new game...</div>
      ) : (
        <>
          <div className="header">
            <h1>Wordle</h1>
            <button className="stats-button" onClick={() => setShowStats(true)}>
              📊 Stats
            </button>
          </div>
          
          <div className="difficulty-selector">
            <button 
              onClick={() => startNewGame("easy")} 
              className={difficulty === "easy" ? "active" : ""}
            >
              Easy (4 letters)
            </button>
            <button 
              onClick={() => startNewGame("medium")} 
              className={difficulty === "medium" ? "active" : ""}
            >
              Medium (5 letters)
            </button>
            <button 
              onClick={() => startNewGame("hard")} 
              className={difficulty === "hard" ? "active" : ""}
            >
              Hard (6 letters)
            </button>
          </div>
          <div className="grid">
            {grid.map((row, rowIndex) => (
              <div className="row" key={rowIndex}>
                {row.map((letter, colIndex) => (
                  <div
                    className={`cell ${
                      rowIndex === currentRow && colIndex === currentCol && !isGameOver 
                        ? 'current-cell' 
                        : ''
                    } ${
                      letter ? 'filled' : ''
                    }`}
                    key={colIndex}
                    style={{
                      backgroundColor: colors[rowIndex][colIndex],
                      animationDelay: `${colIndex * 0.1}s`,
                    }}
                  >
                    {letter}
                  </div>
                ))}
              </div>
            ))}
          </div>
          {message && (
            <div className={`message ${
              message.includes("not a valid word") || message.includes("must be") || message.includes("Error") 
                ? "error" 
                : message.includes("win") || message.includes("Win") 
                ? "success" 
                : ""
            }`}>
              {message}
            </div>
          )}
          {isGameOver && (
            <button onClick={startNewGame} className="new-game-btn">
              New Game
            </button>
          )}
        </>
      )}
      
      <Stats isOpen={showStats} onClose={() => setShowStats(false)} />
    </div>
  );
}

export default Wordle;
