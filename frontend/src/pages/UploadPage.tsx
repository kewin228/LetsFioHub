import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function UploadPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) {
      alert('Заполните название и выберите файл');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/v1/videos/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      alert('Видео загружено!');
      navigate(`/watch/${data.video_id}`);
    } catch (error) {
      alert('Ошибка при загрузке');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container upload-container">
      <h1>Загрузить видео</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label>Название видео *</label>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Описание</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} />
        </div>
        <div className="form-group">
          <label>Видео файл *</label>
          <input type="file" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
        </div>
        <button type="submit" disabled={uploading}>{uploading ? 'Загрузка...' : 'Опубликовать'}</button>
      </form>
    </div>
  );
}

export default UploadPage;
