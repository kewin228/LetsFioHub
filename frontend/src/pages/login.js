import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

const API_URL = process.env.NEXT_PUBLIC_API_URL + '/api';

export default function Login() {
  const router = useRouter();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch(API_URL + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Ошибка входа');
      } else {
        localStorage.setItem('token', data.access_token);
        router.push('/');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '20px', background: '#0F0F0F', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Head><title>Вход - LetsFioHub</title></Head>
      <div style={{ background: '#1a1a1a', padding: '40px', borderRadius: '10px', width: '100%', maxWidth: '400px' }}>
        <h2 style={{ textAlign: 'center', color: '#FF0000' }}>Вход</h2>
        {error && <div style={{ color: 'red', marginBottom: '15px', textAlign: 'center' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required style={{ width: '100%', padding: '12px', marginBottom: '15px', background: '#333', border: 'none', borderRadius: '8px', color: 'white', boxSizing: 'border-box' }} />
          <input name="password" type="password" placeholder="Пароль" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} required style={{ width: '100%', padding: '12px', marginBottom: '15px', background: '#333', border: 'none', borderRadius: '8px', color: 'white', boxSizing: 'border-box' }} />
          <button type="submit" disabled={loading} style={{ width: '100%', padding: '12px', background: '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' }}>{loading ? 'Вход...' : 'Войти'}</button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '20px' }}>Нет аккаунта? <a href="/register" style={{ color: '#FF0000' }}>Зарегистрироваться</a></p>
      </div>
    </div>
  );
}
