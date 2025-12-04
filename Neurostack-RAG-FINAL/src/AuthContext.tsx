// frontend/src/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// --- CONFIGURATION ---
// This must match your FastAPI backend's host and port for local testing
const API_BASE_URL = 'http://localhost:8000/api'; 

// --- TYPES ---
interface AuthContextType {
    token: string | null;
    isLoggedIn: boolean;
    login: (username: string, password: string, isSignup: boolean) => Promise<boolean>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// --- PROVIDER COMPONENT ---
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // Load token from localStorage on initial load
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('access_token')
    );

    useEffect(() => {
        if (token) {
            localStorage.setItem('access_token', token);
            // Set default Authorization header for ALL authenticated requests
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            localStorage.removeItem('access_token');
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [token]);

    const isLoggedIn = !!token;

    const login = async (username: string, password: string, isSignup: boolean = false): Promise<boolean> => {
        const endpoint = isSignup ? '/signup' : '/login';
        
        try {
            const response = await axios.post(`${API_BASE_URL}${endpoint}`, {
                username,
                password,
            });

            const new_token = response.data.access_token;
            setToken(new_token);
            return true;
        } catch (error) {
            const message = axios.isAxiosError(error) && error.response 
                ? error.response.data.detail 
                : 'An unknown network error occurred.';
            console.error(isSignup ? `Signup failed: ${message}` : `Login failed: ${message}`);
            alert(`Authentication Error: ${message}`);
            return false;
        }
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ token, isLoggedIn, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};