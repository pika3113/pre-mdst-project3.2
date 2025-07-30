from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string
import sqlite3
from datetime import datetime
from typing import Optional
import os

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],   
)

# Simple word lists for testing
WORD_LISTS = {
    4: ["WORD", "TEST", "GAME", "PLAY", "TIME", "GOOD", "NICE", "COOL", "FAST", "SLOW", "WORK", "HOME", "LOVE", "HOPE", "LIFE", "MAKE", "TAKE", "COME", "SOME", "HELP", "CALL", "WELL", "TELL", "FEEL", "KEEP", "LOOK", "PART", "WANT", "YEAR", "HAND"],
    5: ["HELLO", "WORLD", "PYTHON", "GAMES", "WORDS", "QUICK", "BROWN", "JUMPS", "FOXES", "TESTS", "MAGIC", "SPACE", "TIGER", "OCEAN", "LIGHT", "HOUSE", "MONEY", "HEART", "NIGHT", "SOUND", "WATER", "PLACE", "RIGHT", "THINK", "POINT", "MUSIC", "YOUNG", "ABOVE", "AGAIN", "STORY"],
    6: ["PYTHON", "CODING", "SIMPLE", "WORDLE", "LETTERS", "RANDOM", "CUSTOM", "FIXING", "ISSUES", "SOLVED", "ANIMAL", "BRIDGE", "CASTLE", "DRAGON", "FLOWER", "GARDEN", "FRIEND", "MARKET", "HEALTH", "FAMILY", "SOCIAL", "SCHOOL", "STRONG", "SYSTEM", "FATHER", "MOTHER", "TRAVEL", "MODERN", "FOREST", "CIRCLE"]
}

# All valid words for validation (includes both target words and valid guesses)
ALL_VALID_WORDS = {
    4: WORD_LISTS[4] + ["ABLE", "ALSO", "BACK", "BEEN", "BEST", "BOOK", "BOTH", "CAME", "CITY", "DATA", "DOES", "DOWN", "EACH", "EVEN", "FACE", "FACT", "FIND", "FIRE", "GIVE", "GOES", "HARD", "HEAD", "HIGH", "HOLD", "HUGE", "IDEA", "INTO", "JUST", "KIND", "KNOW", "LAND", "LAST", "LEFT", "LIVE", "LONG", "MANY", "MOST", "MOVE", "MUST", "NAME", "NEED", "NEWS", "NEXT", "ONCE", "ONLY", "OPEN", "OVER", "PAID", "PATH", "PLAN", "PLUS", "REAL", "ROOM", "SAID", "SAME", "SEEM", "SHOW", "SIDE", "SIZE", "SORT", "SUCH", "SURE", "THAN", "THAT", "THEM", "THEY", "THIS", "THUS", "TOWN", "TRUE", "TURN", "USED", "USER", "VERY", "WALK", "WALL", "WAYS", "WEEK", "WENT", "WERE", "WHAT", "WHEN", "WILL", "WITH", "WORD", "WORK", "YOUR"],
    5: WORD_LISTS[5] + ["ABOUT", "ABOVE", "ABUSE", "ACTOR", "ACUTE", "ADMIT", "ADOPT", "ADULT", "AFTER", "AGENT", "AGREE", "AHEAD", "ALARM", "ALBUM", "ALERT", "ALIEN", "ALIGN", "ALIKE", "ALIVE", "ALLOW", "ALONE", "ALONG", "ALTER", "AMONG", "ANGER", "ANGLE", "ANGRY", "APART", "APPLE", "APPLY", "ARENA", "ARGUE", "ARISE", "ARRAY", "ARROW", "ASIDE", "ASSET", "AVOID", "AWAKE", "AWARD", "AWARE", "BADLY", "BAKER", "BASIC", "BEACH", "BEGAN", "BEGIN", "BEING", "BELOW", "BENCH", "BILLY", "BIRTH", "BLACK", "BLAME", "BLANK", "BLIND", "BLOCK", "BLOOD", "BOARD", "BOOST", "BOOTH", "BOUND", "BRAIN", "BRAND", "BRAVE", "BREAD", "BREAK", "BREED", "BRIEF", "BRING", "BROAD", "BROKE", "BROWN", "BUILD", "BUILT", "BUYER", "CABLE", "CANCER", "CARRY", "CATCH", "CAUSE", "CHAIN", "CHAIR", "CHAOS", "CHARM", "CHART", "CHASE", "CHEAP", "CHECK", "CHEST", "CHILD", "CHINA", "CHOSE", "CIVIL", "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLICK", "CLIMB", "CLOCK", "CLOSE", "CLOUD", "COACH", "COAST", "COULD", "COUNT", "COURT", "COVER", "CRAFT", "CRASH", "CRAZY", "CREAM", "CRIME", "CROSS", "CROWD", "CROWN", "CRUDE", "CURVE", "CYCLE", "DAILY", "DANCE", "DATED", "DEALT", "DEATH", "DEBUT", "DELAY", "DEPTH", "DOING", "DOUBT", "DOZEN", "DRAFT", "DRAMA", "DRANK", "DREAM", "DRESS", "DRILL", "DRINK", "DRIVE", "DROVE", "DYING", "EAGER", "EARLY", "EARTH", "EIGHT", "ELITE", "EMPTY", "ENEMY", "ENJOY", "ENTER", "ENTRY", "EQUAL", "ERROR", "EVENT", "EVERY", "EXACT", "EXIST", "EXTRA", "FAITH", "FALSE", "FAULT", "FIBER", "FIELD", "FIFTH", "FIFTY", "FIGHT", "FINAL", "FIRST", "FIXED", "FLASH", "FLEET", "FLOOR", "FLUID", "FOCUS", "FORCE", "FORTH", "FORTY", "FORUM", "FOUND", "FRAME", "FRANK", "FRAUD", "FRESH", "FRONT", "FRUIT", "FULLY", "FUNNY", "GIANT", "GIVEN", "GLASS", "GLOBE", "GOING", "GRACE", "GRADE", "GRAND", "GRANT", "GRASS", "GRAVE", "GREAT", "GREEN", "GROSS", "GROUP", "GROWN", "GUARD", "GUESS", "GUEST", "GUIDE", "HAPPY", "HARRY", "HEART", "HEAVY", "HENCE", "HENRY", "HORSE", "HOTEL", "HOUSE", "HUMAN", "IDEAL", "IMAGE", "INDEX", "INNER", "INPUT", "ISSUE", "JAPAN", "JIMMY", "JOINT", "JONES", "JUDGE", "KNOWN", "LABEL", "LARGE", "LASER", "LATER", "LAUGH", "LAYER", "LEARN", "LEASE", "LEAST", "LEAVE", "LEGAL", "LEVEL", "LEWIS", "LIGHT", "LIMIT", "LINKS", "LIVES", "LOCAL", "LOGIC", "LOOSE", "LOWER", "LUCKY", "LUNCH", "LYING", "MAGIC", "MAJOR", "MAKER", "MARCH", "MARIA", "MATCH", "MAYBE", "MAYOR", "MEANT", "MEDIA", "METAL", "MIGHT", "MINOR", "MINUS", "MIXED", "MODEL", "MONEY", "MONTH", "MORAL", "MOTOR", "MOUNT", "MOUSE", "MOUTH", "MOVED", "MOVIE", "MUSIC", "NEEDS", "NEVER", "NEWLY", "NIGHT", "NOISE", "NORTH", "NOTED", "NOVEL", "NURSE", "OCCUR", "OCEAN", "OFFER", "OFTEN", "ORDER", "OTHER", "OUGHT", "PAINT", "PANEL", "PAPER", "PARTY", "PEACE", "PETER", "PHASE", "PHONE", "PHOTO", "PIANO", "PIECE", "PILOT", "PITCH", "PLACE", "PLAIN", "PLANE", "PLANT", "PLATE", "POINT", "POUND", "POWER", "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIOR", "PRIZE", "PROOF", "PROUD", "PROVE", "QUEEN", "QUICK", "QUIET", "QUITE", "RADIO", "RAISE", "RANGE", "RAPID", "RATIO", "REACH", "READY", "REALM", "REBEL", "REFER", "RELAX", "RIDER", "RIDGE", "RIGHT", "RIGID", "RIVER", "ROBOT", "ROGER", "ROMAN", "ROUGH", "ROUND", "ROUTE", "ROYAL", "RURAL", "SCALE", "SCENE", "SCOPE", "SCORE", "SENSE", "SERVE", "SEVEN", "SHALL", "SHAPE", "SHARE", "SHARP", "SHEET", "SHELF", "SHELL", "SHIFT", "SHINE", "SHIRT", "SHOCK", "SHOOT", "SHORT", "SHOWN", "SIGHT", "SILLY", "SINCE", "SIXTH", "SIXTY", "SIZED", "SKILL", "SLEEP", "SLIDE", "SMALL", "SMART", "SMILE", "SMITH", "SMOKE", "SNAKE", "SNOW", "SOLID", "SOLVE", "SORRY", "SORT", "SOULS", "SOUND", "SOUTH", "SPACE", "SPARE", "SPEAK", "SPEED", "SPEND", "SPENT", "SPLIT", "SPOKE", "SPORT", "SQUAD", "STAFF", "STAGE", "STAKE", "STAND", "START", "STATE", "STEAM", "STEEL", "STEEP", "STEER", "STERN", "STICK", "STILL", "STOCK", "STONE", "STOOD", "STORE", "STORM", "STORY", "STRIP", "STUCK", "STUDY", "STUFF", "STYLE", "SUGAR", "SUITE", "SUPER", "SWEET", "TABLE", "TAKEN", "TASTE", "TAXES", "TEACH", "TEETH", "TERRY", "TEXAS", "THANK", "THEFT", "THEIR", "THEME", "THERE", "THESE", "THICK", "THING", "THINK", "THIRD", "THOSE", "THREE", "THREW", "THROW", "THUMB", "TIGHT", "TIRED", "TITLE", "TODAY", "TOPIC", "TOTAL", "TOUCH", "TOUGH", "TOWEL", "TOWER", "TRACK", "TRADE", "TRAIN", "TREAT", "TREND", "TRIAL", "TRIBE", "TRICK", "TRIED", "TRIES", "TRUCK", "TRULY", "TRUNK", "TRUST", "TRUTH", "TWICE", "UNCLE", "UNDER", "UNDUE", "UNION", "UNITY", "UNTIL", "UPPER", "UPSET", "URBAN", "USAGE", "USUAL", "VALID", "VALUE", "VIDEO", "VIRUS", "VISIT", "VITAL", "VOCAL", "VOICE", "WASTE", "WATCH", "WATER", "WHEEL", "WHERE", "WHICH", "WHILE", "WHITE", "WHOLE", "WHOSE", "WOMAN", "WOMEN", "WORLD", "WORRY", "WORSE", "WORST", "WORTH", "WOULD", "WRITE", "WRONG", "WROTE", "YOUNG", "YOURS", "YOUTH"],
    6: WORD_LISTS[6] + ["ACCEPT", "ACCESS", "ACROSS", "ACTION", "ACTIVE", "ACTUAL", "ADVICE", "AFFECT", "AFFORD", "AFRAID", "AGENCY", "AGENDA", "ALMOST", "ALWAYS", "AMOUNT", "ANIMAL", "ANNUAL", "ANSWER", "ANYONE", "ANYWAY", "APPEAR", "AROUND", "ARRIVE", "ARTIST", "ASPECT", "ASSESS", "ASSIST", "ASSUME", "ATTACK", "ATTEND", "AUGUST", "AUTHOR", "AVENUE", "BACKED", "BACKUP", "BARELY", "BARREL", "BATTLE", "BEAUTY", "BECAME", "BECOME", "BEFORE", "BEHALF", "BEHAVE", "BEHIND", "BELIEF", "BELONG", "BERLIN", "BETTER", "BEYOND", "BISHOP", "BORDER", "BOTTLE", "BOTTOM", "BOUGHT", "BRANCH", "BREATH", "BRIDGE", "BRIEF", "BRIGHT", "BRING", "BRITAIN", "BROKEN", "BUDGET", "BUNDLE", "BURDEN", "BUREAU", "BUTTON", "CAMERA", "CANCER", "CANNOT", "CARBON", "CAREER", "CASTLE", "CASUAL", "CAUGHT", "CENTER", "CENTRE", "CHANCE", "CHANGE", "CHARGE", "CHOICE", "CHOOSE", "CHOSEN", "CHURCH", "CIRCLE", "CLIENT", "CLOSED", "CLOSER", "COFFEE", "COLUMN", "COMBAT", "COMING", "COMMIT", "COMMON", "COMPLY", "COPPER", "CORNER", "CORPORATE", "COTTON", "COUNTY", "COUPLE", "COURSE", "COVERS", "CREATE", "CREDIT", "CRISIS", "CUSTOM", "DAMAGE", "DANGER", "DEALER", "DEBATE", "DECADE", "DECIDE", "DEFEAT", "DEFEND", "DEFINE", "DEGREE", "DELIVER", "DEMAND", "DEPEND", "DEPUTY", "DERIVE", "DESIGN", "DESIRE", "DETAIL", "DETECT", "DEVICE", "DIFFER", "DINNER", "DIRECT", "DOCTOR", "DOUBLE", "DRIVEN", "DRIVER", "DURING", "EASILY", "EATING", "EDITOR", "EFFECT", "EFFORT", "EIGHTH", "EITHER", "ELEVEN", "EMERGE", "EMPIRE", "EMPLOY", "ENABLE", "ENDING", "ENERGY", "ENGAGE", "ENGINE", "ENOUGH", "ENSURE", "ENTIRE", "EQUITY", "ESCAPE", "ESTATE", "ETHNIC", "EUROPE", "EVEN", "EVENT", "EVERY", "EXCEED", "EXCEPT", "EXCLUDE", "EXCUSE", "EXERCISE", "EXIST", "EXPAND", "EXPECT", "EXPERT", "EXPORT", "EXTEND", "EXTENT", "FABRIC", "FACIAL", "FACTOR", "FAILED", "FAIRLY", "FALLEN", "FAMILY", "FAMOUS", "FATHER", "FELLOW", "FEMALE", "FIGURE", "FILTER", "FINGER", "FINISH", "FISCAL", "FLIGHT", "FLYING", "FOLLOW", "FOOTER", "FOREIGN", "FOREST", "FORGET", "FORMAT", "FORMER", "FOSTER", "FOUGHT", "FOURTH", "FRANCE", "FRIEND", "FUTURE", "GADGET", "GAINED", "GALAXY", "GARAGE", "GARDEN", "GATHER", "GENDER", "GENTLE", "GERMAN", "GLOBAL", "GOLDEN", "GORDON", "GOVERN", "GROWTH", "GUILTY", "HANDLE", "HAPPEN", "HEADED", "HEALTH", "HEIGHT", "HELMET", "HEREBY", "HIDDEN", "HOLDER", "HONEST", "HUMAN", "HUNGRY", "HUNTER", "HURRIED", "IGNORE", "IMMUNE", "IMPACT", "IMPORT", "IMPOSE", "INCOME", "INDEED", "INDOOR", "INFANT", "INFORM", "INITIAL", "INJURY", "INSIDE", "INTEND", "INTENT", "INVEST", "INVITE", "ISLAND", "ITSELF", "JERSEY", "JOSEPH", "JUNIOR", "KILLED", "LABOUR", "LADDER", "LADIES", "LAPTOP", "LARGELY", "LAST", "LATELY", "LATTER", "LAUNCH", "LAWYER", "LEADER", "LEAGUE", "LEARNT", "LEATHER", "LEAVE", "LENGTH", "LESSON", "LETTER", "LIABLE", "LIGHTS", "LIKELY", "LINKED", "LIQUID", "LISTEN", "LITTLE", "LIVING", "LOSING", "LOVELY", "LOSING", "MACHINE", "MAINLY", "MAKEUP", "MANAGE", "MANNER", "MANUAL", "MARBLE", "MARGIN", "MARINE", "MARKED", "MARKET", "MARRIED", "MARTIN", "MASTER", "MATTER", "MATURE", "MEDIUM", "MEMBER", "MEMORY", "MENTAL", "MERELY", "MIDDLE", "MILLER", "MINING", "MINUTE", "MIRROR", "MISSING", "MOBILE", "MODERN", "MODIFY", "MOMENT", "MONTHLY", "MOSTLY", "MOTHER", "MOTION", "MOVING", "MURDER", "MUSCLE", "MUSEUM", "MUTUAL", "MYSELF", "NAMELY", "NARROW", "NATION", "NATIVE", "NATURE", "NEARBY", "NEARLY", "NIGHTS", "NOBODY", "NORMAL", "NOTICE", "NOTION", "OBJECT", "OBTAIN", "OCCUPY", "OCEAN", "OFFICE", "ONLINE", "OPTION", "ORANGE", "ORIGIN", "OUTPUT", "OVERALL", "OXFORD", "PACKED", "PALACE", "PANEL", "PARADE", "PARISH", "PARTLY", "PASSED", "PATENT", "PATTERN", "PAYING", "PEOPLE", "PERIOD", "PERMIT", "PERSON", "PETROL", "PHRASE", "PICKED", "PIECES", "PLANET", "PLATES", "PLAYER", "PLEASE", "PLENTY", "POCKET", "POLICE", "POLICY", "POLISH", "POOR", "PORTAL", "POSTED", "POTATO", "POUND", "PRAISE", "PREFER", "PRETTY", "PREVENT", "PRIEST", "PRIMARY", "PRIME", "PRINCE", "PRISON", "PROFIT", "PROPER", "PROVEN", "PUBLIC", "PURPLE", "PUSHED", "PUTS", "PUZZLE", "QUAINT", "RABBIT", "RACING", "RADICAL", "RAISED", "RANDOM", "RARELY", "RATHER", "RATING", "READER", "REALLY", "REASON", "REBEL", "RECALL", "RECENT", "RECORD", "REDUCE", "REFORM", "REFUSE", "REGARD", "REGION", "RELATE", "RELIEF", "REMAIN", "REMOTE", "REMOVE", "REPAIR", "REPEAT", "REPLACE", "REPLY", "REPORT", "RESCUE", "RESIST", "RESORT", "RESULT", "RETAIL", "RETIRE", "RETURN", "REVEAL", "REVIEW", "REWARD", "RIDING", "RISING", "ROBUST", "ROCKET", "ROLLED", "ROMANS", "RUBBER", "RULING", "RUNNING", "SACRED", "SAFELY", "SAFETY", "SALARY", "SAMPLE", "SAVING", "SAYING", "SCALE", "SCHEME", "SCHOOL", "SCIENCE", "SCREEN", "SCRIPT", "SEARCH", "SEASON", "SECOND", "SECRET", "SECTOR", "SECURE", "SEEING", "SEEKING", "SELECT", "SENATE", "SENIOR", "SERIES", "SERIOUS", "SERVICE", "SETTLE", "SEVERE", "SEXUAL", "SHADOW", "SHARED", "SHEETS", "SHOULD", "SHOWED", "SHOWER", "SHUT", "SIGNED", "SILENT", "SILVER", "SIMPLE", "SIMPLY", "SINGLE", "SISTER", "SLIGHT", "SMOOTH", "SOCIAL", "SOCKET", "SODIUM", "SOLELY", "SOLVED", "SOUGHT", "SOURCE", "SOVIET", "SPEAKS", "SPIRIT", "SPREAD", "SPRING", "SQUARE", "STABLE", "STAGES", "STAIRS", "STANCE", "STANDS", "STATUE", "STATUS", "STAYED", "STEADY", "STOLEN", "STORAGE", "STORED", "STRAIN", "STRAND", "STREAM", "STREET", "STRESS", "STRIKE", "STRING", "STROKE", "STRONG", "STRUCK", "STUDIO", "STUPID", "SUBMIT", "SUDDEN", "SUFFER", "SUMMER", "SUMMIT", "SUPPLY", "SURELY", "SURFACE", "SURVEY", "SWITCH", "SYMBOL", "SYSTEM", "TACKLE", "TAKING", "TALENT", "TALKED", "TARGET", "TAUGHT", "TEMPLE", "TENANT", "TENDER", "TENNIS", "THANKS", "THEORY", "THIRTY", "THOUGH", "THREAD", "THREAT", "THROWN", "TICKET", "TIMBER", "TIMING", "TISSUE", "TITLES", "TOILET", "TONGUE", "TONIGHT", "TOWARD", "TRAVEL", "TREATY", "TRYING", "TUNNEL", "TURNED", "TWELVE", "TWENTY", "TYPING", "UNABLE", "UNIQUE", "UNLESS", "UNLIKE", "UPDATE", "UPLOAD", "URGENT", "USEFUL", "VALLEY", "VARIED", "VECTOR", "VENDOR", "VENUE", "VERBAL", "VERSUS", "VESSEL", "VICTIM", "VIEWER", "VIOLET", "VISUAL", "VOLUME", "WALKER", "WALKED", "WANTED", "WARMER", "WEALTH", "WEAPON", "WEEKLY", "WEIGHT", "WIDELY", "WINDOW", "WINTER", "WITHIN", "WIZARD", "WONDER", "WOODEN", "WORKED", "WORKER", "WORTHY", "WRITER", "YELLOW"]
}

def is_valid_word(word: str, word_length: int) -> bool:
    """Check if a word is valid for the given word length"""
    word = word.upper()
    return word in ALL_VALID_WORDS.get(word_length, [])

difficulty_levels = {
    "easy": 4,
    "medium": 5,
    "hard": 6
}

# Game state storage
game_sessions = {}

# Database setup
DATABASE_PATH = "wordle_stats.db"

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            guesses INTEGER NOT NULL,
            won BOOLEAN NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT
        )
    ''')
    
    # Create user_stats table for additional stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY,
            total_games INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert initial stats row if it doesn't exist
    cursor.execute('INSERT OR IGNORE INTO user_stats (id) VALUES (1)')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

class GuessRequest(BaseModel):
    guess: str

class NewGameRequest(BaseModel):
    pass

class GameStats(BaseModel):
    total_games: int
    wins: int
    losses: int
    win_rate: float
    average_guesses: float
    guess_distribution: dict
    streak: int
    max_streak: int

def get_cell_color(guess, chosen_word):
    """Simple color logic for Wordle"""
    output = {'cells': [], 'message': ''}
    check_occurrence = chosen_word

    # First pass: mark correct letters in green
    for i, letter in enumerate(guess):
        if letter == chosen_word[i]:
            output['cells'].append("#1fdb0dff")  # green
            check_occurrence = check_occurrence.replace(letter, "", 1)
        else:
            output['cells'].append(None)

    # Second pass: mark present but misplaced (yellow) OR wrong entirely (red)
    for i, letter in enumerate(guess):
        if output['cells'][i] is None:
            if letter in check_occurrence:
                output['cells'][i] = '#e4c53aff'  # yellow
                check_occurrence = check_occurrence.replace(letter, "", 1)
            else:
                output['cells'][i] = "#d71717ff"  # red

    is_win = all(color == "#1fdb0dff" for color in output['cells'])
    return output, is_win

def save_game_to_db(word: str, difficulty: str, guesses: int, won: bool, session_id: str):
    """Save completed game to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO games (word, difficulty, guesses, won, session_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (word, difficulty, guesses, won, session_id))
    
    # Update user stats
    cursor.execute('SELECT current_streak FROM user_stats WHERE id = 1')
    current_streak = cursor.fetchone()[0]
    
    if won:
        new_streak = current_streak + 1
    else:
        new_streak = 0
    
    # Get max streak
    cursor.execute('SELECT max_streak FROM user_stats WHERE id = 1')
    max_streak = cursor.fetchone()[0]
    new_max_streak = max(max_streak, new_streak)
    
    cursor.execute('''
        UPDATE user_stats 
        SET current_streak = ?, max_streak = ?, last_updated = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (new_streak, new_max_streak))
    
    conn.commit()
    conn.close()

def calculate_stats():
    """Calculate game statistics from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get basic stats
    cursor.execute('SELECT COUNT(*) FROM games')
    total_games = cursor.fetchone()[0]
    
    if total_games == 0:
        conn.close()
        return {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "average_guesses": 0.0,
            "guess_distribution": {str(i): 0 for i in range(1, 7)},
            "streak": 0,
            "max_streak": 0,
            "difficulty_stats": {}
        }
    
    cursor.execute('SELECT COUNT(*) FROM games WHERE won = 1')
    wins = cursor.fetchone()[0]
    losses = total_games - wins
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0
    
    # Calculate average guesses for won games only
    cursor.execute('SELECT AVG(guesses) FROM games WHERE won = 1')
    avg_result = cursor.fetchone()[0]
    average_guesses = round(avg_result, 1) if avg_result else 0
    
    # Guess distribution (only for won games)
    guess_distribution = {str(i): 0 for i in range(1, 7)}
    cursor.execute('SELECT guesses, COUNT(*) FROM games WHERE won = 1 GROUP BY guesses')
    for guesses, count in cursor.fetchall():
        if 1 <= guesses <= 6:
            guess_distribution[str(guesses)] = count
    
    # Get streak info
    cursor.execute('SELECT current_streak, max_streak FROM user_stats WHERE id = 1')
    streak_info = cursor.fetchone()
    current_streak, max_streak = streak_info if streak_info else (0, 0)
    
    # Get difficulty stats
    cursor.execute('''
        SELECT difficulty, 
               COUNT(*) as total,
               SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins,
               AVG(CASE WHEN won = 1 THEN guesses END) as avg_guesses
        FROM games 
        GROUP BY difficulty
    ''')
    
    difficulty_stats = {}
    for row in cursor.fetchall():
        difficulty, total, wins_diff, avg_guesses_diff = row
        win_rate_diff = (wins_diff / total) * 100 if total > 0 else 0
        difficulty_stats[difficulty] = {
            "total_games": total,
            "wins": wins_diff,
            "win_rate": round(win_rate_diff, 1),
            "average_guesses": round(avg_guesses_diff, 1) if avg_guesses_diff else 0
        }
    
    conn.close()
    
    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 1),
        "average_guesses": average_guesses,
        "guess_distribution": guess_distribution,
        "streak": current_streak,
        "max_streak": max_streak,
        "difficulty_stats": difficulty_stats
    }

@app.post("/new-game/{difficulty}")
async def new_game(difficulty: str, data: NewGameRequest):
    if difficulty not in difficulty_levels:
        raise HTTPException(status_code=404, detail="Difficulty not found")
    
    word_length = difficulty_levels[difficulty]
    word_bank = WORD_LISTS[word_length]
    
    chosen_word = random.choice(word_bank)
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
    word_length = len(chosen_word)
    
    if len(guess) != word_length:
        raise HTTPException(status_code=400, detail=f"Guess must be {word_length} letters")
    
    # Validate that the guess is a real word
    if not is_valid_word(guess, word_length):
        raise HTTPException(status_code=400, detail=f"'{guess}' is not a valid word")
    
    result, is_win = get_cell_color(guess, chosen_word)
    session["guesses"] += 1
    
    if is_win:
        session["is_complete"] = True
        result["message"] = "You win!"
        # Save completed game to database
        save_game_to_db(chosen_word, session["difficulty"], session["guesses"], True, session_id)
    elif session["guesses"] >= session["max_guesses"]:
        session["is_complete"] = True
        result["message"] = f"Game Over! The word was {chosen_word}"
        # Save completed game to database
        save_game_to_db(chosen_word, session["difficulty"], session["guesses"], False, session_id)
    
    return {"cells": result['cells'], "message": result['message'], "won": is_win, "game_over": session["is_complete"]}

@app.get("/stats")
async def get_stats():
    """Get game statistics"""
    return calculate_stats()

@app.get("/history")
async def get_history():
    """Get recent game history"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT word, difficulty, guesses, won, timestamp 
        FROM games 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''')
    
    games = []
    for row in cursor.fetchall():
        word, difficulty, guesses, won, timestamp = row
        games.append({
            "word": word,
            "difficulty": difficulty,  
            "guesses": guesses,
            "won": bool(won),
            "timestamp": timestamp
        })
    
    conn.close()
    return {"games": games}

@app.post("/reset-stats")
async def reset_stats():
    """Reset all game statistics"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM games')
    cursor.execute('UPDATE user_stats SET current_streak = 0, max_streak = 0 WHERE id = 1')
    
    conn.commit()
    conn.close()
    
    return {"message": "Statistics reset successfully"}

@app.post("/validate-word")
async def validate_word(data: GuessRequest):
    """Check if a word is valid for any difficulty level"""
    word = data.guess.upper()
    word_length = len(word)
    
    if word_length not in [4, 5, 6]:
        return {"valid": False, "message": "Word must be 4, 5, or 6 letters long"}
    
    is_valid = is_valid_word(word, word_length)
    return {
        "valid": is_valid, 
        "message": "Valid word" if is_valid else f"'{word}' is not a valid word"
    }

@app.get("/")
async def root():
    return {"message": "Wordle Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
