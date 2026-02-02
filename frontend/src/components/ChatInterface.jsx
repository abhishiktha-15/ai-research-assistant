import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

export default function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!question.trim() || loading) return;

        const userQuestion = question.trim();
        setQuestion('');
        setLoading(true);

        // Add user question to messages
        const newMessages = [
            ...messages,
            { type: 'question', content: userQuestion }
        ];
        setMessages(newMessages);

        try {
            const result = await api.queryPapers(userQuestion);

            // Add answer to messages
            setMessages([
                ...newMessages,
                {
                    type: 'answer',
                    content: result.answer,
                    sources: result.sources
                }
            ]);
        } catch (error) {
            setMessages([
                ...newMessages,
                {
                    type: 'answer',
                    content: `❌ Error: ${error.message}`,
                    sources: []
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const exampleQuestions = [
        "What are the main contributions of these papers?",
        "What methodology was used?",
        "What are the key findings?",
        "What future work is suggested?"
    ];

    const handleExampleClick = (q) => {
        setQuestion(q);
    };

    return (
        <div className="chat-container glass-card">
            <h2>💬 Ask Questions</h2>

            {messages.length === 0 ? (
                <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                        Try asking questions like:
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {exampleQuestions.map((q, i) => (
                            <button
                                key={i}
                                onClick={() => handleExampleClick(q)}
                                style={{
                                    background: 'rgba(102, 126, 234, 0.2)',
                                    border: '1px solid rgba(102, 126, 234, 0.3)',
                                    color: 'white',
                                    padding: '0.5rem 1rem',
                                    borderRadius: '15px',
                                    cursor: 'pointer',
                                    fontSize: '0.9rem',
                                    transition: 'all 0.3s ease'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.background = 'rgba(102, 126, 234, 0.3)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.background = 'rgba(102, 126, 234, 0.2)';
                                }}
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="messages-container">
                    {messages.map((msg, index) => (
                        <div key={index} className="message">
                            {msg.type === 'question' ? (
                                <div className="message-question">
                                    <strong>❓ You:</strong>
                                    <p style={{ marginTop: '0.5rem' }}>{msg.content}</p>
                                </div>
                            ) : (
                                <div className="message-answer">
                                    <strong>🤖 Assistant:</strong>
                                    <p style={{ marginTop: '0.5rem' }}>{msg.content}</p>

                                    {msg.sources && msg.sources.length > 0 && (
                                        <div className="sources">
                                            <p style={{ marginTop: '1rem', fontWeight: '600' }}>
                                                📚 Sources:
                                            </p>
                                            {msg.sources.map((source, i) => (
                                                <div key={i} className="source-card">
                                                    <div className="source-header">
                                                        <span>
                                                            {i + 1}. {source.paper} - {source.section}
                                                        </span>
                                                        <span className="similarity-badge">
                                                            {(source.similarity_score * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                        Page: {source.page || 'N/A'}
                                                    </div>
                                                    <div className="source-excerpt">
                                                        "{source.excerpt.substring(0, 150)}..."
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && (
                        <div className="message">
                            <div className="message-answer">
                                <div className="loading-spinner"></div>
                                <span style={{ marginLeft: '1rem' }}>Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            )}

            <form onSubmit={handleSubmit} className="input-form">
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a question about your papers..."
                    className="question-input"
                    disabled={loading}
                />
                <button
                    type="submit"
                    className="ask-button"
                    disabled={loading || !question.trim()}
                >
                    {loading ? 'Asking...' : 'Ask'}
                </button>
            </form>
        </div>
    );
}
