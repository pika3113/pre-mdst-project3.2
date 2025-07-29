# 🔤 Wordle Clone in React

A browser-based **Wordle clone** built using React, where players guess a 5-letter word within 6 attempts. The game mimics the mechanics of the original Wordle, with customized color feedback — including **🔴 red instead of the standard grey** for incorrect letters.

---

## 🎮 Features

- 🔡 Interactive 6x5 letter grid
- ⌨️ Keyboard input support:
  - Typing letters A–Z
  - `Backspace` to delete letters
  - `Enter` to submit guesses
- 🎨 Color-coded feedback per letter:
  - 🟩 **Green** — correct letter in the correct position
  - 🟨 **Yellow** — letter exists in the word but in the wrong position
  - 🔴 **Red** — letter does not exist in the target word
- 💬 Real-time messages (e.g., “Word must be 5 letters!”)
- 🔚 Game-over detection (on win or all attempts used)
- ⚙️ Easily extensible with backend word validation

---

## 🧠 Game Logic

### ✅ Input Handling
- Users type using a physical keyboard.
- Only letters are accepted; no symbols or numbers.
- Word is entered from left to right and submitted with `Enter`.

### 🚦 Color Feedback Rules
After each guess is submitted:
- **Green (`#6aaa64`)**: Letter is correct and in the correct position.
- **Yellow (`#c9b458`)**: Letter exists in the target word but in a different position. Yellow is only applied as many times as that letter appears in the word.
- **Red (`#ff4d4d`)**: Letter is not in the target word at all.

> Note: The color logic avoids over-highlighting duplicate letters and ensures fairness like the original Wordle.

---

## 🧱 Project Structure

```plaintext
.
├── src/
│   ├── App.js        # Renders the Wordle component
│   ├── Wordle.js     # Core game logic and rendering
│   ├── App.css       # Styling for grid, cells, and messages
├── public/
│   └── index.html
├── package.json
└── README.md
