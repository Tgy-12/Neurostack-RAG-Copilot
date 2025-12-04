import React, { useState, FormEvent } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

// --- CONFIGURATION ---
const API_BASE_URL = 'http://localhost:8000/api'; 

// --- TYPES ---
interface RAGResponse {
    query: string;
    answer: string;
    source_chunks: string[];
    similarity_scores: string[];
    validation_status: string; // GROUNDED, REJECTED_LOW_CONTEXT, REJECTED_HALLUCINATION_CHECK, etc.
}

const ChatPage: React.FC = () => {
    const { logout } = useAuth();
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState<RAGResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;
        
        setLoading(true);
        setResponse(null);
        setError(null);

        try {
            // Axios uses the Authorization header set in AuthContext
            const res = await axios.post<RAGResponse>(
                `${API_BASE_URL}/copilot`, 
                { text: query },
            );
            setResponse(res.data);
            setQuery(''); // Clear the input after successful submission
        } catch (err) {
            const message = axios.isAxiosError(err) && err.response 
                ? err.response.data.detail || "Authentication Failed or Server Error" 
                : "A network error occurred.";
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        if (status.includes("GROUNDED")) return 'green';
        if (status.includes("REJECTED")) return 'red';
        if (status.includes("ERROR")) return 'purple';
        return 'orange';
    };

    const styles: { [key: string]: React.CSSProperties } = {
        container: { maxWidth: '900px', margin: '30px auto', padding: '20px', fontFamily: 'Arial, sans-serif', backgroundColor: '#fff', borderRadius: '8px' },
        header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #eee', paddingBottom: '10px', marginBottom: '20px' },
        logoutButton: { padding: '8px 15px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', transition: 'background-color 0.2s' },
        form: { display: 'flex', marginBottom: '30px' },
        input: { flexGrow: 1, padding: '12px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px 0 0 4px', outline: 'none' },
        submitButton: { padding: '12px 20px', backgroundColor: loading ? '#6c757d' : '#007bff', color: 'white', border: 'none', borderRadius: '0 4px 4px 0', cursor: 'pointer', transition: 'background-color 0.2s' },
        errorMessage: { color: 'red', marginBottom: '20px', padding: '10px', border: '1px solid red', backgroundColor: '#fee', borderRadius: '4px' },
        responseArea: { border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#f9f9f9' },
        chunkBox: { border: '1px dashed #bbb', padding: '15px', margin: '10px 0', borderRadius: '4px', backgroundColor: '#fff' },
        chunkHeader: { fontSize: '14px', color: '#555', marginBottom: '5px', borderBottom: '1px solid #eee', paddingBottom: '5px' },
        chunkText: { fontSize: '14px', whiteSpace: 'pre-wrap' }
    };

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h2>NeuroStack SaaS Copilot 🚀</h2>
                <button onClick={logout} style={styles.logoutButton}>Log Out</button>
            </div>
            
            <form onSubmit={handleSubmit} style={styles.form}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question about the documentation (e.g., How do I reset my password?)"
                    style={styles.input}
                    disabled={loading}
                />
                <button type="submit" style={styles.submitButton} disabled={loading}>
                    {loading ? 'Processing...' : 'Ask Copilot'}
                </button>
            </form>

            {error && <div style={styles.errorMessage}>Error: {error}</div>}

            {response && (
                <div style={styles.responseArea}>
                    <h3>🤖 Final Grounded Answer</h3>
                    <p style={{ fontWeight: 'bold' }}>{response.answer}</p>
                    
                    <p style={{ marginTop: '15px' }}>
                        **Validation Status:** <span style={{ color: getStatusColor(response.validation_status), fontWeight: 'bold' }}> 
                            {response.validation_status.replace(/_/g, ' ')}
                        </span>
                    </p>

                    <h3 style={{ marginTop: '20px' }}>📚 Retrieved Source Chunks ({response.source_chunks.length})</h3>
                    <p style={{ fontSize: '12px', color: '#777' }}>*Hybrid Retrieval Proof: Documents used to generate the answer.*</p>
                    {response.source_chunks.map((chunk, index) => (
                        <div key={index} style={styles.chunkBox}>
                            <p style={styles.chunkHeader}>
                                **Source {index + 1}** - {response.similarity_scores[index]}
                            </p>
                            <p style={styles.chunkText}>{chunk}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ChatPage;