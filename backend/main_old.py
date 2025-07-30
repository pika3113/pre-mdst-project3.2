from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wordle_game import wordle_turn, getCellColor
import random

# Simple fallback word lists in case NLTK fails
FALLBACK_WORDS = {
    4: ["WORD", "TEST", "GAME", "PLAY", "TIME", "GOOD", "NICE", "COOL", "FAST", "SLOW", "HOPE", "LOVE", "LUCK", "WORK", "HOME"],
    5: ["HELLO", "WORLD", "PYTHON", "GAMES", "WORDS", "QUICK", "BROWN", "JUMPS", "FOXES", "TESTS", "MAGIC", "SPACE", "TIGER", "OCEAN", "LIGHT"],
    6: ["PYTHON", "CODING", "SIMPLE", "WORDLE", "LETTERS", "RANDOM", "CUSTOM", "FIXING", "ISSUES", "SOLVED", "ANIMAL", "BRIDGE", "CASTLE", "DRAGON", "FLOWER"]
}

# Try to import NLTK, but fall back to simple words if it fails
try:
    import nltk
    from nltk.corpus import words
    
    # Try to access the words corpus
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        print("Downloading NLTK words corpus...")
        nltk.download('words')
        print("NLTK words corpus downloaded successfully")
    
    USE_NLTK = True
    print("NLTK successfully loaded")
except Exception as e:
    print(f"NLTK failed to load: {e}")
    print("Using fallback word lists")
    USE_NLTK = False

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],   
)
difficultyLevels = {
    "easy" : 4,
    "medium" : 5,
    "hard" : 6
}

# Game state storage (in production, use a proper database)
game_sessions = {}

class GuessRequest(BaseModel):
    guess:str

class NewGameRequest(BaseModel):
    pass


@app.post("/new-game/{difficulty}")
async def new_game(difficulty: str, data: NewGameRequest):
    if difficulty not in difficultyLevels:
        raise HTTPException(status_code=404, detail="Difficulty not found")
    
    word_length = difficultyLevels[difficulty]
    
    if USE_NLTK:
        # Use NLTK words
        try:
            all_words = words.words()
            wordBank = [w.upper() for w in all_words if len(w) == word_length and w.isalpha()]
        except Exception as e:
            print(f"NLTK error: {e}, falling back to predefined words")
            wordBank = FALLBACK_WORDS[word_length]
    else:
        # Use fallback words
        wordBank = FALLBACK_WORDS[word_length]
    
    if not wordBank:
        raise HTTPException(status_code=500, detail="No words found for this difficulty")
    
    chosen_word = random.choice(wordBank)
    session_id = f"{difficulty}_{random.randint(1000, 9999)}"
    
    game_sessions[session_id] = {
        "word": chosen_word,
        "difficulty": difficulty,
        "guesses": 0,
        "max_guesses": 6,
        "is_complete": False
    }
    
    return {"session_id": session_id, "word_length": word_length, "max_guesses": 6}

@app.post("/guess/{session_id}")
async def make_guess(session_id: str, data: GuessRequest):
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Game is already complete")
    
    guess = data.guess.upper()
    chosen_word = session["word"]
    
    if len(guess) != len(chosen_word):
        raise HTTPException(status_code=400, detail=f"Guess must be {len(chosen_word)} letters")
    
    result, is_win = getCellColor(guess, chosen_word)
    session["guesses"] += 1
    
    if is_win:
        session["is_complete"] = True
        result["message"] = "You win!"
    elif session["guesses"] >= session["max_guesses"]:
        session["is_complete"] = True
        result["message"] = f"Game Over! The word was {chosen_word}"
    
    return {"cells": result['cells'], "message": result['message'], "won": is_win, "game_over": session["is_complete"]}

@app.post("/{difficulty}")
async def play(difficulty: str, data: GuessRequest):
    guess = data.guess.lower()
    try:
        result,won = wordle_turn(difficultyLevels[difficulty],guess)
        return {"cells": result['cells'], "message": result['message'], "won": won}
    except ValueError:
        raise HTTPException(status_code=404,detail="Difficulty not found")
  