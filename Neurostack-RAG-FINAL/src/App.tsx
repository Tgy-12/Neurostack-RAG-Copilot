import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import AuthForm from './AuthForm';
import ChatPage from './ChatPage';

// Component to protect routes (Mandatory requirement)
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isLoggedIn } = useAuth();
    // If not logged in, redirect to the login page
    return isLoggedIn ? <>{children}</> : <Navigate to="/login" replace />;
};

const AppRoutes: React.FC = () => {
    return (
        <Routes>
            {/* Login and Signup routes */}
            <Route path="/login" element={<AuthForm isSignup={false} />} />
            <Route path="/signup" element={<AuthForm isSignup={true} />} />
            
            {/* The main protected chat application */}
            <Route 
                path="/chat" 
                element={
                    <ProtectedRoute>
                        <ChatPage />
                    </ProtectedRoute>
                } 
            />
            
            {/* Default route redirects to the chat (which forces login if needed) */}
            <Route path="/" element={<Navigate to="/chat" replace />} />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};


const App: React.FC = () => {
    return (
        <Router>
            <AuthProvider>
                <AppRoutes />
            </AuthProvider>
        </Router>
    );
};

export default App;