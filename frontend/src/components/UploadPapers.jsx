import { useState } from 'react';
import { api } from '../services/api';

export default function UploadPapers({ onUploadSuccess }) {
    const [uploading, setUploading] = useState(false);
    const [papers, setPapers] = useState([]);
    const [dragOver, setDragOver] = useState(false);
    const [status, setStatus] = useState(null);

    // Load papers on component mount
    useState(() => {
        loadPapers();
    }, []);

    const loadPapers = async () => {
        try {
            const data = await api.getPapers();
            setPapers(data);
        } catch (error) {
            console.error('Failed to load papers:', error);
        }
    };

    const handleFileSelect = async (e) => {
        const file = e.target.files?.[0];
        if (file) {
            await uploadFile(file);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files?.[0];
        if (file) {
            await uploadFile(file);
        }
    };

    const uploadFile = async (file) => {
        if (!file.name.endsWith('.pdf')) {
            setStatus({ type: 'error', message: 'Only PDF files are allowed' });
            return;
        }

        setUploading(true);
        setStatus(null);

        try {
            const result = await api.uploadPaper(file);
            setStatus({ type: 'success', message: result.message });
            await loadPapers();
            if (onUploadSuccess) onUploadSuccess();
        } catch (error) {
            setStatus({ type: 'error', message: error.message });
        } finally {
            setUploading(false);
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    return (
        <div className="upload-section glass-card">
            <h2>📄 Upload Research Papers</h2>

            {status && (
                <div className={`status-message status-${status.type}`}>
                    {status.type === 'success' ? '✓' : '✕'} {status.message}
                </div>
            )}

            <div
                className={`upload-zone ${dragOver ? 'dragover' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input').click()}
            >
                <div className="upload-icon">📤</div>
                <h3>{uploading ? 'Uploading...' : 'Drop PDF here or click to upload'}</h3>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                    Upload research papers to ask questions about them
                </p>
                <input
                    id="file-input"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="upload-input"
                    disabled={uploading}
                />
            </div>

            {papers.length > 0 && (
                <div className="papers-list">
                    <h3>📚 Uploaded Papers ({papers.length})</h3>
                    {papers.map((paper, index) => (
                        <div key={index} className="paper-item">
                            <span>📄 {paper.filename}</span>
                            <span style={{ color: 'var(--text-secondary)' }}>
                                {formatFileSize(paper.size_bytes)}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
