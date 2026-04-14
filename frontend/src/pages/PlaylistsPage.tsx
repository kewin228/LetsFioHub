import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Playlist {
  id: number;
  name: string;
  description: string;
  videos: string[];
  video_details?: any[];
}

function PlaylistsPage() {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [newPlaylistName, setNewPlaylistName] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetchPlaylists();
  }, []);

  const fetchPlaylists = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/users/me/playlists?user_id=1');
      const data = await res.json();
      setPlaylists(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const createPlaylist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPlaylistName.trim()) return;

    try {
      const res = await fetch('http://localhost:8000/api/v1/playlists?user_id=1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newPlaylistName, description: '', is_public: true })
      });
      const data = await res.json();
      setPlaylists([...playlists, data]);
      setNewPlaylistName('');
      setShowCreate(false);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="container">
      <div className="playlists-header">
        <h1>📋 Мои плейлисты</h1>
        <button onClick={() => setShowCreate(!showCreate)} className="btn-primary">
          + Создать плейлист
        </button>
      </div>

      {showCreate && (
        <form onSubmit={createPlaylist} className="create-playlist-form">
          <input
            type="text"
            placeholder="Название плейлиста"
            value={newPlaylistName}
            onChange={(e) => setNewPlaylistName(e.target.value)}
            required
          />
          <button type="submit">Создать</button>
        </form>
      )}

      <div className="playlists-grid">
        {playlists.length === 0 ? (
          <p>У вас пока нет плейлистов</p>
        ) : (
          playlists.map((playlist) => (
            <div key={playlist.id} className="playlist-card">
              <h3>{playlist.name}</h3>
              <p>{playlist.description || 'Нет описания'}</p>
              <p>📹 {playlist.videos.length} видео</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default PlaylistsPage;
