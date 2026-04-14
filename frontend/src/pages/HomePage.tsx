import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Video {
  id: string;
  title: string;
  description: string;
  views: number;
  likes: number;
  uploader?: { id: number; username: string };
  created_at: string;
}

function HomePage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [trending, setTrending] = useState<Video[]>([]);
  const [recommendations, setRecommendations] = useState<Video[]>([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    try {
      const [videosRes, trendingRes, recsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/videos'),
        fetch('http://localhost:8000/api/v1/videos/trending'),
        fetch('http://localhost:8000/api/v1/videos/recommendations')
      ]);
      const videosData = await videosRes.json();
      const trendingData = await trendingRes.json();
      const recsData = await recsRes.json();
      
      setVideos(videosData.videos || []);
      setTrending(trendingData.trending || []);
      setRecommendations(recsData.recommendations || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatViews = (views: number) => {
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  const renderVideos = (videoList: Video[]) => (
    <div className="videos-grid">
      {videoList.map((video) => (
        <Link to={`/watch/${video.id}`} key={video.id} className="video-card-link">
          <div className="video-card">
            <div className="video-thumbnail">🎬</div>
            <div className="video-info">
              <h3>{video.title}</h3>
              <p>{video.uploader?.username || 'Unknown'}</p>
              <div className="video-stats">
                <span>👁️ {formatViews(video.views)}</span>
                <span>❤️ {video.likes}</span>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );

  if (loading) return <div className="loading">🎬 Загрузка видео...</div>;

  return (
    <div className="container">
      <div className="hero">
        <h1>Добро пожаловать в Let's FioHub</h1>
        <p>Смотрите, загружайте, делитесь видео</p>
      </div>

      <div className="tabs">
        <button className={activeTab === 'all' ? 'tab-active' : 'tab'} onClick={() => setActiveTab('all')}>
          📺 Все видео
        </button>
        <button className={activeTab === 'trending' ? 'tab-active' : 'tab'} onClick={() => setActiveTab('trending')}>
          🔥 Тренды
        </button>
        <button className={activeTab === 'recommended' ? 'tab-active' : 'tab'} onClick={() => setActiveTab('recommended')}>
          👍 Рекомендации
        </button>
      </div>

      {activeTab === 'all' && renderVideos(videos)}
      {activeTab === 'trending' && renderVideos(trending)}
      {activeTab === 'recommended' && renderVideos(recommendations)}

      {videos.length === 0 && activeTab === 'all' && (
        <div className="empty-state">
          <p>📭 Пока нет видео. Будьте первым!</p>
          <Link to="/upload" className="btn-primary">📤 Загрузить видео</Link>
        </div>
      )}
    </div>
  );
}

export default HomePage;
