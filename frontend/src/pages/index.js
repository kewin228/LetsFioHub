import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Home() {
  const [videos, setVideos] = useState([]);
  const [theme, setTheme] = useState('default');

  const themes = ['default', 'cyberpunk', 'cod', 'fortnite', 'minecraft', 'valorant', 'lol', 'darksouls', 'apex'];

  const changeTheme = (newTheme) => {
    setTheme(newTheme);
    if (typeof window !== 'undefined') {
      document.body.setAttribute('data-theme', newTheme);
      localStorage.setItem('gamerTheme', newTheme);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('gamerTheme') || 'default';
      changeTheme(saved);
    }
  }, []);

  return (
    <div style={{ minHeight: '100vh', padding: '20px', background: 'var(--bg, #0F0F0F)', color: 'white' }}>
      <Head>
        <title>Let'sFioHub - Let's-1.0</title>
      </Head>

      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', padding: '20px', background: '#000', borderRadius: '10px' }}>
        <h1 style={{ color: 'var(--primary, #FF0000)', margin: 0 }}>🎬 Let'sFioHub</h1>
        <div>
          <button style={{ marginRight: '10px', padding: '10px 20px', background: 'var(--primary, #FF0000)', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Войти</button>
          <button style={{ padding: '10px 20px', background: 'var(--primary, #FF0000)', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Регистрация</button>
        </div>
      </header>

      <div style={{ marginBottom: '30px', padding: '20px', background: '#1a1a1a', borderRadius: '10px' }}>
        <h3 style={{ marginTop: 0 }}>🎮 Геймерские стили:</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {themes.map(t => (
            <button
              key={t}
              onClick={() => changeTheme(t)}
              style={{
                padding: '8px 16px',
                background: theme === t ? 'var(--primary, #FF0000)' : '#333',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                textTransform: 'capitalize',
                transition: 'all 0.3s'
              }}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <h2 style={{ marginBottom: '20px' }}>📺 Рекомендовано для вас</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        <div style={{ background: '#1a1a1a', borderRadius: '10px', overflow: 'hidden', transition: 'transform 0.3s' }}
             onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
             onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <div style={{ aspectRatio: '16/9', background: 'linear-gradient(135deg, var(--primary, #FF0000), var(--secondary, #CC0000))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontSize: '64px' }}>🎥</span>
          </div>
          <div style={{ padding: '15px' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>Пример видео</h3>
            <p style={{ color: '#888', margin: 0, fontSize: '14px' }}>👁 0 просмотров • 👍 0 лайков</p>
          </div>
        </div>
      </div>

      <style jsx global>{`
        :root {
          --primary: #FF0000;
          --secondary: #CC0000;
          --bg: #0F0F0F;
        }
        [data-theme="cyberpunk"] {
          --primary: #00FFFF;
          --secondary: #FF00FF;
          --bg: #0A0A0F;
        }
        [data-theme="cod"] {
          --primary: #FF6B00;
          --secondary: #FFD700;
          --bg: #1C1C1C;
        }
        [data-theme="fortnite"] {
          --primary: #9D4EDD;
          --secondary: #00F5FF;
          --bg: #2D1B4E;
        }
        [data-theme="minecraft"] {
          --primary: #5D8C3A;
          --secondary: #8B7355;
          --bg: #1E1E1E;
        }
        [data-theme="valorant"] {
          --primary: #FF4655;
          --secondary: #FFFFFF;
          --bg: #0F1923;
        }
        [data-theme="lol"] {
          --primary: #C8AA6E;
          --secondary: #0AC8B9;
          --bg: #091428;
        }
        [data-theme="darksouls"] {
          --primary: #8B0000;
          --secondary: #FFD700;
          --bg: #0D0D0D;
        }
        [data-theme="apex"] {
          --primary: #F26522;
          --secondary: #FFFFFF;
          --bg: #1A1A1A;
        }
        body {
          background: var(--bg);
          color: white;
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
      `}</style>
    </div>
  );
}
