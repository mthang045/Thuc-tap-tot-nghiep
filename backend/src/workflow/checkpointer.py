from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

# Chuỗi kết nối (giống bên trên)
DB_URI = "postgresql://admin:admin@localhost:5432/legal_db"

def get_checkpointer():
    """
    Tạo bộ nhớ dài hạn cho Agent dùng Postgres
    """
    pool = ConnectionPool(conninfo=DB_URI)
    
    # PostgresSaver cần được setup bảng trước khi dùng
    # (Hàm setup này chỉ cần chạy 1 lần lúc khởi tạo app)
    checkpointer = PostgresSaver(pool)
    checkpointer.setup() 
    
    return checkpointer