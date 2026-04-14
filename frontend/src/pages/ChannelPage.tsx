import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function ChannelPage() {
  const { username } = useParams();
  const [channel, setChannel] = useState<any>(null);

  useEffect(() => {
    fetchChannel();
  }, [username]);

  const fetchChannel = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/users/1`);
      const data = await res.json();
      setChannel(data);
    } catch (error) {
      setChannel({ username, display_name: username, subscriber_count: 0 });
    }
  };

  if (!channel) return <div className="loading">Загрузка...</div>;

  return (
    <div className="container">
      <div className="channel-header">
        <div className="channel-avatar">📺</div>
        <div className="channel-info">
          <h1>{channel.display_name || channel.username}</h1>
          <p>{channel.subscriber_count} подписчиков</p>
        </div>
      </div>
    </div>
  );
}

export default ChannelPage;
