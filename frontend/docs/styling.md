# Styling Documentation

This document describes the CSS architecture and design system for the Wordle game frontend.

## 🎨 CSS Architecture

The styling system uses CSS modules with a component-based approach:

```
src/styles/
├── globals.css          # Global styles and CSS variables
├── theme.css           # Color themes and design tokens
├── components/         # Component-specific styles
│   ├── AuthModal.css
│   ├── GameBoard.css
│   ├── Keyboard.css
│   └── ...
├── pages/             # Page-specific styles
│   ├── LandingPage.css
│   ├── MenuScreen.css
│   └── ...
└── utils/             # Utility CSS classes
    ├── animations.css
    ├── layout.css
    └── responsive.css
```

## 🌈 Design System

### Color Palette
```css
/* src/styles/theme.css */
:root {
  /* Primary Colors */
  --color-primary: #6aaa64;      /* Correct (Green) */
  --color-secondary: #c9b458;    /* Present (Yellow) */
  --color-tertiary: #787c7e;     /* Absent (Gray) */
  
  /* Background Colors */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f6f7f8;
  --color-bg-dark: #121213;
  --color-bg-modal: rgba(0, 0, 0, 0.5);
  
  /* Text Colors */
  --color-text-primary: #1a1a1b;
  --color-text-secondary: #787c7e;
  --color-text-inverse: #ffffff;
  
  /* Border Colors */
  --color-border-light: #d3d6da;
  --color-border-medium: #878a8c;
  --color-border-dark: #3a3a3c;
  
  /* Status Colors */
  --color-success: #6aaa64;
  --color-warning: #c9b458;
  --color-error: #e74c3c;
  --color-info: #3498db;
}

/* Dark Theme */
[data-theme="dark"] {
  --color-bg-primary: #121213;
  --color-bg-secondary: #1a1a1b;
  --color-text-primary: #ffffff;
  --color-text-secondary: #818384;
  --color-border-light: #3a3a3c;
  --color-border-medium: #565758;
}
```

### Typography
```css
/* Font System */
:root {
  --font-family-primary: 'Helvetica Neue', Arial, sans-serif;
  --font-family-mono: 'Courier New', monospace;
  
  /* Font Sizes */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  
  /* Font Weights */
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line Heights */
  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### Spacing System
```css
/* Spacing Scale */
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */
  --spacing-20: 5rem;    /* 80px */
}
```

## 🎮 Game-Specific Styles

### Game Board
```css
/* src/styles/components/GameBoard.css */
.game-board {
  display: grid;
  grid-template-rows: repeat(6, 1fr);
  gap: var(--spacing-2);
  padding: var(--spacing-4);
  max-width: 350px;
  margin: 0 auto;
}

.game-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--spacing-2);
}

.game-letter {
  width: 62px;
  height: 62px;
  border: 2px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  transition: all 0.2s ease;
}

/* Letter States */
.letter-empty {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.letter-filled {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  border-color: var(--color-border-medium);
}

.letter-correct {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.letter-present {
  background-color: var(--color-secondary);
  color: var(--color-text-inverse);
  border-color: var(--color-secondary);
}

.letter-absent {
  background-color: var(--color-tertiary);
  color: var(--color-text-inverse);
  border-color: var(--color-tertiary);
}
```

### Keyboard
```css
/* src/styles/components/Keyboard.css */
.keyboard {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  padding: var(--spacing-4);
  max-width: 500px;
  margin: 0 auto;
}

.keyboard-row {
  display: flex;
  justify-content: center;
  gap: var(--spacing-1);
}

.keyboard-key {
  min-width: 43px;
  height: 58px;
  padding: 0 var(--spacing-2);
  border: none;
  border-radius: 4px;
  background-color: var(--color-border-light);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease;
  user-select: none;
}

.keyboard-key:hover {
  background-color: var(--color-border-medium);
}

.keyboard-key:active {
  transform: scale(0.95);
}

/* Key States */
.key-correct {
  background-color: var(--color-primary) !important;
  color: var(--color-text-inverse);
}

.key-present {
  background-color: var(--color-secondary) !important;
  color: var(--color-text-inverse);
}

.key-absent {
  background-color: var(--color-tertiary) !important;
  color: var(--color-text-inverse);
}

/* Special Keys */
.key-wide {
  min-width: 65px;
  font-size: var(--font-size-xs);
}

.key-enter {
  min-width: 80px;
}

.key-backspace {
  min-width: 80px;
}
```

## 🎭 Animations

### Flip Animation
```css
/* src/styles/utils/animations.css */
@keyframes letter-flip {
  0% {
    transform: rotateX(0);
  }
  50% {
    transform: rotateX(90deg);
  }
  100% {
    transform: rotateX(0);
  }
}

.letter-flip {
  animation: letter-flip 0.6s ease forwards;
}

/* Staggered animation delays */
.animation-delay-0 { animation-delay: 0ms; }
.animation-delay-1 { animation-delay: 100ms; }
.animation-delay-2 { animation-delay: 200ms; }
.animation-delay-3 { animation-delay: 300ms; }
.animation-delay-4 { animation-delay: 400ms; }
```

### Shake Animation
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

.shake {
  animation: shake 0.5s ease-in-out;
}
```

### Pop Animation
```css
@keyframes pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.pop {
  animation: pop 0.3s ease-in-out;
}
```

## 📱 Responsive Design

### Breakpoints
```css
/* src/styles/utils/responsive.css */
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}

/* Mobile Styles */
@media (max-width: 767px) {
  .game-letter {
    width: 50px;
    height: 50px;
    font-size: var(--font-size-lg);
  }
  
  .keyboard-key {
    min-width: 35px;
    height: 48px;
    font-size: var(--font-size-xs);
  }
  
  .container {
    padding: var(--spacing-2);
  }
}

/* Tablet Styles */
@media (min-width: 768px) and (max-width: 1023px) {
  .game-letter {
    width: 58px;
    height: 58px;
  }
  
  .container {
    padding: var(--spacing-4);
  }
}

/* Desktop Styles */
@media (min-width: 1024px) {
  .game-letter {
    width: 62px;
    height: 62px;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-6);
  }
}
```

## 🎨 Component Styling Guidelines

### Modal Styles
```css
/* src/styles/components/Modal.css */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-bg-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-4);
}

.modal-content {
  background-color: var(--color-bg-primary);
  border-radius: 8px;
  padding: var(--spacing-6);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.modal-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: var(--spacing-1);
}
```

### Button Styles
```css
/* src/styles/components/Button.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3) var(--spacing-6);
  border: none;
  border-radius: 6px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Button Variants */
.button-primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.button-primary:hover:not(:disabled) {
  background-color: #5a9a54;
}

.button-secondary {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
}

.button-secondary:hover:not(:disabled) {
  background-color: var(--color-border-light);
}

.button-danger {
  background-color: var(--color-error);
  color: var(--color-text-inverse);
}

.button-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

/* Button Sizes */
.button-sm {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
}

.button-lg {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
}
```

## 🌙 Dark Mode Implementation

### Theme Switching
```css
/* Automatic theme detection */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #121213;
    --color-bg-secondary: #1a1a1b;
    --color-text-primary: #ffffff;
    --color-text-secondary: #818384;
  }
}

/* Manual theme override */
[data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f6f7f8;
  --color-text-primary: #1a1a1b;
  --color-text-secondary: #787c7e;
}

[data-theme="dark"] {
  --color-bg-primary: #121213;
  --color-bg-secondary: #1a1a1b;
  --color-text-primary: #ffffff;
  --color-text-secondary: #818384;
}
```

### Theme Toggle Component
```javascript
// Theme toggle implementation
const ThemeToggle = () => {
  const [theme, setTheme] = useState('auto');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'auto';
    setTheme(savedTheme);
    applyTheme(savedTheme);
  }, []);

  const applyTheme = (newTheme) => {
    if (newTheme === 'auto') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', newTheme);
    }
    localStorage.setItem('theme', newTheme);
  };

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  return (
    <button onClick={toggleTheme} className="theme-toggle">
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
};
```

## 🎯 Performance Considerations

### CSS Optimization
- Use CSS custom properties for consistent theming
- Minimize repaints with `transform` and `opacity` for animations
- Use `will-change` sparingly for animation performance
- Prefer `flex` and `grid` over absolute positioning

### Critical CSS
- Inline critical CSS for above-the-fold content
- Load non-critical CSS asynchronously
- Use CSS modules to avoid style conflicts

### Animation Performance
```css
/* Optimized animations */
.optimized-animation {
  will-change: transform, opacity;
  transform: translateZ(0); /* Force hardware acceleration */
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```
