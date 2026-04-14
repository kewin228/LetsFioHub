import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
      } else {
        alert('Регистрация успешна! Теперь войдите.');
        navigate('/login');
      }
    } catch (error) {
      alert('Ошибка регистрации');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Регистрация</h2>
        <form onSubmit={handleSubmit}>
          <input 
            type="text" 
            placeholder="Имя пользователя" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            required 
          />
          <input 
            type="email" 
            placeholder="Email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required 
          />
          <input 
            type="password" 
            placeholder="Пароль" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
          />
          <button type="submit">Зарегистрироваться</button>
        </form>
        <p>Уже есть аккаунт? <Link to="/login">Войти</Link></p>
      </div>
    </div>
  );
}

export default RegisterPage;
