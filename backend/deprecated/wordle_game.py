import nltk
from nltk.corpus import words
import random

def getCellColor(guess,chosenWord= "DODAN"):
    # initialisation
    output = {'cells':[],'message':''}
    checkOccurrence = chosenWord

    # first pass: mark correct letters in green
    for i, letter in enumerate(guess):
        if letter == chosenWord[i]:
            output['cells'].append("#1fdb0dff")
            checkOccurrence = checkOccurrence.replace(letter, "", 1)
        else:
            output['cells'].append(None) # need to mark that the letter has been parsed

    # second pass: mark present but misplaced (yellow) OR wrong entirely (red)
    for i, letter in enumerate(guess):
        if output['cells'][i] is None: # only process letters that are NOT green
            if letter in checkOccurrence:
                output['cells'][i] = '#e4c53aff' # yellow color
                checkOccurrence = checkOccurrence.replace(letter, "", 1)
            else:
                output['cells'][i] = "#d71717ff" # red color
        
    #determine if guess is FULLY correct
    is_win = all(color == "#1fdb0dff" for color in output['cells'])
    return output, is_win

def wordle_turn(difficulty,guess):
    all_words = words.words()
    wordBank = [w.lower() for w in all_words if len(w) == difficulty and w.isalpha()]
    chosenWord = random.choice(wordBank)
    guess = guess.lower()

    output, is_win = getCellColor(guess,chosenWord)
    return output, is_win