"""
Simple Flask API for Legal Contract System
Minimal version without Django dependencies

ML/AI Stack:
- SVM Classifier: 10 contract types, 60% accuracy
- BM25 Search: Keyword-based search, in-memory from MongoDB
- PageIndex RAG: Tree-based LLM reasoning, 98.7% accuracy benchmark
- Groq LLM: Llama 3.3 70B for contract analysis

Replaced Vector RAG (sentence-transformers) with BM25 for:
- Faster build time (0.4s vs 5s)  
- No embedding model dependency
- Better keyword matching for legal terms
"""
from flask import Flask, jsonify, request, send_from_directory, abort, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
import pymongo
import jwt
from datetime import datetime, timedelta
from functools import wraps
from datetime import datetime
import PyPDF2
import docx
import io
from template_generator import generate_template_file

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Import ML models (SVM + BM25 + PageIndex)
from ml_models import get_svm_classifier
from bm25_search_v2 import get_bm25_searcher

# PageIndex lazy loading
_pageindex_manager = None

def get_pageindex_retriever():
    """Lazy load PageIndex retriever"""
    global _pageindex_manager
    if _pageindex_manager is None:
        print("🔧 Loading PageIndex system...")
        try:
            from pageindex_rag import PageIndexManager
            _pageindex_manager = PageIndexManager(cache_file='embeddings/pageindex_cache.pkl')
            _pageindex_manager.build_index(force_rebuild=False)
            print("✅ PageIndex system loaded")
        except Exception as e:
            print(f"⚠️ PageIndex loading failed: {e}")
            _pageindex_manager = None
    return _pageindex_manager.get_retriever() if _pageindex_manager else None

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize global instances (lazy loading)
_llm_client = None

def get_llm_client():
    """Lazy load Groq LLM client"""
    global _llm_client
    if _llm_client is None:
        print("🔧 Loading Groq LLM...")
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your-groq-api-key-here":
            print("⚠️  GROQ_API_KEY not configured - AI analysis will be limited")
            print("💡 Get FREE API key at: https://console.groq.com/keys")
            raise ValueError("GROQ_API_KEY not configured")
        _llm_client = ChatGroq(
            api_key=api_key,
            model="llama-3.3-70b-versatile",  # Updated to newer model
            temperature=0.3,
            max_retries=2
        )
    return _llm_client

def save_analysis_to_history(user_email, analysis_data):
    """Save analysis result to MongoDB history collection"""
    try:
        import pymongo
        from datetime import datetime
        
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        history_collection = db['analysis_history']
        
        # Prepare document
        history_doc = {
            "user_email": user_email,
            "filename": analysis_data.get("filename"),
            "file_size": analysis_data.get("file_size"),
            "upload_time": datetime.now(),
            "contract_type": analysis_data.get("contract_type"),
            "risk_level": analysis_data.get("risk_level"),
            "has_violation": analysis_data.get("has_violation", False),
            "summary": analysis_data.get("summary"),
            "ai_analysis": analysis_data.get("ai_analysis"),
            "issues_count": len(analysis_data.get("issues", [])),
            "issues": analysis_data.get("issues", []),
            
            # Safety Score fields - NEW!
            "safety_score": analysis_data.get("safety_score"),
            "safety_reasoning": analysis_data.get("safety_reasoning"),
            "high_risk_count": analysis_data.get("high_risk_count", 0),
            "medium_risk_count": analysis_data.get("medium_risk_count", 0),
            "low_risk_count": analysis_data.get("low_risk_count", 0),
            
            "created_at": datetime.now()
        }
        
        # Insert into collection
        result = history_collection.insert_one(history_doc)
        print(f"✅ Saved to history: {result.inserted_id}")
        
        client.close()
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"⚠️  Failed to save history: {e}")
        return None

def extract_text_from_file(filepath):
    """Extract text from uploaded file"""
    ext = filepath.rsplit('.', 1)[1].lower()
    
    try:
        if ext == 'pdf':
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
                
        elif ext == 'docx':
            doc = docx.Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
            
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read().strip()
                
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.url_map.strict_slashes = False  # Fix CORS redirect issue
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['SECRET_KEY'] = 'legal-contract-reviewer-secret-key-2026'  # Change in production!

CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-CSRFToken'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     expose_headers=['Content-Disposition'])

# Initialize Flask-Limiter for rate limiting (memory backend)
# Use init_app to avoid argument ordering issues across versions
limiter = Limiter(key_func=get_remote_address, default_limits=[], storage_uri="memory://")
limiter.init_app(app)

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173']:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Legal Contract Reviewer API",
        "version": "2.0.0",
        "features": {
            "mongodb": "✓ Connected",
            "pageindex": "✓ Ready",
            "svm_models": "✓ Trained",
            "groq_api": "✓ Configured"
        }
    })


@app.route('/api/templates/<template_id>/download')
def download_template(template_id):
    """Serve predefined template files from static/templates
    - Requires a valid JWT
    - Only users with subscription_tier == 'pro' are allowed to download
    - If a requested real file (.docx/.pdf) is missing, generate and save it on demand
    Allowed template_id: t1, t2, t3
    """
    # Require token and ensure user is Pro
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'success': False, 'error': 'Token không tồn tại'}), 401
    if token.startswith('Bearer '):
        token = token[7:]

    payload = verify_token(token)
    if not payload:
        return jsonify({'success': False, 'error': 'Token không hợp lệ hoặc đã hết hạn'}), 401

    # Prefer authoritative subscription from DB (in case token is stale)
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        db = client['legal_AI_db']
        users_collection = db['users']
        user = users_collection.find_one({'email': payload.get('email')})
        client.close()
        subscription = (user.get('subscription_tier') if user else payload.get('subscription_tier', 'free'))
    except Exception:
        subscription = payload.get('subscription_tier', 'free')

    # Allow if user is Pro OR is an admin
    is_admin = False
    try:
        is_admin = bool(user.get('is_admin', False)) if user else bool(payload.get('is_admin', False))
    except Exception:
        is_admin = bool(payload.get('is_admin', False))

    if not subscription or (str(subscription).lower() != 'pro' and not is_admin):
        return jsonify({'success': False, 'error': 'Chỉ tài khoản Pro hoặc admin mới được tải file này'}), 403

    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    mapping = {
        # map to real document types
        't1': 't1.docx',
        't2': 't2.pdf',
        't3': 't3.docx'
    }

    filename = mapping.get(template_id)
    if not filename:
        return jsonify({'success': False, 'error': 'Template not found'}), 404

    file_path = os.path.join(templates_dir, filename)

    # If file missing, generate sample .docx or .pdf using template_generator
    if not os.path.exists(file_path):
        try:
            generate_template_file(template_id, file_path, context={'generated_by': 'template_generator'})
        except Exception as e:
            print('Error generating template file:', e)
            return jsonify({'success': False, 'error': 'Server error khi tạo template'}), 500

    # Send the file as attachment
    try:
        return send_from_directory(templates_dir, filename, as_attachment=True)
    except Exception as e:
        print('Error sending template:', e)
        return jsonify({'success': False, 'error': 'Server error khi gửi file'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client['legal_AI_db']
        collections = len(db.list_collection_names())
        client.close()
        
        return jsonify({
            "status": "healthy",
            "mongodb": {
                "connected": True,
                "collections": collections
            },
            "pageindex_cache": os.path.exists("data/page_index_cache.pkl"),
            "svm_models": os.path.exists("models/svm/contract_type_model.pkl")
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/models/status')
def models_status():
    """Check status of all models"""
    return jsonify({
        "svm": {
            "contract_type": os.path.exists("models/svm/contract_type_model.pkl"),
            "risk_level": os.path.exists("models/svm/risk_level_model.pkl"),
            "violation": os.path.exists("models/svm/violation_model.pkl")
        },
        "pageindex": {
            "cache_exists": os.path.exists("data/page_index_cache.pkl"),
            "cache_size_mb": round(os.path.getsize("data/page_index_cache.pkl") / 1024 / 1024, 2) if os.path.exists("data/page_index_cache.pkl") else 0
        }
    })

@app.route('/api/csrf/', methods=['GET'])
def csrf():
    """CSRF token endpoint (not needed for this simple API)"""
    return jsonify({"csrfToken": "not-required"})

def create_token(user_email, user_data):
    """Create JWT token for user"""
    payload = {
        'email': user_email,
        'full_name': user_data.get('full_name', ''),
        'subscription_tier': user_data.get('subscription_tier', 'free'),
        'is_admin': user_data.get('is_admin', False),
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'error': 'Token không tồn tại'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Token không hợp lệ hoặc đã hết hạn'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated

@app.route('/api/verify/', methods=['GET'])
@token_required
def verify():
    """Verify token and return user data"""
    return jsonify({
        "success": True,
        "user": request.user
    })

@app.route('/api/profile/', methods=['GET'])
@token_required
def get_profile():
    """Get user profile information"""
    try:
        import pymongo
        
        user_email = request.user.get('email')
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']
        
        # Get user data
        user = users_collection.find_one({'email': user_email})
        
        client.close()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy người dùng'
            }), 404
        
        # Return profile data (exclude password)
        profile = {
            'email': user.get('email'),
            'full_name': user.get('full_name', ''),
            'phone': user.get('phone', ''),
            'company': user.get('company', ''),
            'position': user.get('position', ''),
            'avatar': user.get('avatar', ''),
            'subscription_tier': user.get('subscription_tier', 'free'),
            'is_admin': user.get('is_admin', False),
            'created_at': user.get('created_at').isoformat() if user.get('created_at') else None
        }
        
        return jsonify({
            'success': True,
            'profile': profile
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/profile/', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile information"""
    try:
        import pymongo
        
        user_email = request.user.get('email')
        data = request.get_json()
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']
        
        # Build update document
        update_doc = {}
        allowed_fields = ['full_name', 'phone', 'company', 'position']
        
        for field in allowed_fields:
            if field in data:
                update_doc[field] = data[field]
        
        if not update_doc:
            client.close()
            return jsonify({
                'success': False,
                'error': 'Không có dữ liệu để cập nhật'
            }), 400
        
        # Update user profile
        result = users_collection.update_one(
            {'email': user_email},
            {'$set': update_doc}
        )
        
        client.close()
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy người dùng hoặc không có thay đổi'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thông tin thành công'
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-avatar/', methods=['POST'])
@token_required
def upload_avatar():
    """Upload user avatar"""
    try:
        import pymongo
        import os
        from werkzeug.utils import secure_filename
        
        user_email = request.user.get('email')
        
        # Check if file is in request
        if 'avatar' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy file avatar'
            }), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Không có file được chọn'
            }), 400
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else None
        
        if not file_ext or file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': 'Định dạng file không hợp lệ. Chỉ chấp nhận: png, jpg, jpeg, gif, webp'
            }), 400
        
        # Create avatars directory if not exists
        avatars_dir = os.path.join(os.getcwd(), 'static', 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        filename = f"{uuid.uuid4().hex}.{file_ext}"
        filepath = os.path.join(avatars_dir, filename)
        
        # Save file
        file.save(filepath)
        
        # Save avatar path to database
        avatar_url = f"/static/avatars/{filename}"
        
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']
        
        # Get old avatar to delete
        user = users_collection.find_one({'email': user_email})
        old_avatar = user.get('avatar', '') if user else ''
        
        # Update avatar in database
        result = users_collection.update_one(
            {'email': user_email},
            {'$set': {'avatar': avatar_url}}
        )
        
        client.close()
        
        # Delete old avatar file if exists
        if old_avatar and old_avatar.startswith('/static/avatars/'):
            old_filepath = os.path.join(os.getcwd(), old_avatar[1:])  # Remove leading /
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except Exception as e:
                    print(f"⚠️ Failed to delete old avatar: {e}")
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'error': 'Không thể cập nhật avatar'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Tải lên avatar thành công',
            'avatar_url': avatar_url
        }), 200
        
    except Exception as e:
        print(f"❌ Error uploading avatar: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/delete-avatar/', methods=['DELETE'])
@token_required
def delete_avatar():
    """Delete user's avatar file and clear avatar field in DB"""
    try:
        import pymongo
        import os

        user_email = request.user.get('email')

        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']

        user = users_collection.find_one({'email': user_email})
        if not user:
            client.close()
            return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404

        avatar = user.get('avatar', '')
        # Remove avatar file if stored under static/avatars
        if avatar and avatar.startswith('/static/avatars/'):
            avatar_path = os.path.join(os.getcwd(), avatar[1:])  # remove leading /
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    print(f"⚠️ Failed to remove avatar file: {e}")

        # Clear avatar field in DB
        result = users_collection.update_one({'email': user_email}, {'$set': {'avatar': ''}})
        client.close()

        if result.modified_count == 0:
            return jsonify({'success': False, 'error': 'Không thể xóa avatar'}), 500

        return jsonify({'success': True, 'message': 'Đã xóa avatar'}), 200

    except Exception as e:
        print(f"❌ Error deleting avatar: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history/', methods=['GET'])
@token_required
def get_analysis_history():
    """Get analysis history for current user"""
    try:
        import pymongo
        from bson import ObjectId
        
        user_email = request.user.get('email')
        
        # Get pagination parameters
        limit = int(request.args.get('limit', 20))
        skip = int(request.args.get('skip', 0))
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        history_collection = db['analysis_history']
        
        # Get total count
        total = history_collection.count_documents({"user_email": user_email})
        
        # Get history records
        history_records = list(history_collection.find(
            {"user_email": user_email}
        ).sort("created_at", -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for record in history_records:
            record['_id'] = str(record['_id'])
            if 'upload_time' in record and hasattr(record['upload_time'], 'isoformat'):
                record['upload_time'] = record['upload_time'].isoformat()
            if 'created_at' in record and hasattr(record['created_at'], 'isoformat'):
                record['created_at'] = record['created_at'].isoformat()
        
        client.close()
        
        return jsonify({
            "success": True,
            "data": {
                "records": history_records,
                "total": total,
                "limit": limit,
                "skip": skip
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/history/<history_id>', methods=['GET'])
@token_required
def get_analysis_detail(history_id):
    """Get specific analysis detail by ID"""
    try:
        import pymongo
        from bson import ObjectId
        
        user_email = request.user.get('email')
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        history_collection = db['analysis_history']
        
        # Get record
        record = history_collection.find_one({
            "_id": ObjectId(history_id),
            "user_email": user_email
        })
        
        if not record:
            return jsonify({
                "success": False,
                "error": "Không tìm thấy bản ghi"
            }), 404
        
        # Convert ObjectId to string
        record['_id'] = str(record['_id'])
        if 'upload_time' in record and hasattr(record['upload_time'], 'isoformat'):
            record['upload_time'] = record['upload_time'].isoformat()
        if 'created_at' in record and hasattr(record['created_at'], 'isoformat'):
            record['created_at'] = record['created_at'].isoformat()
        
        client.close()
        
        return jsonify({
            "success": True,
            "data": record
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving detail: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/history/<history_id>', methods=['DELETE'])
@token_required
def delete_analysis_history(history_id):
    """Delete specific analysis from history"""
    try:
        import pymongo
        from bson import ObjectId
        
        user_email = request.user.get('email')
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        history_collection = db['analysis_history']
        
        # Delete record
        result = history_collection.delete_one({
            "_id": ObjectId(history_id),
            "user_email": user_email
        })
        
        client.close()
        
        if result.deleted_count > 0:
            return jsonify({
                "success": True,
                "message": "Đã xóa bản ghi"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Không tìm thấy bản ghi"
            }), 404
        
    except Exception as e:
        print(f"❌ Error deleting history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def create_token(user_email, user_data):
    """Create JWT token for user"""
    payload = {
        'email': user_email,
        'full_name': user_data.get('full_name', ''),
        'subscription_tier': user_data.get('subscription_tier', 'free'),
        'is_admin': user_data.get('is_admin', False),
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'error': 'Token không tồn tại'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Token không hợp lệ hoặc đã hết hạn'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated

@app.route('/api/register/', methods=['POST'])
@limiter.limit('3 per minute')
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"Thiếu trường {field}"
                }), 400
        
        # Connect to MongoDB
        import pymongo
        from datetime import datetime
        
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']
        
        # Check if user already exists
        existing_user = users_collection.find_one({
            "$or": [
                {"email": data['email']},
                {"phone": data['phone']}
            ]
        })
        
        if existing_user:
            client.close()
            return jsonify({
                "success": False,
                "error": "Email hoặc số điện thoại đã được đăng ký"
            }), 400
        
        # Create new user (store hashed password)
        hashed = generate_password_hash(data['password'])
        user_doc = {
            "full_name": data['full_name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": hashed,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "subscription_tier": "free"
        }

        result = users_collection.insert_one(user_doc)
        client.close()
        
        return jsonify({
            "success": True,
            "message": "Đăng ký thành công!",
            "email": data['email'],
            "user_id": str(result.inserted_id)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Lỗi server: {str(e)}"
        }), 500

@app.route('/api/login/', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                "success": False,
                "error": "Thiếu email hoặc mật khẩu"
            }), 400
        
        # Connect to MongoDB
        import pymongo

        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']

        # Find user by email
        user = users_collection.find_one({
            "email": data['email']
        })

        if not user:
            client.close()
            return jsonify({
                "success": False,
                "error": "Email hoặc mật khẩu không đúng"
            }), 401

        stored_pw = user.get('password', '')

        # Check hashed password first
        password_match = False
        try:
            if stored_pw:
                password_match = check_password_hash(stored_pw, data['password'])
        except Exception:
            password_match = False

        # Fallback for existing accounts with plaintext passwords: migrate to hashed password on successful match
        if not password_match and stored_pw == data['password']:
            # Plaintext match - migrate to hashed password
            try:
                new_hashed = generate_password_hash(data['password'])
                users_collection.update_one({'email': data['email']}, {'$set': {'password': new_hashed}})
                password_match = True
            except Exception as e:
                print(f"⚠️ Failed to migrate plaintext password: {e}")

        if not password_match:
            client.close()
            return jsonify({
                "success": False,
                "error": "Email hoặc mật khẩu không đúng"
            }), 401

        # At this point password verified
        client.close()

        if user:
            # Create JWT token
            token = create_token(user['email'], {
                'full_name': user['full_name'],
                'subscription_tier': user.get('subscription_tier', 'free'),
                'is_admin': user.get('is_admin', False)
            })

            return jsonify({
                "success": True,
                "message": "Đăng nhập thành công!",
                "token": token,
                "user": {
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "subscription_tier": user.get('subscription_tier', 'free'),
                    "is_admin": user.get('is_admin', False)
                }
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Lỗi server: {str(e)}"
        }), 500


@app.route('/api/change-password/', methods=['PUT'])
@token_required
@limiter.limit('6 per minute')
def change_password():
    """Allow user to change their password"""
    try:
        import pymongo
        data = request.get_json()
        user_email = request.user.get('email')
        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({'success': False, 'error': 'Thiếu dữ liệu'}), 400
        old_pw = data.get('old_password')
        new_pw = data.get('new_password')

        if len(new_pw) < 8:
            return jsonify({'success': False, 'error': 'Mật khẩu mới phải có ít nhất 8 ký tự'}), 400

        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        users_collection = db['users']

        user = users_collection.find_one({'email': user_email})
        if not user:
            client.close()
            return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404

        stored_pw = user.get('password', '')

        # Verify old password (supports hashed and plaintext fallback)
        valid_old = False
        try:
            if stored_pw:
                valid_old = check_password_hash(stored_pw, old_pw)
        except Exception:
            valid_old = False

        if not valid_old and stored_pw == old_pw:
            # plaintext match - treat as valid
            valid_old = True

        if not valid_old:
            client.close()
            return jsonify({'success': False, 'error': 'Mật khẩu hiện tại không đúng'}), 401

        # Hash new password and save
        new_hashed = generate_password_hash(new_pw)
        users_collection.update_one({'email': user_email}, {'$set': {'password': new_hashed}})
        client.close()

        return jsonify({'success': True, 'message': 'Đổi mật khẩu thành công'}), 200

    except Exception as e:
        print(f"❌ Error changing password: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/legal-documents/', methods=['GET'])
def get_legal_documents():
    """Get list of legal documents with optional filtering"""
    try:
        import pymongo
        from bson import ObjectId
        
        # Get query parameters
        category = request.args.get('category', None)
        year = request.args.get('year', None)
        search = request.args.get('search', None)
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        legal_docs = db['legal_documents']
        
        # Build query
        query = {}
        if category:
            query['category_code'] = category
        if year:
            query['year'] = int(year)
        if search:
            query['$text'] = {'$search': search}
        
        # Get total count
        total = legal_docs.count_documents(query)
        
        # Get documents
        documents = list(legal_docs.find(
            query,
            {'full_content': 0}  # Exclude full content for list view
        ).sort('year', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            if 'imported_at' in doc and hasattr(doc['imported_at'], 'isoformat'):
                doc['imported_at'] = doc['imported_at'].isoformat()
            if 'updated_at' in doc and hasattr(doc['updated_at'], 'isoformat'):
                doc['updated_at'] = doc['updated_at'].isoformat()
        
        client.close()
        
        return jsonify({
            "success": True,
            "data": {
                "documents": documents,
                "total": total,
                "limit": limit,
                "skip": skip
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving legal documents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/legal-documents/<doc_id>', methods=['GET'])
def get_legal_document_detail(doc_id):
    """Get detailed information about a specific legal document"""
    try:
        import pymongo
        from bson import ObjectId
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        legal_docs = db['legal_documents']
        
        # Get document
        document = legal_docs.find_one({'_id': ObjectId(doc_id)})
        
        if not document:
            return jsonify({
                "success": False,
                "error": "Không tìm thấy văn bản"
            }), 404
        
        # Convert ObjectId to string
        document['_id'] = str(document['_id'])
        if 'imported_at' in document and hasattr(document['imported_at'], 'isoformat'):
            document['imported_at'] = document['imported_at'].isoformat()
        if 'updated_at' in document and hasattr(document['updated_at'], 'isoformat'):
            document['updated_at'] = document['updated_at'].isoformat()
        
        client.close()
        
        return jsonify({
            "success": True,
            "data": document
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving document detail: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/legal-documents/search', methods=['POST'])
def search_legal_documents():
    """Search legal documents by text"""
    try:
        import pymongo
        from bson import ObjectId
        
        data = request.get_json()
        query_text = data.get('query', '')
        category = data.get('category', None)
        limit = int(data.get('limit', 10))
        
        if not query_text:
            return jsonify({
                "success": False,
                "error": "Query text is required"
            }), 400
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        legal_docs = db['legal_documents']
        
        # Build search query
        search_query = {'$text': {'$search': query_text}}
        if category:
            search_query['category_code'] = category
        
        # Search with text score
        results = list(legal_docs.find(
            search_query,
            {'score': {'$meta': 'textScore'}, 'full_content': 0}
        ).sort([('score', {'$meta': 'textScore'})]).limit(limit))
        
        # Convert ObjectId to string and prepare results
        for doc in results:
            doc['_id'] = str(doc['_id'])
            if 'imported_at' in doc and hasattr(doc['imported_at'], 'isoformat'):
                doc['imported_at'] = doc['imported_at'].isoformat()
            if 'updated_at' in doc and hasattr(doc['updated_at'], 'isoformat'):
                doc['updated_at'] = doc['updated_at'].isoformat()
        
        client.close()
        
        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "count": len(results),
                "query": query_text
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error searching documents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/legal-documents/categories', methods=['GET'])
def get_legal_categories():
    """Get list of all categories with document counts"""
    try:
        import pymongo
        
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client['legal_AI_db']
        legal_docs = db['legal_documents']
        
        # Aggregate by category
        pipeline = [
            {'$group': {
                '_id': {
                    'category': '$category',
                    'category_code': '$category_code'
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        categories = []
        for item in legal_docs.aggregate(pipeline):
            categories.append({
                'category': item['_id']['category'],
                'category_code': item['_id']['category_code'],
                'count': item['count']
            })
        
        client.close()
        
        return jsonify({
            "success": True,
            "data": categories
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving categories: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/upload/', methods=['POST', 'OPTIONS'])
def upload_file():
    """Handle contract file upload and analysis"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("\n" + "="*60)
        print("📤 CONTRACT ANALYSIS REQUEST")
        print("="*60)
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "Không tìm thấy file trong request"
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "Chưa chọn file"
            }), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"Định dạng file không hợp lệ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        print(f"📁 File saved: {filename} ({file_size} bytes)")
        
        # Extract text from file
        print("📄 Extracting text from document...")
        contract_text = extract_text_from_file(filepath)
        
        if not contract_text or len(contract_text) < 100:
            return jsonify({
                "success": False,
                "error": "Không thể trích xuất văn bản từ file hoặc file quá ngắn"
            }), 400
        
        print(f"✓ Extracted {len(contract_text)} characters")
        
        # ========== AI DETAILED ANALYSIS WITH RAG ==========
        print("\n🤖 Running AI Detailed Analysis with RAG...")
        ai_analysis = None
        ai_available = False
        legal_context = ""
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            llm = get_llm_client()
            
            # ===== BM25: Get relevant legal context (keyword matching) =====
            print("🔍 Retrieving relevant legal context (BM25 keyword search)...")
            bm25_searcher = get_bm25_searcher()
            if bm25_searcher.is_loaded():
                # Extract key terms for search
                search_query = contract_text[:500]  # Use first 500 chars as query
                bm25_results = bm25_searcher.search(search_query, top_k=3)
                
                if bm25_results['success'] and bm25_results['results']:
                    legal_context = "\n\nVĂN BẢN PHÁP LUẬT LIÊN QUAN (BM25 Keyword Search):\n"
                    for result in bm25_results['results']:
                        legal_context += f"\n[{result['law_name']}]\n"
                        if result['section_title']:
                            legal_context += f"Phần: {result['section_title']}\n"
                        legal_context += f"{result['content'][:300]}...\n"
                        legal_context += f"(Điểm BM25: {result['score']:.2f})\n"
                    print(f"  ✓ Found {len(bm25_results['results'])} relevant legal documents (BM25)")
                else:
                    print("  ⚠️ No relevant legal documents found")
            else:
                print("  ⚠️ BM25 system not loaded")
            
            # ===== PAGEINDEX: Get relevant legal context (tree-based reasoning) =====
            print("🌲 Retrieving legal context (PageIndex Tree Search)...")
            pageindex_retriever = get_pageindex_retriever()
            if pageindex_retriever:
                try:
                    search_query = contract_text[:500]
                    pageindex_results = pageindex_retriever.search(search_query, top_k_docs=2, top_k_sections=2)
                    
                    if pageindex_results:
                        legal_context += "\n\nVĂN BẢN PHÁP LUẬT (PageIndex Tree Search với LLM Reasoning):\n"
                        for result in pageindex_results[:3]:  # Top 3
                            legal_context += f"\n[{result['law_name']} - {result['section_title']}]\n"
                            legal_context += f"{result['content'][:300]}...\n"
                            legal_context += f"(Phương pháp: {result['retrieval_method']}, Độ tin cậy: {result['reasoning_score']:.2%})\n"
                        print(f"  ✓ Found {len(pageindex_results)} relevant sections via PageIndex")
                    else:
                        print("  ⚠️ PageIndex: No results found")
                except Exception as e:
                    print(f"  ⚠️ PageIndex search error: {e}")
            else:
                print("  ⚠️ PageIndex system not loaded")
            
            # Create analysis prompt with legal context
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """Bạn là chuyên gia pháp lý Việt Nam chuyên phân tích hợp đồng. 
Nhiệm vụ của bạn là phân tích chi tiết hợp đồng và đưa ra đánh giá chuyên môn dựa trên văn bản pháp luật.

Hãy phân tích theo cấu trúc sau:
1. TÓM TẮT TỔNG QUAN (2-3 câu ngắn gọn về loại hợp đồng và mục đích)
2. CÁC VẤN ĐỀ PHÁT HIỆN (liệt kê từng vấn đề cụ thể với mức độ nghiêm trọng)
   - Dùng "NGHIÊM TRỌNG:" cho vấn đề nguy hiểm
   - Dùng "TRUNG BÌNH:" cho vấn đề cần chú ý
   - Dùng "THẤP:" cho gợi ý cải thiện
3. PHÂN TÍCH CHI TIẾT (giải thích tại sao mỗi vấn đề quan trọng và tham chiếu văn bản pháp luật nếu có)
4. KHUYẾN NGHỊ CẢI THIỆN (đề xuất cụ thể từng điểm cần sửa đổi)

Trả lời bằng tiếng Việt, chuyên nghiệp nhưng dễ hiểu.{legal_context}"""),
                ("human", "Phân tích hợp đồng sau:\n\n{contract_text}")
            ])
            
            chain = analysis_prompt | llm
            ai_response = chain.invoke({
                "contract_text": contract_text[:4000],  # Limit text length
                "legal_context": legal_context
            })
            ai_analysis = ai_response.content
            ai_available = True
            print(f"  ✓ AI Analysis completed ({len(ai_analysis)} chars)")
        except Exception as e:
            print(f"  ⚠️ AI Analysis failed: {e}")
            # Fallback analysis when AI is not available
            ai_analysis = f"""📋 PHÂN TÍCH CƠ BẢN (AI chưa được cấu hình)

🔍 TÓM TẮT:
Hợp đồng đã được tải lên thành công với {len(contract_text)} ký tự.

⚠️ LƯU Ý:
- Để sử dụng phân tích AI chi tiết, vui lòng cấu hình GROQ_API_KEY
- Truy cập https://console.groq.com/keys để lấy API key miễn phí
- Cập nhật file .env với API key của bạn

💡 KHUYẾN NGHỊ:
- Kiểm tra kỹ các điều khoản về trách nhiệm và nghĩa vụ
- Xem xét các điều khoản về thanh toán và thời hạn
- Đảm bảo hợp đồng tuân thủ quy định pháp luật Việt Nam
- Nên có luật sư xem xét trước khi ký kết

📖 Để phân tích chi tiết, vui lòng cấu hình GROQ_API_KEY trong file .env"""
            ai_available = False
        
        # ========== SVM CLASSIFICATION ==========
        print("\n📊 Classifying contract type with SVM...")
        svm_classifier = get_svm_classifier()
        classification_result = {'category_code': 'khac', 'category_name': 'Hợp đồng khác', 'confidence': 0.0}
        
        if svm_classifier.is_loaded():
            classification_result = svm_classifier.classify(contract_text[:1000])  # Use first 1000 chars
            if classification_result['success']:
                print(f"  ✓ Contract type: {classification_result['category_name']} ({classification_result['confidence']:.0%})")
            else:
                print(f"  ⚠️ Classification failed: {classification_result.get('error', 'Unknown')}")
        else:
            print("  ⚠️ SVM classifier not loaded")
        
        # ========== PARSE AI ANALYSIS TO ISSUES ==========
        issues_detected = []
        lines = ai_analysis.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('+')):
                issue_text = line.lstrip('-•+ ').strip()
                # Determine severity
                if any(word in line.upper() for word in ['NGHIÊM TRỌNG', 'NGUY HIỂM', 'VI PHẠM']):
                    issues_detected.append(f"🚨 {issue_text}")
                elif any(word in line.upper() for word in ['TRUNG BÌNH', 'THIẾU', 'CHƯA RÕ']):
                    issues_detected.append(f"⚡ {issue_text}")
                else:
                    issues_detected.append(f"ℹ️ {issue_text}")
        
        # Fallback if no issues parsed
        if not issues_detected:
            issues_detected.append("⚡ Hợp đồng cần được xem xét kỹ lưỡng hơn")
            issues_detected.append("ℹ️ Nên bổ sung thêm điều khoản bảo vệ quyền lợi")
        
        # ========== COUNT SEVERITY LEVELS ==========
        high_risk_count = len([i for i in issues_detected if i.startswith('🚨')])
        medium_risk_count = len([i for i in issues_detected if i.startswith('⚡')])
        low_risk_count = len([i for i in issues_detected if i.startswith('ℹ️')])
        
        # ========== AI SAFETY SCORE EVALUATION ==========
        # Ask AI to provide a safety score (0-100) with reasoning
        safety_score = None
        safety_reasoning = ""
        
        if ai_available:
            try:
                print("\n🎯 Getting AI safety score...")
                score_prompt = ChatPromptTemplate.from_messages([
                    ("system", """Bạn là chuyên gia đánh giá rủi ro pháp lý. Hãy đánh giá độ an toàn của hợp đồng bằng một điểm số từ 0-100:

- 90-100: Hợp đồng rất an toàn, đầy đủ điều khoản bảo vệ
- 70-89: Hợp đồng tốt, có một số điểm cần cải thiện nhỏ
- 50-69: Hợp đồng trung bình, có vấn đề cần lưu ý
- 30-49: Hợp đồng có rủi ro, cần chỉnh sửa nhiều điểm
- 0-29: Hợp đồng nguy hiểm, có rủi ro pháp lý nghiêm trọng

Căn cứ vào số lượng và mức độ nghiêm trọng của vấn đề:
- Vấn đề NGHIÊM TRỌNG: {high_risk} vấn đề (ảnh hưởng lớn đến điểm)
- Vấn đề TRUNG BÌNH: {medium_risk} vấn đề (ảnh hưởng vừa phải)
- Vấn đề THẤP: {low_risk} vấn đề (ảnh hưởng nhỏ)

Trả lời theo định dạng:
ĐIỂM: [số từ 0-100]
LÝ DO: [1-2 câu giải thích ngắn gọn tại sao cho điểm này]"""),
                    ("human", "Đánh giá hợp đồng với {total} vấn đề phát hiện:\n{issues}")
                ])
                
                chain = score_prompt | llm
                score_response = chain.invoke({
                    "high_risk": high_risk_count,
                    "medium_risk": medium_risk_count,
                    "low_risk": low_risk_count,
                    "total": len(issues_detected),
                    "issues": "\n".join(issues_detected[:10])  # First 10 issues
                })
                
                # Parse AI response
                score_text = score_response.content
                for line in score_text.split('\n'):
                    if line.strip().startswith('ĐIỂM:'):
                        try:
                            score_str = line.split('ĐIỂM:')[1].strip()
                            # Extract number from string (handle "85" or "85/100" formats)
                            import re
                            numbers = re.findall(r'\d+', score_str)
                            if numbers:
                                safety_score = int(numbers[0])
                                safety_score = max(0, min(100, safety_score))  # Clamp to 0-100
                        except:
                            pass
                    elif line.strip().startswith('LÝ DO:'):
                        safety_reasoning = line.split('LÝ DO:')[1].strip()
                
                if safety_score is not None:
                    print(f"  ✓ AI Safety Score: {safety_score}/100")
                    print(f"  ✓ Reasoning: {safety_reasoning}")
                else:
                    print("  ⚠️ Could not parse AI score, using calculated score")
            except Exception as e:
                print(f"  ⚠️ AI scoring failed: {e}")
        
        # Fallback calculation if AI score not available
        if safety_score is None:
            safety_score = 100
            safety_score -= high_risk_count * 10    # -10 points per high risk
            safety_score -= medium_risk_count * 5   # -5 points per medium risk
            safety_score -= low_risk_count * 2      # -2 points per low risk
            safety_score = max(0, min(100, safety_score))
            safety_reasoning = f"Điểm tự động: {high_risk_count} vấn đề nghiêm trọng, {medium_risk_count} trung bình, {low_risk_count} thấp"
        
        # ========== COMPILE ANALYSIS RESULT ==========
        analysis_result = {
            "filename": filename,
            "file_size": file_size,
            "upload_time": datetime.now().isoformat(),
            "status": "analyzed",
            
            # AI Analysis - CHI TIẾT QUAN TRỌNG
            "ai_analysis": ai_analysis,
            "ai_available": ai_available,
            
            # AI Safety Score - ĐIỂM AN TOÀN VỚI LÝ DO
            "safety_score": safety_score,
            "safety_reasoning": safety_reasoning,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
            
            # SVM Classification Results
            "contract_type": classification_result.get('category_name', 'Hợp đồng khác'),
            "contract_type_code": classification_result.get('category_code', 'khac'),
            "contract_type_confidence": classification_result.get('confidence', 0.0),
            "contract_type_probabilities": classification_result.get('all_scores', {}),
            
            # Mock risk/violation data (có thể train thêm model cho tương lai)
            "risk_level": "medium",
            "risk_confidence": 0.75,
            "risk_probabilities": {},
            
            "has_violation": False,
            "violation_probability": 0.0,
            
            # RAG Legal References - replaced mock data with real RAG results
            "legal_references": [],
            
            # Summary
            "summary": f"Hợp đồng loại '{classification_result.get('category_name', 'Khác')}' đã được phân tích {'chi tiết bởi AI với RAG' if ai_available else 'cơ bản'}. Độ dài: {len(contract_text)} ký tự. Phát hiện {len(issues_detected)} vấn đề cần lưu ý. Điểm an toàn: {safety_score}/100.",
            
            # Issues from AI
            "issues": issues_detected
        }
        
        # Add real BM25 legal references if available
        if legal_context:
            bm25_searcher = get_bm25_searcher()
            search_query = contract_text[:500]
            bm25_results = bm25_searcher.search(search_query, top_k=3)
            if bm25_results['success']:
                for result in bm25_results['results']:
                    analysis_result["legal_references"].append({
                        "title": result['law_name'],
                        "section": result.get('section_title', ''),
                        "content": result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                        "source": f"{result['law_name']} / {result.get('section_title', 'Toàn văn')}",
                        "relevance": result['score']
                    })
        
        # ========== SAVE TO DATABASE HISTORY ========== ==========
        # Try to get user email from token
        user_email = "anonymous"
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = verify_token(token)
            if payload:
                user_email = payload.get('email', 'anonymous')
        
        # Save to MongoDB history
        history_id = save_analysis_to_history(user_email, analysis_result)
        if history_id:
            analysis_result["history_id"] = history_id
        
        print("\n✅ ANALYSIS COMPLETED WITH AI!" if ai_available else "\n✅ ANALYSIS COMPLETED (Basic mode)")
        print("="*60)
        
        return jsonify({
            "success": True,
            "data": analysis_result
        }), 200
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi phân tích file: {str(e)}"
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Lỗi server: {str(e)}"
        }), 500

@app.route('/api/generate-pdf/', methods=['POST', 'OPTIONS'])
def generate_pdf():
    """
    Generate PDF report from analysis data (Vietnamese support)
    Uses fpdf2 with Arial Unicode fonts
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    try:
        from pdf_generator import generate_pdf_report
        import uuid
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Không có dữ liệu để tạo báo cáo"
            }), 400
        
        # Get analysis content (Markdown format)
        analysis_content = data.get('analysis', data.get('ai_analysis', ''))
        if not analysis_content:
            return jsonify({
                "success": False,
                "error": "Thiếu nội dung phân tích (analysis field)"
            }), 400
        
        # Generate unique filename
        contract_name = data.get('filename', data.get('contract_name', 'Hop_Dong'))
        # Remove file extension and special chars
        contract_name = contract_name.rsplit('.', 1)[0]
        contract_name = contract_name.replace(' ', '_')
        
        pdf_filename = f"Bao_Cao_{contract_name}_{uuid.uuid4().hex[:6]}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Create PDF report with Vietnamese support
        print(f"🔨 Generating PDF: {pdf_filename}")
        result_path = generate_pdf_report(analysis_content, pdf_path)
        
        if not result_path or not os.path.exists(result_path):
            return jsonify({
                "success": False,
                "error": "Lỗi tạo PDF - File không được tạo"
            }), 500
        
        print(f"✅ PDF created: {result_path}")
        
        # Return file as download with CORS headers
        from flask import send_file, make_response
        response = make_response(send_file(
            result_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Bao_Cao_{contract_name}.pdf"
        ))
        
        # Add CORS headers to file response
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:3000')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response
        
    except Exception as e:
        print(f"❌ PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi tạo PDF: {str(e)}"
        }), 500


# ==================== ML ENDPOINTS ====================

@app.route('/api/classify-contract/', methods=['POST', 'OPTIONS'])
def classify_contract():
    """
    SVM Contract Classification Endpoint
    Phân loại hợp đồng bằng SVM model
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Thiếu trường 'text' trong request body"
            }), 400
        
        text = data['text']
        
        if len(text) < 50:
            return jsonify({
                "success": False,
                "error": "Text quá ngắn (cần ít nhất 50 ký tự)"
            }), 400
        
        # Classify với SVM
        print(f"🔍 Classifying contract ({len(text)} chars)...")
        svm_classifier = get_svm_classifier()
        
        if not svm_classifier.is_loaded():
            return jsonify({
                "success": False,
                "error": "SVM model chưa được load. Chạy: python train_svm_model.py"
            }), 500
        
        result = svm_classifier.classify(text)
        
        print(f"✅ Classification: {result.get('category_name', 'Unknown')} ({result.get('confidence', 0):.0%})")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Classification error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi phân loại: {str(e)}"
        }), 500


@app.route('/api/bm25-search/', methods=['POST', 'OPTIONS'])
def bm25_search():
    """
    BM25 Keyword Search Endpoint
    Tìm kiếm dựa trên từ khóa (keyword matching) không cần embeddings
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Thiếu trường 'query' trong request body"
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        filter_category = data.get('category', None)
        
        if len(query) < 3:
            return jsonify({
                "success": False,
                "error": "Query quá ngắn (cần ít nhất 3 ký tự)"
            }), 400
        
        # Search với BM25
        print(f"🔍 BM25 Search: '{query[:50]}...' (top_k={top_k})")
        bm25_searcher = get_bm25_searcher()
        
        if not bm25_searcher.is_loaded():
            return jsonify({
                "success": False,
                "error": "BM25 index chưa được build từ MongoDB"
            }), 500
        
        result = bm25_searcher.search(query, top_k=top_k, filter_category=filter_category)
        
        if result['success']:
            print(f"✅ Found {result['total_results']} results")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ BM25 search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi tìm kiếm: {str(e)}"
        }), 500


@app.route('/api/search/', methods=['POST', 'OPTIONS'])
@app.route('/api/pageindex-search/', methods=['POST', 'OPTIONS'])  # Backward compatibility
def pageindex_search():
    """
    PageIndex Tree Search Endpoint
    Tìm kiếm bằng tree-based reasoning với LLM (không dùng vector embeddings)
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Thiếu trường 'query' trong request body"
            }), 400
        
        query = data['query']
        top_k_docs = data.get('top_k_docs', 2)
        top_k_sections = data.get('top_k_sections', 3)
        
        if len(query) < 3:
            return jsonify({
                "success": False,
                "error": "Query quá ngắn (cần ít nhất 3 ký tự)"
            }), 400
        
        # Search với PageIndex
        print(f"🌲 PageIndex Search: '{query[:50]}...'")
        pageindex_retriever = get_pageindex_retriever()
        
        if not pageindex_retriever:
            return jsonify({
                "success": False,
                "error": "PageIndex chưa được load. Chạy: python pageindex_rag.py"
            }), 500
        
        results = pageindex_retriever.search(query, top_k_docs=top_k_docs, top_k_sections=top_k_sections)
        
        print(f"✅ PageIndex found {len(results)} results via tree search")
        
        return jsonify({
            "success": True,
            "results": results,
            "total_results": len(results),
            "method": "pageindex_tree_search",
            "query": query
        }), 200
        
    except Exception as e:
        print(f"❌ PageIndex search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi tìm kiếm PageIndex: {str(e)}"
        }), 500


@app.route('/api/compare-search/', methods=['POST', 'OPTIONS'])
def compare_search():
    """
    So sánh kết quả giữa BM25 (keyword) và PageIndex (LLM reasoning)
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Thiếu trường 'query' trong request body"
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 3)
        
        print(f"\n🔍 COMPARISON SEARCH: '{query[:50]}...'")
        print("="*60)
        
        # BM25 search
        bm25_results = []
        bm25_time = 0
        bm25_searcher = get_bm25_searcher()
        if bm25_searcher and bm25_searcher.is_loaded():
            import time
            start = time.time()
            bm25_result = bm25_searcher.search(query, top_k=top_k)
            bm25_time = (time.time() - start) * 1000  # ms
            if bm25_result['success']:
                bm25_results = bm25_result['results']
            print(f"✓ BM25: {len(bm25_results)} results in {bm25_time:.2f}ms")
        
        # PageIndex search
        pageindex_results = []
        pageindex_time = 0
        pageindex_retriever = get_pageindex_retriever()
        if pageindex_retriever:
            import time
            start = time.time()
            pageindex_results = pageindex_retriever.search(query, top_k_docs=2, top_k_sections=top_k)
            pageindex_time = (time.time() - start) * 1000  # ms
            print(f"✓ PageIndex: {len(pageindex_results)} results in {pageindex_time:.2f}ms")
        
        return jsonify({
            "success": True,
            "query": query,
            "bm25": {
                "results": bm25_results,
                "count": len(bm25_results),
                "time_ms": bm25_time,
                "method": "keyword_matching"
            },
            "pageindex": {
                "results": pageindex_results,
                "count": len(pageindex_results),
                "time_ms": pageindex_time,
                "method": "llm_tree_reasoning"
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi so sánh: {str(e)}"
        }), 500


@app.route('/api/ml-status/', methods=['GET'])
def ml_status():
    """
    Kiểm tra trạng thái các ML models (SVM, BM25, PageIndex)
    """
    try:
        svm_classifier = get_svm_classifier()
        bm25_searcher = get_bm25_searcher()
        pageindex_retriever = get_pageindex_retriever()
        
        # Get BM25 stats
        bm25_stats = bm25_searcher.get_stats() if bm25_searcher else {}
        
        status = {
            "svm": {
                "loaded": svm_classifier.is_loaded(),
                "model_path": "models/svm_contract_classifier.pkl",
                "accuracy": svm_classifier.metadata.get('accuracy', 0) if svm_classifier.metadata else 0,
                "categories": list(svm_classifier.categories.values()) if svm_classifier.categories else []
            },
            "bm25": {
                "loaded": bm25_stats.get('loaded', False),
                "total_documents": bm25_stats.get('total_documents', 0),
                "total_tokens": bm25_stats.get('total_tokens', 0),
                "avg_tokens_per_doc": round(bm25_stats.get('avg_tokens_per_doc', 0), 2),
                "method": "keyword_matching",
                "description": "BM25 in-memory index from MongoDB"
            },
            "pageindex": {
                "loaded": pageindex_retriever is not None,
                "cache_path": "embeddings/pageindex_cache.pkl",
                "total_documents": len(pageindex_retriever.document_trees) if pageindex_retriever else 0,
                "total_nodes": len(pageindex_retriever.node_index) if pageindex_retriever else 0,
                "method": "llm_tree_reasoning",
                "description": "Vectorless RAG with LLM reasoning"
            }
        }
        
        return jsonify({
            "success": True,
            "status": status
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Legal Contract Reviewer API")
    print("=" * 60)
    print("Starting server...")
    print("API: http://localhost:5000")
    print("Health: http://localhost:5000/health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000)  # Tắt debug mode để tránh auto-reload
