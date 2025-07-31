// API configuration
console.log('All environment variables:', process.env);
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('VITE_API_URL specifically:', process.env.VITE_API_URL);

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
console.log('Final API_BASE_URL:', API_BASE_URL);
export { API_BASE_URL };