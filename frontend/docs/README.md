# Frontend Documentation

Welcome to the Wordle Game Frontend documentation. This React + Vite application provides a modern, responsive user interface for the Wordle game with authentication, statistics, and multiplayer features.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   ├── pages/             # Main application pages/screens
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API communication and external services
│   ├── utils/             # Utility functions and helpers
│   ├── styles/            # CSS modules and styling
│   ├── assets/            # Static assets (images, icons)
│   ├── App.jsx            # Main application component
│   └── main.jsx           # Application entry point
├── public/                # Public static files
├── docs/                  # Documentation (this folder)
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
└── Dockerfile             # Container configuration
```

## 🧩 Architecture Overview

The frontend follows a **modular React architecture** with clear separation of concerns:

- **Components**: Reusable UI elements (buttons, modals, game boards)
- **Pages**: Complete screen layouts (landing, game, profile)
- **Hooks**: Custom React hooks for state management and side effects
- **Services**: API communication and data fetching
- **Utils**: Pure utility functions and helpers

## 🚀 Getting Started

### Development
```bash
npm install
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Docker
```bash
docker build -t wordle-frontend .
docker run -p 3000:80 wordle-frontend
```

## 📖 Documentation Sections

- [Components](./components.md) - UI component documentation
- [Pages](./pages.md) - Page/screen documentation  
- [API Integration](./api.md) - Backend communication
- [Authentication](./auth.md) - User authentication flow
- [Game Logic](./game.md) - Frontend game mechanics
- [Styling](./styling.md) - CSS and design system
- [Deployment](./deployment.md) - Build and deployment guide

## 🔗 Related Documentation

- [Backend API Documentation](../backend/docs/)
- [Docker Setup](../docker-compose.yml)
- [Project README](../README.md)
