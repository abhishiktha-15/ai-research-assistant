import { useState, useEffect } from 'react';
import UploadPapers from './components/UploadPapers';
import ChatInterface from './components/ChatInterface';
import { api } from './services/api';
import './index.css';

function App() {
    const [apiStatus, setApiStatus] = useState('checking');

    useEffect(() => {
        checkApiHealth();
    }, []);

    const checkApiHealth = async () => {
        try {
            await api.checkHealth();
            setApiStatus('healthy');
        } catch (error) {
            setApiStatus('error');
            console.error('API health check failed:', error);
        }
    };

    return (
        <div className="app">
            <header className="header">
                <h1>🤖 RAG2</h1>
                <p>AI Research Paper Assistant</p>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                    Upload PDFs, ask questions, get answers with citations
                </p>
            </header>

            {apiStatus === 'error' && (
                <div className="status-message status-error">
                    ⚠️ Cannot connect to API server. Make sure the backend is running on port 8000.
                </div>
            )}

            {apiStatus === 'checking' && (
                <div className="status-message status-info">
                    🔄 Connecting to API server...
                </div>
            )}

            <div style={{ display: 'grid', gap: '2rem' }}>
                <UploadPapers onUploadSuccess={() => { }} />
                <ChatInterface />
            </div>

            <footer style={{
                textAlign: 'center',
                marginTop: '3rem',
                color: 'var(--text-secondary)',
                fontSize: '0.9rem'
            }}>
                <p>Built with ❤️ using RAG, Endee Vector DB, and Gemini AI</p>
            </footer>
        </div>
    );
}

export default App;
