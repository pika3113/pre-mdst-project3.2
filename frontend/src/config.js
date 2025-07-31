// API configuration
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
console.log('API_BASE_URL:', API_BASE_URL);
export { API_BASE_URL };