#Import english dict
from nltk.corpus import brown

# Download WordNet (only needed once)
import nltk
nltk.download('brown')

import random
import sys

# Get all words and group into 1 giant list
allWords = list(brown.words())

#Defining the different characteristics of words in each difficulty
easy = [word for word in allWords if 4 <= len(word) <= 5] # $3
medium = [word for word in allWords if 6 <= len(word) <= 7] # $5
hard = [word for word in allWords if len(word) == 8 ] # $7
extreme = [word for word in allWords if len(word) >= 9 ] # $10

# Defining the difficulty dictionary using the word lists
difficulty = {"easy": easy, "medium": medium, "hard": hard, "extreme": extreme}

# Command for display of current progress in hangman
def replace_char_with_list(display, indices, guess):
    display_list = display.replace (" ", "")
    display_list = list(display_list)
    for index in indices:
        display_list[index] = guess
    display_list = " ".join(display_list)
    return ''.join(display_list)

# Global variable across all games
money_Pool = 0

# Difficulty selector
def setDifficulty ():
  while True:
    print(f"Choose your difficulty: \nEasy - $3 \nMedium - $5 \nHard - $7 \nExtreme - $10")
    mode = input()
    mode = mode.lower()
    if mode == "easy" or mode == "medium" or mode == "hard" or mode == "extreme":
      return mode
    else:
      print ("Invalid input, please choose: Easy, Medium, Hard, Extreme")
      continue

# Money decided
def setMoney (difficulty):
  if difficulty == "easy":
    amount = 3
  elif difficulty == "medium":
    amount = 5
  elif difficulty == "hard":
    amount = 7
  elif difficulty == "extreme":
    amount = 10
  else:
      amount = 0 # Default or handle invalid difficulty

  return amount

def play_hangman(chosen_difficulty, earned_money):
    # Choose word choice
    global difficulty # Ensure the difficulty dictionary is accessible
    chosenWordList = difficulty[chosen_difficulty]
    chosenWord = random.choice(chosenWordList)
    chosenWord = chosenWord.upper()
    display = len(chosenWord) * "_ " # Initialize display here
    print (display)

    #Define the number of guesses
    guesses = 6
    used_letters = set() # Initialize a set to store used letters

    global money_Pool # Declare money_Pool as global to modify it

    while True:
        if guesses > 0:
            #print (f"The word has {len(chosenWord)} letters")
            print (f"Used letters: {' '.join(sorted(list(used_letters)))}") # Display used letters
            guess = input("Guess a letter or type '!' to guess the word: ") # Modified prompt
            guess = guess.upper()

            # Handle guessing the whole word
            if guess == "!":
                while True:
                    print (f"Would you like to guess the word? Y/N")
                    answer = input()
                    answer = answer.upper() # Convert answer to uppercase for consistent checking
                    if answer == "Y":
                      guessWord = input("Guess the word: ")
                      guessWord = guessWord.upper()
                      if guessWord == chosenWord:
                        print ("You win!")
                        money_Pool += earned_money # Correctly add earned_money
                        print (f"Total Money: ${money_Pool}")
                        return "win" # Return win status
                      else:
                        print("That's not the word. You lose.")
                        return "lose" # Return lose status
                    elif answer == "N":
                      break # Go back to guessing letters
                    else:
                      print ("Invalid input")
                      continue
                continue # Continue the outer game loop after deciding not to guess the word


            # Handle guessing a single letter
            if guess.isalpha() and len(guess) == 1:
                if guess in used_letters:
                    print(f"You already guessed the letter '{guess}'.")
                    print (f"Progress: {display} ")
                    continue # Skip the rest of the loop and ask for another guess

                used_letters.add(guess) # Add the guessed letter to the set

                presentLetter = set(chosenWord) # Move inside to be sure its for the current word
                if guess in presentLetter:
                    print (f"Correct!, you have {guesses} guesses remaining")
                    print (f"Progress: {display} ")

                    # Obtain the index of the guessed letter
                    letterPosition = [i for i, char in enumerate(chosenWord) if char == guess]

                    # For user friendly presentation
                    letterPositionPre = letterPosition.copy()
                    letterPositionPre = [x + 1 for x in letterPositionPre]
                    print (f"Positions: {letterPositionPre}")

                    display = replace_char_with_list(display, letterPosition, guess) # Use and update display
                    print (f"Progress: {display} ") # Print display

                    # Check if the word is fully guessed
                    if "_ " not in display:
                        print("Congratulations! You guessed the word!")
                        money_Pool += earned_money # Correctly add earned_money
                        print (f"Total Money: ${money_Pool}")
                        return "win" # Return win status

                else: # Check for answer (P2)
                    print (f"Wrong!, you have {guesses - 1} guesses remaining")
                    print (f"Progress: {display} ")
                    guesses -= 1

            else: # Handle invalid input for single letter guess
                print ("Invalid input, please enter a single letter or type '!' to guess the word.")

        else:
            print (f"Nice try, better luck next time. The word was {chosenWord} ")
            return "lose" # Return lose status


# Outer loop to play multiple games
while True:
    # Ensure setDifficulty and setMoney are defined in accessible cells
    chosen_difficulty = setDifficulty() # Call setDifficulty to get the mode
    earned_money = setMoney(chosen_difficulty) # Call setMoney to get the money
    game_result = play_hangman(chosen_difficulty, earned_money) # Play a game

    play_again = input("Do you want to play again? (Y/N): ").upper()
    if play_again != 'Y':
        break
    # The following elif was causing an IndentationError and has been removed.
    elif play_again == "N":
      sys.exit() # Use sys.exit() to exit the game
    else:
        print ("Invalid input. Please enter Y/N.")
        continue

print(f"Final Money Pool: ${money_Pool}")
money_Pool = 0 # Reset to 0 for when the game is resetted
print(f"Money Pool cleared. Current Money Pool: ${money_Pool}")