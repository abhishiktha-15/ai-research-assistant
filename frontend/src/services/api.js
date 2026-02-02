/**
 * API Service - Handles all backend communication
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
    /**
     * Check API health
     */
    async checkHealth() {
        const response = await fetch(`${API_URL}/api/health`);
        if (!response.ok) throw new Error('API health check failed');
        return response.json();
    },

    /**
     * Get list of uploaded papers
     */
    async getPapers() {
        const response = await fetch(`${API_URL}/api/papers`);
        if (!response.ok) throw new Error('Failed to fetch papers');
        return response.json();
    },

    /**
     * Upload a PDF paper
     */
    async uploadPaper(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/api/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    },

    /**
     * Query the papers with a question
     */
    async queryPapers(question, topK = 5) {
        const response = await fetch(`${API_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question,
                top_k: topK,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }

        return response.json();
    },

    /**
     * Trigger ingestion of all papers
     */
    async ingestAll() {
        const response = await fetch(`${API_URL}/api/ingest-all`, {
            method: 'POST',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ingestion failed');
        }

        return response.json();
    },
};
