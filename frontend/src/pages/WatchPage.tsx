import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

interface Video {
  id: string;
  title: string;
  description: string;
  views: number;
  likes: number;
  uploader?: {
    id: number;
    username: string;
  };
}

interface Comment {
  id: number;
  text: string;
  author?: { username: string };
  likes: number;
}

function WatchPage() {
  const { id } = useParams();
  const [video, setVideo] = useState<Video | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchVideo();
      fetchComments();
    }
  }, [id]);

  const fetchVideo = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/videos/${id}`);
      const data = await res.json();
      setVideo(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/videos/${id}/comments`);
      const data = await res.json();
      setComments(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleLike = async () => {
    if (!video) return;
    try {
      await fetch(`http://localhost:8000/api/v1/videos/${video.id}/like?user_id=1`, {
        method: 'POST'
      });
      setVideo({ ...video, likes: video.likes + 1 });
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const res = await fetch(`http://localhost:8000/api/v1/videos/${id}/comments?user_id=1`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newComment })
      });
      const data = await res.json();
      setComments([data, ...comments]);
      setNewComment('');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (!video) return <div className="error">Видео не найдено</div>;

  return (
    <div className="watch-container">
      <div className="video-player">
        <video
          controls
          src={`http://localhost:8000/api/v1/videos/${video.id}/stream`}
          className="player"
        />
      </div>

      <div className="video-info-section">
        <h1>{video.title}</h1>
        <div className="video-meta">
          <div className="video-stats">
            <span>👁️ {video.views} просмотров</span>
            <button onClick={handleLike} className="like-btn">👍 {video.likes}</button>
          </div>
          <div className="uploader-info">
            <strong>📺 {video.uploader?.username || 'User'}</strong>
          </div>
        </div>
        <div className="video-description">
          <p>{video.description || 'Нет описания'}</p>
        </div>
      </div>

      <div className="comments-section">
        <h3>💬 Комментарии ({comments.length})</h3>
        <form onSubmit={handleComment} className="comment-form">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Напишите комментарий..."
            rows={3}
          />
          <button type="submit">Отправить</button>
        </form>
        <div className="comments-list">
          {comments.map((comment) => (
            <div key={comment.id} className="comment">
              <div className="comment-author">{comment.author?.username || 'User'}</div>
              <div className="comment-text">{comment.text}</div>
              <div className="comment-meta">❤️ {comment.likes}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default WatchPage;
