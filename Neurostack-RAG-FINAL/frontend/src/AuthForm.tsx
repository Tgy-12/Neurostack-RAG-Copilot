import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';

interface AuthFormProps {
    isSignup: boolean;
}

const AuthForm: React.FC<AuthFormProps> = ({ isSignup }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await login(username, password, isSignup);
        if (success) {
            // Navigate to the protected chat page on success
            navigate('/chat');
        }
    };

    const styles: { [key: string]: React.CSSProperties } = {
        container: { padding: '20px', maxWidth: '400px', margin: '50px auto', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.1)', fontFamily: 'Arial, sans-serif' },
        form: { display: 'flex', flexDirection: 'column', gap: '15px' },
        input: { padding: '10px', border: '1px solid #ddd', borderRadius: '4px' },
        button: { padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' },
        switchButton: { background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline', padding: '0', fontSize: '14px' }
    };

    return (
        <div style={styles.container}>
            <h2>{isSignup ? 'Sign Up' : 'Log In'}</h2>
            <form onSubmit={handleSubmit} style={styles.form}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    style={styles.input}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={styles.input}
                />
                <button 
                    type="submit" 
                    style={styles.button}
                >
                    {isSignup ? 'Create Account' : 'Log In'}
                </button>
                <p style={{ marginTop: '5px', textAlign: 'center' }}>
                    {isSignup ? "Already have an account? " : "Don't have an account? "}
                    <button 
                        type="button" 
                        onClick={() => navigate(isSignup ? '/login' : '/signup')}
                        style={styles.switchButton}
                    >
                        {isSignup ? 'Log In' : 'Sign Up'}
                    </button>
                </p>
            </form>
        </div>
    );
};

export default AuthForm;