import random
import time
from collections import deque
from nltk.corpus import brown
from nltk.probability import FreqDist

# Game Boundaries
DIFFICULTY_SETTINGS = {
    "easy": {"length": 4, "reward": 30},
    "normal": {"length": 5, "reward": 40},
    "hard": {"length": 6, "reward": 50},
}

IDEAL_STEPS = (4, 6)
TIME_BONUSES = [(20, 30), (60, 20), (120, 10)]
STREAK_BONUS = 100
HINT_COST_START = 10
HINT_COST_INCREMENT = 10

# Word List
def get_common_words(length):
    tokens = [w.lower() for w in brown.words() if w.isalpha()]
    fdist = FreqDist(tokens)
    return {w for w, _ in fdist.items() if len(w) == length}

# === Game Logic ===
def one_letter_diff(w1, w2):
    return sum(a != b for a, b in zip(w1, w2)) == 1

def find_shortest_path(start, end, word_list):
    visited = {start}
    queue = deque([(start, [])])
    while queue:
        current, path = queue.popleft()
        if current == end:
            return path + [end]
        for i in range(len(current)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c != current[i]:
                    neighbor = current[:i] + c + current[i+1:]
                    if neighbor in word_list and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
    return None

def get_random_pair(word_list, length):
    words = list(word_list)
    while True:
        w1, w2 = random.sample(words, 2)
        path = find_shortest_path(w1, w2, word_list)
        if path and IDEAL_STEPS[0] <= len(path) - 1 <= IDEAL_STEPS[1]:
            return w1, w2, path

def suggest_hint(current_word, target_word, word_list):
    path = find_shortest_path(current_word, target_word, word_list)
    return path[0] if path and len(path) > 0 else None

def calculate_time_bonus(seconds):
    for limit, bonus in TIME_BONUSES:
        if seconds <= limit:
            return bonus
    return 0

# Main Game
def play_game():
    money_pool = 0

    while True:
        print("\n=== MORPHLE ===")
        print(f"Current Balance: ${money_pool}")
        mode = input("Choose your difficulty (easy / normal / hard): ").strip().lower()
        if mode not in DIFFICULTY_SETTINGS:
            print("Oi choose properly lah.")
            continue

        config = DIFFICULTY_SETTINGS[mode]
        length = config["length"]
        reward = config["reward"]
        word_list = get_common_words(length)

        start_word, target_word, ideal_path = get_random_pair(word_list, length)

        print(f"\nTransform '{start_word.upper()}' to '{target_word.upper()}' (Word Length: {length})")
        print(f"Ideal steps: {len(ideal_path) - 1}")
        print(f"Use 'hint' to cheat a bit (starts at ${HINT_COST_START}, +${HINT_COST_INCREMENT} per use)")
        print("Type 'i quit' if you scared.\n")

        current_word = start_word
        hint_cost = HINT_COST_START
        hint_uses = 0
        mistakes = 0
        move_count = 0
        start_time = time.time()

        while current_word != target_word:
            print(f"\nYour cash: ${money_pool}")
            move = input(f"{current_word.upper()} -> ").strip().lower()

            if move == "i quit":
                print("Eh why sudd ghost?")
                return

            if move == "hint":
                hint = suggest_hint(current_word, target_word, word_list)
                if hint:
                    print(f"HINT: Try '{hint.upper()}' (-${hint_cost})")
                    money_pool -= hint_cost
                    hint_cost += HINT_COST_INCREMENT
                    hint_uses += 1
                else:
                    print("No hints for you, bro.")
                continue

            if len(move) != length or not move.isalpha():
                print("Wrong size lah. You blur ah?")
                mistakes += 1
                continue

            if not one_letter_diff(current_word, move):
                print("Running own programme is it?")
                mistakes += 1
                continue

            if move not in word_list:
                print("Fail English ah?")
                mistakes += 1
                continue

            current_word = move
            move_count += 1

        # Puzzle Complete
        duration = int(time.time() - start_time)
        time_bonus = calculate_time_bonus(duration)
        penalty = TIME_OVER_PENALTY if duration > TIME_CUTOFF else 0
        streak_bonus = STREAK_BONUS if hint_uses == 0 and mistakes == 0 else 0

        round_earnings = reward + time_bonus + streak_bonus - penalty
        money_pool += round_earnings

        print("\n=== PUZZLE COMPLETE ===")
        print(f"Path: {' -> '.join(ideal_path).upper()}")
        print(f"Time: {duration}s | Moves: {move_count} | Ideal: {len(ideal_path) - 1}")
        print(f"Base Reward: ${reward}")
        if time_bonus:
            print(f"Time Bonus: +${time_bonus}")
        if streak_bonus:
            print(f"Streak Bonus: +${streak_bonus}")
        if penalty:
            print(f"Time Penalty: -${penalty}")
        print(f"Round Earnings: ${round_earnings}")

        # Ensure money pool never goes negative
        if money_pool < 0:
            print("You went bankrupt this round, but nvm la we don't minus your bank.")
            money_pool = 0

        print(f"New Balance: ${money_pool}")

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != 'y':
            print(f"\nFinal Winnings: ${money_pool} — Not bad lah.")
            print("Go buy kopi or something.")
            break
