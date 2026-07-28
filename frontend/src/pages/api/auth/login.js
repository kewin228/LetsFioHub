export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        return res.status(response.status).json(data);
      }
      
      return res.status(200).json(data);
    } catch (error) {
      console.error('Login error:', error);
      return res.status(500).json({ detail: 'Ошибка сервера' });
    }
  }
  
  return res.status(405).json({ message: 'Method not allowed' });
}
