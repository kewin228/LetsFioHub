window.deleteVideo = async function(id) {
    if (!confirm('Удалить видео?')) return;
    try {
        console.log('Удаляем видео:', id);
        const res = await fetch(`${API_URL}/api/videos/${id}`, { 
            method: 'DELETE', 
            headers: { 'Authorization': `Bearer ${token}` } 
        });
        console.log('Ответ:', res.status);
        if (res.ok) {
            alert('Видео удалено!');
            renderPage();
        } else {
            const error = await res.text();
            alert('Ошибка удаления: ' + error);
        }
    } catch(e) { 
        console.error('Ошибка:', e);
        alert('Ошибка: ' + e.message); 
    }
}
