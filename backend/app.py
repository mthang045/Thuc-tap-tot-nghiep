"""
Flask Web Application for Legal Contract Reviewer
MongoDB-only architecture - No Django, Pure Flask + MongoDB
"""
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import secrets
import sys
import hashlib
from functools import wraps
import time
import atexit

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflow.graph import build_graph
from src.resource_config import (
    MAX_FILE_SIZE, ALLOWED_EXTENSIONS, UPLOAD_FOLDER,
    AUTO_CLEANUP_UPLOADS, CLEANUP_AFTER_HOURS, SESSION_LIFETIME,
    ENABLE_RATE_LIMIT, RATE_LIMIT_PER_MINUTE
)

# MongoDB Connection
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Kết nối MongoDB
try:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.getenv('MONGODB_DB', 'legal_db')
    
    mongo_client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    mongo_client.server_info()
    mongo_db = mongo_client[MONGODB_DB]
    
    # Collections
    users_collection = mongo_db['users']
    analysis_collection = mongo_db['analysis_history']
    contracts_collection = mongo_db['contracts']
    legal_docs_collection = mongo_db['legal_documents']
    
    # Tạo indexes
    users_collection.create_index('email', unique=True)
    users_collection.create_index('username', unique=True)
    analysis_collection.create_index([('user', 1), ('timestamp', -1)])
    
    print(f"✅ MongoDB connected: {MONGODB_DB}")
    print(f"✅ Collections: users, analysis_history, contracts, legal_documents")
    MONGODB_CONNECTED = True
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("⚠️ Will use in-memory storage instead")
    MONGODB_CONNECTED = False
    mongo_db = None
    users_collection = None
    analysis_collection = None
    contracts_collection = None
    legal_docs_collection = None

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# Enable CORS for frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Tạo thư mục uploads nếu chưa có
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Mock analysis history
ANALYSIS_HISTORY = []

# Cache cho analysis results
ANALYSIS_CACHE = {}
CACHE_TTL = 3600  # 1 giờ

# Rate limiting
RATE_LIMIT_STORE = {}

# Graph singleton - lazy initialization
_app_graph = None

def get_app_graph():
    """Lazy load graph để tiết kiệm tài nguyên"""
    global _app_graph
    if _app_graph is None:
        print("🔄 Building LangGraph (first time)...")
        _app_graph = build_graph()
    return _app_graph

def cleanup_old_files():
    """Xóa các file uploads cũ để tiết kiệm dung lượng"""
    if not AUTO_CLEANUP_UPLOADS:
        return
    
    now = time.time()
    cutoff = now - (CLEANUP_AFTER_HOURS * 3600)
    
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            if file_time < cutoff:
                try:
                    os.remove(filepath)
                    print(f"✓ Cleaned up old file: {filename}")
                except Exception as e:
                    print(f"⚠️ Error cleaning {filename}: {e}")

def rate_limit(f):
    """Decorator để giới hạn số requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ENABLE_RATE_LIMIT:
            return f(*args, **kwargs)
        
        user_id = session.get('user_email', request.remote_addr)
        now = time.time()
        
        if user_id not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[user_id] = []
        
        # Lọc requests trong 1 phút gần nhất
        RATE_LIMIT_STORE[user_id] = [
            t for t in RATE_LIMIT_STORE[user_id] 
            if now - t < 60
        ]
        
        if len(RATE_LIMIT_STORE[user_id]) >= RATE_LIMIT_PER_MINUTE:
            return jsonify({
                'success': False, 
                'message': 'Quá nhiều requests. Vui lòng thử lại sau.'
            }), 429
        
        RATE_LIMIT_STORE[user_id].append(now)
        return f(*args, **kwargs)
    
    return decorated_function

def get_cache_key(text):
    """Tạo cache key từ contract text"""
    return hashlib.md5(text.encode()).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Trang chu"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """API đăng nhập với MongoDB"""
    if not MONGODB_CONNECTED:
        return jsonify({'success': False, 'message': 'Database không khả dụng'}), 503
    
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email và mật khẩu không được để trống'}), 400
        
        # Tìm user trong MongoDB
        user = users_collection.find_one({
            '$or': [
                {'email': email},
                {'username': email}
            ]
        })
        
        if not user:
            return jsonify({'success': False, 'message': 'Email hoặc mật khẩu không đúng'}), 401
        
        # Kiểm tra password
        if check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_email'] = user['email']
            session['is_admin'] = user.get('is_admin', False)
            session.permanent = True
            
            return jsonify({
                'success': True,
                'email': user['email'],
                'is_admin': user.get('is_admin', False)
            })
        else:
            return jsonify({'success': False, 'message': 'Email hoặc mật khẩu không đúng'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': f'Lỗi đăng nhập: {str(e)}'}), 500

@app.route('/api/csrf/', methods=['GET'])
def get_csrf():
    """CSRF token endpoint for frontend"""
    return jsonify({'status': 'ok'}), 200

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    """API đăng ký với MongoDB"""
    if not MONGODB_CONNECTED:
        return jsonify({'success': False, 'message': 'Database không khả dụng'}), 503
    
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        username = data.get('username', email.split('@')[0] if email else '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email và mật khẩu không được để trống'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400
        
        # Kiểm tra email đã tồn tại
        if users_collection.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400
        
        # Kiểm tra username đã tồn tại
        if users_collection.find_one({'username': username}):
            # Tạo username unique
            count = users_collection.count_documents({})
            username = f"{username}_{count + 1}"
        
        # Tạo user mới trong MongoDB
        user_doc = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'is_admin': False,
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Tự động đăng nhập sau khi đăng ký
        session['user_id'] = user_id
        session['user_email'] = email
        session['is_admin'] = False
        session.permanent = True
        
        return jsonify({
            'success': True, 
            'message': 'Đăng ký thành công',
            'email': email,
            'user_id': user_id
        })
        
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'success': False, 'message': f'Lỗi đăng ký: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """API dang xuat"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/verify', methods=['GET'])
def verify_session():
    """API kiểm tra session"""
    if 'user_email' in session:
        return jsonify({
            'success': True,
            'user': {
                'email': session['user_email'],
                'is_admin': session.get('is_admin', False)
            }
        })
    return jsonify({'success': False, 'message': 'Chưa đăng nhập'}), 401

@app.route('/api/upload', methods=['POST'])
@rate_limit
def upload_file():
    """API upload và phân tích hợp đồng - với caching"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file được tải lên'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Đọc nội dung file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                contract_text = f.read()
        except:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    contract_text = f.read()
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Không đọc được file: {str(e)}'
                }), 500
        
        # Kiểm tra cache
        cache_key = get_cache_key(contract_text)
        now = time.time()
        
        if cache_key in ANALYSIS_CACHE:
            cached_data, cached_time = ANALYSIS_CACHE[cache_key]
            if now - cached_time < CACHE_TTL:
                print("✓ Using cached analysis result")
                # Cleanup file ngay sau khi đọc
                if AUTO_CLEANUP_UPLOADS:
                    try:
                        os.remove(filepath)
                    except:
                        pass
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'cached': True
                })
        
        # Gọi Agent để phân tích
        try:
            app_graph = get_app_graph()
            inputs = {"contract_text": contract_text}
            result = app_graph.invoke(inputs)
            
            # Parse kết quả
            analysis_data = {
                'contractName': filename,
                'uploadDate': datetime.now().strftime('%d/%m/%Y'),
                'finalReport': result.get('final_report', 'Không có kết quả phân tích'),
                'extractedClauses': result.get('extracted_clauses', [])[:10],  # Giới hạn
                'researchResults': result.get('research_results', [])[:5]  # Giới hạn
            }
            
            # Cache kết quả
            ANALYSIS_CACHE[cache_key] = (analysis_data, now)
            
            # Lưu vào MongoDB history
            history_doc = {
                'user': session['user_email'],
                'data': analysis_data,
                'timestamp': datetime.now(),
                'created_at': datetime.now()
            }
            
            if MONGODB_CONNECTED and analysis_collection is not None:
                try:
                    analysis_collection.insert_one(history_doc)
                    print("✅ Saved to MongoDB history")
                except Exception as e:
                    print(f"⚠️ Failed to save to MongoDB: {e}")
                    # Fallback to memory
                    ANALYSIS_HISTORY.append({
                        'id': len(ANALYSIS_HISTORY) + 1,
                        'user': session['user_email'],
                        'data': analysis_data,
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                # Fallback: Lưu vào memory nếu MongoDB không khả dụng
                ANALYSIS_HISTORY.append({
                    'id': len(ANALYSIS_HISTORY) + 1,
                    'user': session['user_email'],
                    'data': analysis_data,
                    'timestamp': datetime.now().isoformat()
                })
                # Giới hạn history size
                if len(ANALYSIS_HISTORY) > 100:
                    ANALYSIS_HISTORY.pop(0)
            
            # Cleanup file ngay sau khi phân tích xong
            if AUTO_CLEANUP_UPLOADS:
                try:
                    os.remove(filepath)
                except:
                    pass
            
            return jsonify({
                'success': True,
                'data': analysis_data
            })
        except Exception as e:
            # Cleanup file khi có lỗi
            if AUTO_CLEANUP_UPLOADS:
                try:
                    os.remove(filepath)
                except:
                    pass
            return jsonify({
                'success': False,
                'message': f'Lỗi khi phân tích: {str(e)}'
            }), 500
    
    return jsonify({'success': False, 'message': 'File không hợp lệ'}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    """API lay lich su phan tich - from MongoDB"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Vui long dang nhap'}), 401
    
    user_email = session['user_email']
    
    # Lấy từ MongoDB nếu có kết nối
    if MONGODB_CONNECTED and analysis_collection is not None:
        try:
            # Query MongoDB
            cursor = analysis_collection.find(
                {'user': user_email}
            ).sort('timestamp', -1).limit(100)
            
            user_history = []
            for idx, doc in enumerate(cursor):
                # Convert MongoDB document to dict
                history_item = {
                    'id': idx + 1,
                    'user': doc['user'],
                    'data': doc['data'],
                    'timestamp': doc['timestamp'].isoformat() if isinstance(doc['timestamp'], datetime) else doc['timestamp']
                }
                user_history.append(history_item)
            
            print(f"✅ Loaded {len(user_history)} items from MongoDB")
            return jsonify({
                'success': True,
                'history': user_history
            })
        except Exception as e:
            print(f"⚠️ MongoDB query failed: {e}")
            # Fallback to memory
    
    # Fallback: Lấy từ memory nếu MongoDB không khả dụng
    user_history = [h for h in ANALYSIS_HISTORY if h['user'] == user_email]
    
    return jsonify({
        'success': True,
        'history': user_history
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """API thong ke cho admin"""
    if 'user_email' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Khong co quyen truy cap'}), 403
    
    stats = {
        'totalUsers': len(USERS_DB),
        'totalAnalyses': len(ANALYSIS_HISTORY),
        'activeUsers': len(set(h['user'] for h in ANALYSIS_HISTORY))
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })

@app.route('/history')
def history():
    """History page"""
    if 'user_email' not in session:
        return redirect('/')
    return render_template('history.html')

@app.route('/settings')
def settings():
    """Trang cài đặt tài khoản"""
    if 'user_email' not in session:
        return redirect('/')
    return render_template('settings.html')

@app.route('/pricing')
def pricing():
    """Trang bảng giá"""
    return render_template('pricing.html')

@app.route('/admin')
def admin():
    """Trang admin dashboard"""
    if 'user_email' not in session or not session.get('is_admin'):
        return redirect('/')
    return render_template('admin.html')

# Cleanup tasks
@atexit.register
def shutdown():
    """Cleanup khi app shutdown"""
    print("🧹 Cleaning up resources...")
    cleanup_old_files()
    # Clear caches
    ANALYSIS_CACHE.clear()
    RATE_LIMIT_STORE.clear()

if __name__ == '__main__':
    # Cleanup old files khi khởi động
    cleanup_old_files()
    app.run(debug=True, host='0.0.0.0', port=5000)
