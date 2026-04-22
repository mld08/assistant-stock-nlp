import { useState, useRef, useEffect, useCallback } from 'react';
import './ChatWindow.css';
import MessageBubble from './MessageBubble.jsx';
import { FiSend, FiCornerDownLeft } from 'react-icons/fi';
import { sendMessage } from '../services/api.js';

const WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'bot',
  content: "👋 Bienvenue dans l'**Assistant Stock Mandeme** !\n\nJe suis votre assistant intelligent de gestion de stock. Commencez par **uploader un fichier Excel** en haut, puis posez-moi vos questions.\n\nExemples :\n- *donne-moi l'article 10*\n- *CUMP de l'article 17*\n- *articles de la famille réseau*\n\nTapez **aide** pour voir toutes les commandes.",
  type: 'text',
  data: null,
};

const ChatWindow = () => {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: trimmed,
      type: 'text',
      data: null,
    };

    const loadingMessage = {
      id: Date.now() + 1,
      role: 'bot',
      content: '',
      type: 'text',
      data: null,
      isLoading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(trimmed);

      const botMessage = {
        id: Date.now() + 2,
        role: 'bot',
        content: response.message || '',
        type: response.type || 'text',
        data: response.data || null,
        columns: response.columns || null,
      };

      setMessages(prev => {
        const updated = prev.filter(m => !m.isLoading);
        return [...updated, botMessage];
      });
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 2,
        role: 'bot',
        content: `❌ **Erreur** : ${error.message}`,
        type: 'text',
        data: null,
      };

      setMessages(prev => {
        const updated = prev.filter(m => !m.isLoading);
        return [...updated, errorMessage];
      });
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    'Résumé du stock',
    'Tous les articles',
    'Familles disponibles',
    'Aide',
  ];

  const handleQuickAction = (action) => {
    setInput(action);
    // Use a ref to trigger send after state update
    setTimeout(() => {
      const fakeEvent = { trim: () => action };
      // Directly set and send
      setInput('');
      setIsLoading(true);

      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: action,
        type: 'text',
        data: null,
      };

      const loadingMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: '',
        type: 'text',
        data: null,
        isLoading: true,
      };

      setMessages(prev => [...prev, userMessage, loadingMessage]);

      sendMessage(action)
        .then(response => {
          const botMessage = {
            id: Date.now() + 2,
            role: 'bot',
            content: response.message || '',
            type: response.type || 'text',
            data: response.data || null,
            columns: response.columns || null,
          };
          setMessages(prev => {
            const updated = prev.filter(m => !m.isLoading);
            return [...updated, botMessage];
          });
        })
        .catch(error => {
          const errorMessage = {
            id: Date.now() + 2,
            role: 'bot',
            content: `❌ **Erreur** : ${error.message}`,
            type: 'text',
            data: null,
          };
          setMessages(prev => {
            const updated = prev.filter(m => !m.isLoading);
            return [...updated, errorMessage];
          });
        })
        .finally(() => {
          setIsLoading(false);
          inputRef.current?.focus();
        });
    }, 0);
  };

  return (
    <div className="chat-window">
      {/* Messages area */}
      <div className="chat-messages" id="chat-messages">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick actions */}
      {messages.length <= 1 && (
        <div className="quick-actions">
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              className="quick-action-btn"
              onClick={() => handleQuickAction(action)}
              disabled={isLoading}
            >
              {action}
            </button>
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            id="chat-input"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Posez votre question sur le stock..."
            rows={1}
            disabled={isLoading}
            aria-label="Message au chatbot"
          />
          <button
            id="send-button"
            className={`send-btn ${input.trim() ? 'active' : ''}`}
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            aria-label="Envoyer le message"
          >
            <FiSend />
          </button>
        </div>
        <div className="input-hint">
          <FiCornerDownLeft size={12} />
          <span>Entrée pour envoyer</span>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
