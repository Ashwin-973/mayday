/**
 * Chat API client.
 * Handles streaming communication with the backend.
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Send a chat message and receive streaming response.
 * 
 * @param {string} sessionId - Session identifier
 * @param {string} message - User message
 * @param {function} onChunk - Callback for each response chunk
 * @param {function} onComplete - Callback when streaming completes
 * @param {function} onError - Callback for errors
 */
export async function sendMessage(sessionId, message, onChunk, onComplete, onError) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                onComplete?.();
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            onChunk?.(chunk);
        }
    } catch (error) {
        console.error('Chat API error:', error);
        onError?.(error);
    }
}

/**
 * Generate a unique session ID.
 * 
 * @returns {string} Session ID
 */
export function generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
}
