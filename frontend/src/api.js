import axios from 'axios';

// Automatically detect if we are in development (on port 5173) 
// and point to the backend (port 8000). 
// Otherwise, use relative paths (for unified deployment).
const getBaseURL = () => {
    // Rely entirely on relative paths so that Vite's server.proxy
    // or the production unified server handles routing seamlessly.
    return '';
};

const api = axios.create({
    baseURL: getBaseURL(),
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add a response interceptor to handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            // Redirect to login page
            // Since we are not in a React component, use window.location
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
