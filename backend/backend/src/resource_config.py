"""
Resource Configuration & Optimization Settings
Cấu hình tối ưu tài nguyên cho ứng dụng
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============= DATABASE CONFIGURATION =============
DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DB', 'legal_db'),
    'user': os.getenv('POSTGRES_USER', 'admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'admin'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# Connection Pool Settings
DB_POOL_CONFIG = {
    'minconn': 1,      # Số connection tối thiểu
    'maxconn': 5,      # Số connection tối đa (giảm từ 10 -> 5)
    'keepalive': 300,  # Giữ kết nối 5 phút
}

COLLECTION_NAME = "legal_documents"

# ============= ML MODEL CONFIGURATION =============
# Lazy Loading - chỉ load khi cần
ENABLE_LAZY_LOADING = True

# Model Paths
SVM_MODEL_DIR = "models/svm"

# Embedder Settings
EMBEDDER_MODEL = 'all-MiniLM-L6-v2'  # Lightweight model
EMBEDDER_DEVICE = 'cpu'  # Dùng CPU để tiết kiệm GPU memory

# ============= LLM CONFIGURATION =============
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"  # Model nhẹ, nhanh
LLM_TEMPERATURE = 0
LLM_MAX_TOKENS = 2048  # Giới hạn token output

# Cache settings
ENABLE_LLM_CACHE = True
CACHE_TTL = 3600  # Cache 1 giờ

# ============= RETRIEVAL CONFIGURATION =============
# Số documents retrieve mỗi query
DEFAULT_TOP_K = 3  # Giảm từ 5 -> 3
MAX_TOP_K = 5

# Batch processing
MAX_BATCH_SIZE = 10  # Xử lý tối đa 10 clauses cùng lúc

# ============= APPLICATION SETTINGS =============
# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (giảm từ 16MB)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
UPLOAD_FOLDER = 'uploads'
AUTO_CLEANUP_UPLOADS = True  # Tự động xóa file sau khi xử lý
CLEANUP_AFTER_HOURS = 1  # Xóa file sau 1 giờ

# Session
SESSION_LIFETIME = 3600  # 1 giờ

# Rate Limiting
ENABLE_RATE_LIMIT = True
RATE_LIMIT_PER_MINUTE = 10  # 10 requests/phút

# ============= MEMORY OPTIMIZATION =============
# Giới hạn memory usage
MAX_MEMORY_MB = 512  # 512MB cho embedder
CLEAR_CACHE_INTERVAL = 1800  # Clear cache mỗi 30 phút

# Processing
USE_MULTIPROCESSING = False  # Tắt multiprocessing để giảm memory
MAX_WORKERS = 2  # Giới hạn số workers

# ============= LOGGING =============
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENABLE_PERFORMANCE_LOGGING = True

# ============= DEVELOPMENT/PRODUCTION =============
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
