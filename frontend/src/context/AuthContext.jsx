import React, { createContext, useState, useEffect, useContext } from 'react';
import authService from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in on mount
        const checkUser = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    // Decode token or fetch user profile if endpoint exists
                    // For now, let's decode simpler or assume valid if distinct
                    // Ideally call /auth/me
                    // Since we didn't implement /auth/me, we rely on stored user info or just token presence + role
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        setUser(JSON.parse(storedUser));
                    }
                } catch (error) {
                    console.error("Auth check failed", error);
                    logout();
                }
            }
            setLoading(false);
        };
        checkUser();
    }, []);

    const login = async (username, password) => {
        const data = await authService.login(username, password);

        const { access_token, role } = data;
        localStorage.setItem('token', access_token);
        const userData = { username, role };
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        return userData;
    };

    const createSubAdmin = async (userData) => {
        const data = await authService.createSubAdmin(userData);
        return data;
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, createSubAdmin, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
