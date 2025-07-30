// API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // Use nginx proxy in production
  : 'http://localhost:8000';  // Direct connection in development

export { API_BASE_URL };
