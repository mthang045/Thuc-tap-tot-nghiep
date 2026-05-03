
    'corsheaders.middleware.CorsMiddleware',
# Database - chỉ dùng MongoDB, tất cả dữ liệu được truy cập qua pymongo trong app.py
# Django không cần database engine vì không dùng ORM
# MongoDB Configuration
MONGODB_DB = os.getenv('MONGODB_DB', 'legal_AI_db')

# REST Framework settings - không dùng vì app.py là Flask API
# Giữ nguyên để Django admin có thể chạy nếu cần