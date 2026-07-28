import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

const API_URL = 'https://letsfiohub-1.onrender.com/api';

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({ email: '', password: '', username: '', display_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch(API_URL + '/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Ошибка регистрации');
      } else {
        router.push('/login');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '20px', background: '#0F0F0F', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Head><title>Регистрация - LetsFioHub</title></Head>
      <div style={{ background: '#1a1a1a', padding: '40px', borderRadius: '10px', width: '100%', maxWidth: '400px' }}>
        <h2 style={{ textAlign: 'center', color: '#FF0000' }}>Регистрация</h2>
        {error && <div style={{ color: 'red', marginBottom: '15px', textAlign: 'center' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required style={{ width: '100%', padding: '12px', marginBottom: '15px', background: '#333', border: 'none', borderRadius: '8px', color: 'white', boxSizing: 'border-box' }} />
          <input name="username" placeholder="Username" value={form.username} onChange={(e) => setForm({...form, username: e.target.value})} required style={{ width: '100%', padding: '12px', marginBottom: '15px', background: '#333', border: 'none', borderRadius: '8px', color: 'white', boxSizing: 'border-box' }} />
          <input name="display_name" placeholder="Отображаемое имя" value={form.display_name} onChange={(e) => setForm({...form, display_name: e.target.value})} style={{ width: '100%', padding: '12px', marginBottom: '15px', background: '#333', border: 'none', borderRadius: '8px', color: 'white', boxSizing: 'border-box' }} />
          <input name="password" type="password" placeholder="Пароль" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} required style={{ width: '100%', padding: '12px', marginBottom: '15px', background: '#333', border: 'none', borderRadius: '8px', color: 'white', boxSizing: 'border-box' }} />
          <button type="submit" disabled={loading} style={{ width: '100%', padding: '12px', background: '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' }}>{loading ? 'Регистрация...' : 'Зарегистрироваться'}</button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '20px' }}>Уже есть аккаунт? <a href="/login" style={{ color: '#FF0000' }}>Войти</a></p>
      </div>
    </div>
  );
}
// Trigger Vercel rebuild
