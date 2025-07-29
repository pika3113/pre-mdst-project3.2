import React, {useState, useEffect, useCallback} from "react";
import "./App.css";
import { generate } from 'random-words';

const WORD_LENGTH = 5;
const MAX_GUESSES = 6;


function getFiveLetterWord() {
  let word = '';
  while (word.length !== 5) {
    word = generate();
  }
  return word.toLowerCase();
}

const TARGET_WORD = getFiveLetterWord();
console.log(TARGET_WORD);
//not sure if i wanna put this here or backend

const emptyGrid = Array(MAX_GUESSES).fill(null).map(() => Array(WORD_LENGTH).fill(""));

function Wordle() {
    const [grid, setGrid] = useState(emptyGrid)
    const [currentRow, setCurrentRow] = useState(0);
    const [currentCol, setCurrentCol] = useState(0);
    const [isGameOver, setIsGameOver] = useState(false);
    const [message, setMessage] = useState("");

    const onKeyDown = useCallback(
        async (e) => {
        if (isGameOver) return;

        const key = e.key.toUpperCase();

        if (key === "BACKSPACE") {
            if (currentCol > 0 ) {
                //console.log(currentCol, currentRow);
                updateGrid(currentRow, currentCol-1, "");
                setCurrentCol(currentCol - 1);
            }
            return
            }

        if (key === 'ENTER') {
            //console.log(currentCol, currentRow);
            if (currentCol !== WORD_LENGTH) {
                setMessage("word must be 5 letters!");
                return;
            }
            const guess = grid[currentRow].join("");
            
            //temp bypass cus no backend
            //validate guess with backend
                // try {
                //     const res = await fetch("http://localhost:4000/validate", {
                //         method: 'POST',
                //         headers: {'Content-Type': 'application/json'},
                //         body: JSON.stringify({ guess })
                //     });
                //     const data = await res.json();
                //     if (!data.valid) {
                //         setMessage(data.message || "invalid guess");
                //         return;
                //     }
                // } catch {
                //     setMessage("validation error")
                //     return;
                // }

                // if (guess === TARGET_WORD) {
                //     setMessage('you win');
                //     setIsGameOver(true);
                //     return;
                // }

            setCurrentRow(currentRow+1);
            setCurrentCol(0);
            setMessage("");
            return;            
        }

        if (/^[A-z]$/.test(key)) {
            if (currentCol < WORD_LENGTH) {
                updateGrid(currentRow, currentCol, key.toLowerCase())
                setCurrentCol(currentCol+1)

            }
        }
        },
        [currentCol, currentRow, isGameOver, TARGET_WORD]
    );

    useEffect(() => {
        window.addEventListener("keydown", onKeyDown);
        return () => window.removeEventListener("keydown", onKeyDown);
    }, [onKeyDown]);

    function updateGrid(row,col,letter) {
        setGrid((prev) => {
            const newGrid = prev.map((r) => r.slice());
            newGrid[row][col] = letter;
            return newGrid
        });
    }

    function getCellColor(row,col) {
        const letter = grid[row][col];
        if (!letter) return "white";
        if (row >= currentRow) return "white"

        const guess = grid[row];
        const target = TARGET_WORD.split("");
        
        if (letter === TARGET_WORD[col]) return '#1fdb0dff' //green

        //count how many times letter occurs in target
        const targetCount = target.filter((l) => l === letter).length;

        //count how many times letter guessed in correct spot
        const correctCount= guess.filter((l,i) => l === letter && target[i] === l).length;

        const guessBefore = guess.slice(0,col).filter((l) => l === letter).length;  

        if (target.includes(letter) && guessBefore < targetCount - correctCount) {
            return "#e4c53aff"; //yellow
        }

        return '#d71717ff'; //grey
    }

    return (
        <div className = "wordle-container">
            <div className = "grid">
                {grid.map((row, rowIndex) => (
                    <div className = "row" key={rowIndex}>
                        {row.map((letter,colIndex) => (
                            <div
                                className = "cell"
                                key = {colIndex}
                                style = {{ backgroundColor: getCellColor(rowIndex, colIndex)}}
                            >
                                {letter}
                            </div>
                        ))}
                    </div>
                ))}                
            </div>
            {message && <div className="message">{message}</div>}
        </div>
    );

}

export default Wordle;