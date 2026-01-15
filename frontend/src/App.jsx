import { useState, useEffect, useRef } from 'react';
import { sendMessage, generateSessionId } from './api/chat';
import './styles/globals.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const messagesEndRef = useRef(null);
  const currentResponseRef = useRef('');

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);
    currentResponseRef.current = '';

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    // Add placeholder for agent message
    setMessages((prev) => [...prev, { role: 'agent', content: '', isStreaming: true }]);

    // Send message and handle streaming response
    await sendMessage(
      sessionId,
      userMessage,
      // onChunk
      (chunk) => {
        currentResponseRef.current += chunk;
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.role === 'agent') {
            lastMessage.content = currentResponseRef.current;
          }
          return newMessages;
        });
      },
      // onComplete
      () => {
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.role === 'agent') {
            lastMessage.isStreaming = false;
          }
          return newMessages;
        });
        setIsLoading(false);
      },
      // onError
      (error) => {
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.role === 'agent') {
            lastMessage.content = 'Sorry, I encountered an error. Please try again.';
            lastMessage.isStreaming = false;
          }
          return newMessages;
        });
        setIsLoading(false);
      }
    );
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <h1 className="header-title">AI Agent</h1>
          <p className="header-subtitle">Weather & Stock Information Assistant</p>
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">🤖</div>
            <h2 className="welcome-title">Hello! How can I help you?</h2>
            <p className="welcome-text">I can provide weather forecasts and stock prices.</p>
            <div className="example-queries">
              <div className="example-query">💭 "Weather in Chennai"</div>
              <div className="example-query">📈 "Tesla stock price"</div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-wrapper ${message.role === 'user' ? 'user-message-wrapper' : 'agent-message-wrapper'}`}
              >
                <div className={`message ${message.role === 'user' ? 'user-message' : 'agent-message'}`}>
                  <div className="message-content">
                    {message.content}
                    {message.isStreaming && <span className="cursor">▋</span>}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="input-container">
        <div className="input-wrapper">
          <input
            type="text"
            className="message-input"
            placeholder="Ask about weather or stocks..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button
            className={`send-button ${isLoading || !inputValue.trim() ? 'disabled' : ''}`}
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? (
              <svg className="loading-spinner" viewBox="0 0 24 24">
                <circle className="spinner-circle" cx="12" cy="12" r="10" />
              </svg>
            ) : (
              <svg className="send-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
