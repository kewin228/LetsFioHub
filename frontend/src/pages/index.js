import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

const API_URL = 'https://letsfiohub-1.onrender.com/api';

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Загружаем профиль пользователя
      fetch(API_URL + '/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error('Не авторизован');
        })
        .then(data => {
          setUser(data);
          setLoading(false);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.reload(); // Перезагружаем страницу
  };

  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#0F0F0F', color: 'white' }}>Загрузка...</div>;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0F0F0F', color: 'white' }}>
      <Head><title>LetsFioHub</title></Head>
      
      {/* Шапка */}
      <header style={{ padding: '20px', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: '#FF0000', margin: 0, cursor: 'pointer' }} onClick={() => router.push('/')}>LetsFioHub</h1>
        <div>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <span>Привет, <b>{user.display_name || user.username}</b>!</span>
              <button onClick={handleLogout} style={{ padding: '8px 16px', background: '#333', color: 'white', border: '1px solid #FF0000', borderRadius: '8px', cursor: 'pointer' }}>
                Выйти
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => router.push('/login')} style={{ padding: '8px 16px', background: 'transparent', color: 'white', border: '1px solid #FF0000', borderRadius: '8px', cursor: 'pointer' }}>
                Войти
              </button>
              <button onClick={() => router.push('/register')} style={{ padding: '8px 16px', background: '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                Регистрация
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Основной контент */}
      <main style={{ padding: '40px 20px', textAlign: 'center' }}>
        {user ? (
          <div>
            <h2>Добро пожаловать в твой профиль!</h2>
            <p>Email: {user.email}</p>
            <p>Имя пользователя: {user.username}</p>
          </div>
        ) : (
          <div>
            <h2>Добро пожаловать в LetsFioHub</h2>
            <p>Войдите или зарегистрируйтесь, чтобы получить доступ к видео.</p>
          </div>
        )}
      </main>
    </div>
  );
}
