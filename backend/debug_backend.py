import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from main import app
    from wordle_game import getCellColor
    print("✓ All imports successful")
    
    # Test the getCellColor function
    result, is_win = getCellColor("HELLO", "HELLO")
    print(f"✓ getCellColor test: {result}, win: {is_win}")
    
    # Test NLTK
    import nltk
    from nltk.corpus import words
    try:
        word_list = words.words()
        print(f"✓ NLTK working, found {len(word_list)} words")
    except LookupError:
        print("✗ NLTK words corpus not found, downloading...")
        nltk.download('words')
        word_list = words.words()
        print(f"✓ NLTK working after download, found {len(word_list)} words")
    
    print("✓ All backend components working correctly")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
