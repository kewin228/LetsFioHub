import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import WatchPage from './pages/WatchPage';
import UploadPage from './pages/UploadPage';
import ChannelPage from './pages/ChannelPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SearchPage from './pages/SearchPage';
import PlaylistsPage from './pages/PlaylistsPage';
import ThemeToggle from './components/ThemeToggle';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`;
    }
  };

  return (
    <Router>
      <div className="app">
        <header className="header">
          <div className="container">
            <div className="header-content">
              <Link to="/" className="logo">
                <img 
                  src="/images/logo.svg" 
                  alt="Let's figure it out" 
                  className="logo-svg"
                />
              </Link>
              
              <form onSubmit={handleSearch} className="search-form">
                <input
                  type="text"
                  placeholder="Поиск видео..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button type="submit">🔍</button>
              </form>

              <div className="nav-links">
                <ThemeToggle />
                <Link to="/playlists" className="nav-link" title="Плейлисты">📋</Link>
                <Link to="/upload" className="nav-link" title="Загрузить">📤</Link>
                <Link to="/login" className="nav-link" title="Войти">👤</Link>
              </div>
            </div>
          </div>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/watch/:id" element={<WatchPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/channel/:username" element={<ChannelPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/playlists" element={<PlaylistsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
