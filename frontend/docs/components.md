# Components Documentation

This document describes the reusable UI components in the Wordle game frontend.

## 🧩 Component Architecture

Components are organized by functionality and reusability:

```
src/components/
├── auth/              # Authentication related components
├── game/              # Game-specific components  
├── ui/                # Generic UI components
└── layout/            # Layout and navigation components
```

## 🔐 Authentication Components

### AuthModal
**File**: `src/components/auth/AuthModal.jsx`
**Purpose**: Handles user login and registration

#### Props
- `isOpen` (boolean) - Controls modal visibility
- `onClose` (function) - Called when modal is closed
- `initialMode` (string) - 'login' or 'register'

#### Features
- Toggleable login/register modes
- Form validation
- Auto-login after registration
- Google OAuth integration
- Error handling and display

#### Usage
```jsx
<AuthModal 
  isOpen={showAuth} 
  onClose={() => setShowAuth(false)}
  initialMode="login" 
/>
```

## 🎮 Game Components

### GameBoard
**File**: `src/components/game/GameBoard.jsx`
**Purpose**: Displays the main Wordle game grid

#### Props
- `guesses` (array) - Array of guess objects
- `currentGuess` (string) - Current input guess
- `gameStatus` (string) - 'playing', 'won', 'lost'

### WordRow
**File**: `src/components/game/WordRow.jsx`
**Purpose**: Individual row in the game grid

#### Props
- `guess` (string) - The guessed word
- `isCurrentGuess` (boolean) - If this is the active row
- `evaluation` (array) - Letter evaluations ('correct', 'present', 'absent')

### Keyboard
**File**: `src/components/game/Keyboard.jsx`
**Purpose**: Virtual keyboard for game input

#### Props
- `onKeyPress` (function) - Called when key is pressed
- `letterStates` (object) - Letter evaluation states for coloring

## 📊 Statistics Components

### StatsModal
**File**: `src/components/stats/StatsModal.jsx`
**Purpose**: Displays game statistics in a modal

#### Props
- `isOpen` (boolean) - Controls modal visibility
- `onClose` (function) - Called when modal is closed
- `stats` (object) - User statistics data

### GuessDistribution
**File**: `src/components/stats/GuessDistribution.jsx`
**Purpose**: Bar chart showing guess distribution

#### Props
- `distribution` (array) - Array of guess counts [1,2,3,4,5,6]

## 🎨 UI Components

### Button
**File**: `src/components/ui/Button.jsx`
**Purpose**: Reusable button component

#### Props
- `variant` (string) - 'primary', 'secondary', 'danger'
- `size` (string) - 'sm', 'md', 'lg'
- `disabled` (boolean)
- `onClick` (function)
- `children` (ReactNode)

### Modal
**File**: `src/components/ui/Modal.jsx`
**Purpose**: Generic modal wrapper

#### Props
- `isOpen` (boolean)
- `onClose` (function)
- `title` (string)
- `children` (ReactNode)

### LoadingSpinner
**File**: `src/components/ui/LoadingSpinner.jsx`
**Purpose**: Loading indicator

#### Props
- `size` (string) - 'sm', 'md', 'lg'
- `color` (string) - CSS color value

## 🏗️ Layout Components

### Header
**File**: `src/components/layout/Header.jsx`
**Purpose**: Application header with navigation and user menu

### Navigation
**File**: `src/components/layout/Navigation.jsx`
**Purpose**: Main navigation menu

### Footer
**File**: `src/components/layout/Footer.jsx`
**Purpose**: Application footer

## 🎯 Component Guidelines

### Best Practices
1. **Single Responsibility**: Each component has one clear purpose
2. **Props Validation**: Use PropTypes or TypeScript for prop validation
3. **Reusability**: Design components to be reusable across pages
4. **Accessibility**: Include proper ARIA labels and keyboard navigation
5. **Performance**: Use React.memo for expensive components

### Naming Conventions
- **PascalCase** for component names
- **camelCase** for props and functions
- **kebab-case** for CSS classes
- **UPPER_CASE** for constants

### File Structure
```jsx
// Component imports
import React from 'react';
import PropTypes from 'prop-types';

// Style imports
import './ComponentName.css';

// Component definition
const ComponentName = ({ prop1, prop2 }) => {
  // Component logic
  
  return (
    <div className="component-name">
      {/* JSX content */}
    </div>
  );
};

// PropTypes validation
ComponentName.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.func
};

// Default props
ComponentName.defaultProps = {
  prop2: () => {}
};

export default ComponentName;
```
