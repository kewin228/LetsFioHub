from database import SessionLocal
from models import User, Video

db = SessionLocal()

try:
    # Удаляем все видео
    db.query(Video).delete()
    print("✅ Все видео удалены")
    
    # Удаляем всех пользователей
    db.query(User).delete()
    print("✅ Все пользователи удалены")
    
    db.commit()
    print("🎉 База данных очищена!")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    db.rollback()
finally:
    db.close()
