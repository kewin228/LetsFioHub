import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';

function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [results, setResults] = useState({ videos: [], channels: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query) {
      search();
    }
  }, [query]);

  const search = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Поиск...</div>;

  return (
    <div className="container">
      <h1>Результаты поиска: "{query}"</h1>
      
      {results.channels.length > 0 && (
        <div className="search-section">
          <h2>Каналы</h2>
          <div className="channels-list">
            {results.channels.map((channel: any) => (
              <Link to={`/channel/${channel.username}`} key={channel.id} className="channel-card">
                <div className="channel-avatar-small">📺</div>
                <div>
                  <h3>{channel.username}</h3>
                  <p>{channel.subscriber_count} подписчиков</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {results.videos.length > 0 && (
        <div className="search-section">
          <h2>Видео</h2>
          <div className="videos-grid">
            {results.videos.map((video: any) => (
              <Link to={`/watch/${video.id}`} key={video.id} className="video-card-link">
                <div className="video-card">
                  <div className="video-thumbnail">🎬</div>
                  <div className="video-info">
                    <h3>{video.title}</h3>
                    <p>{video.uploader?.username}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {results.videos.length === 0 && results.channels.length === 0 && (
        <p>Ничего не найдено</p>
      )}
    </div>
  );
}

export default SearchPage;
