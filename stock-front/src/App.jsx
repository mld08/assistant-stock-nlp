import { useState, useEffect } from 'react';
import './App.css';
import FileUpload from './components/FileUpload.jsx';
import ChatWindow from './components/ChatWindow.jsx';
import { FiDatabase, FiCpu, FiBox, FiSun, FiMoon } from 'react-icons/fi';

function App() {
  const [dbStatus, setDbStatus] = useState(null);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('mandeme-theme') || 'dark';
  });

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('mandeme-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleUploadSuccess = (result) => {
    setDbStatus({
      loaded: true,
      message: result.message,
      rowCount: result.row_count,
    });
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header" id="app-header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">
              <FiBox />
            </div>
            <div className="logo-text">
              <h1>Mandeme Stock</h1>
              <span className="logo-subtitle">Assistant Intelligent</span>
            </div>
          </div>
        </div>
        <div className="header-right">
          {dbStatus && dbStatus.loaded && (
            <div className="db-badge" id="db-status">
              <FiDatabase className="db-badge-icon" />
              <span>{dbStatus.rowCount} articles</span>
            </div>
          )}
          <div className="ai-badge">
            <FiCpu className="ai-badge-icon" />
            <span>IA Locale</span>
          </div>
          <button
            id="theme-toggle"
            className="theme-toggle-btn"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
            title={theme === 'dark' ? 'Mode clair' : 'Mode sombre'}
          >
            <div className="theme-toggle-track">
              <FiSun className="theme-icon sun" />
              <FiMoon className="theme-icon moon" />
              <div className={`theme-toggle-thumb ${theme}`} />
            </div>
          </button>
        </div>
      </header>

      {/* Upload Zone */}
      <div className="upload-section" id="upload-section">
        <FileUpload onUploadSuccess={handleUploadSuccess} />
      </div>

      {/* Chat */}
      <main className="app-main">
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;
