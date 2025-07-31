// API configuration - Use Vite's import.meta.env instead of process.env
console.log('All environment variables:', import.meta.env);
console.log('MODE:', import.meta.env.MODE);
console.log('VITE_API_URL specifically:', import.meta.env.VITE_API_URL);

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
console.log('Final API_BASE_URL:', API_BASE_URL);
export { API_BASE_URL };
