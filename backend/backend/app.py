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
from vnpay_utils import create_payment_url, verify_return_signature
from src.resource_config import (
    MAX_FILE_SIZE, ALLOWED_EXTENSIONS, UPLOAD_FOLDER,
    AUTO_CLEANUP_UPLOADS, CLEANUP_AFTER_HOURS, SESSION_LIFETIME,
    ENABLE_RATE_LIMIT, RATE_LIMIT_PER_MINUTE
)

# MongoDB Connection
import pymongo
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE', '')
VNPAY_HASH_SECRET = os.getenv('VNPAY_HASH_SECRET', '')
VNPAY_PAYMENT_URL = os.getenv('VNPAY_PAYMENT_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
VNPAY_RETURN_URL = os.getenv('VNPAY_RETURN_URL', 'http://localhost:5000/api/payments/vnpay/return')
VNPAY_IPN_URL = os.getenv('VNPAY_IPN_URL', 'http://localhost:5000/api/payments/vnpay/ipn')
FRONTEND_RETURN_URL = os.getenv('FRONTEND_RETURN_URL', 'http://localhost:5173/payment/return')

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
    payments_collection = mongo_db['payments']

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
    payments_collection = None

if MONGODB_CONNECTED:
    try:
        # Email luôn phải unique
        users_collection.create_index('email', unique=True)

        # Nếu có index username_1 cũ (unique trên null), loại bỏ để tránh duplicate key với dữ liệu legacy
        existing_indexes = users_collection.index_information()
        if 'username_1' in existing_indexes:
            users_collection.drop_index('username_1')

        # Username dùng index tra cứu không-unique để tương thích dữ liệu cũ và tránh startup warning
        users_collection.create_index(
            [('username', pymongo.ASCENDING)],
            name='username_lookup',
            unique=False,
        )

        analysis_collection.create_index([('user', 1), ('timestamp', -1)])
        payments_collection.create_index('txn_ref', unique=True)
        print("✅ MongoDB indexes ensured")
    except PyMongoError as e:
        # Không hạ toàn bộ hệ thống xuống in-memory chỉ vì lỗi index
        print(f"⚠️ MongoDB index warning: {e}")
        print("⚠️ Continue without forcing in-memory fallback")

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS

# Enable CORS for frontend - More permissive config
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "x-csrftoken", "X-CSRFToken"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])

# Additional CORS headers for all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://localhost:5173']:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, x-csrftoken, X-CSRFToken'
    return response

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


def get_client_ip():
    """Get client ip with proxy support for VNPay vnp_IpAddr."""
    ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    if ip:
        return ip
    return request.remote_addr or '127.0.0.1'


def get_plan_price(plan, billing_cycle='monthly'):
    prices = {
        'pro': {'monthly': 299000, 'yearly': 2990000},
        'enterprise': {'monthly': 999000, 'yearly': 9990000},
    }
    plan_prices = prices.get(plan)
    if not plan_prices:
        return 0
    return plan_prices.get(billing_cycle, plan_prices['monthly'])


def serialize_payment(doc):
    """Convert payment document to JSON-safe payload for frontend."""
    return {
        'txn_ref': doc.get('txn_ref', ''),
        'plan': doc.get('plan', ''),
        'billing_cycle': doc.get('billing_cycle', 'monthly'),
        'amount': doc.get('amount', 0),
        'status': doc.get('status', 'pending'),
        'provider': doc.get('provider', 'vnpay'),
        'created_at': doc.get('created_at').isoformat() if isinstance(doc.get('created_at'), datetime) else doc.get('created_at'),
        'updated_at': doc.get('updated_at').isoformat() if isinstance(doc.get('updated_at'), datetime) else doc.get('updated_at'),
        'vnp_response_code': doc.get('vnp_response_code'),
        'vnp_transaction_no': doc.get('vnp_transaction_no'),
    }


def update_vnpay_payment(txn_ref, params, is_success):
    """Persist VNPay return/IPN response and update subscription on success."""
    payment_doc = None
    if MONGODB_CONNECTED and payments_collection is not None and txn_ref:
        payment_doc = payments_collection.find_one({'txn_ref': txn_ref})

    if MONGODB_CONNECTED and payments_collection is not None and txn_ref:
        payments_collection.update_one(
            {'txn_ref': txn_ref},
            {
                '$set': {
                    'status': 'success' if is_success else 'failed',
                    'updated_at': datetime.now(),
                    'vnp_response_code': params.get('vnp_ResponseCode'),
                    'vnp_transaction_status': params.get('vnp_TransactionStatus'),
                    'vnp_transaction_no': params.get('vnp_TransactionNo'),
                    'vnp_bank_code': params.get('vnp_BankCode'),
                    'vnp_pay_date': params.get('vnp_PayDate'),
                    'signature_valid': True,
                }
            }
        )

    if is_success and payment_doc and MONGODB_CONNECTED and users_collection is not None:
        users_collection.update_one(
            {'email': payment_doc['user_email']},
            {
                '$set': {
                    'subscription_tier': payment_doc.get('plan', 'pro'),
                    'updated_at': datetime.now(),
                }
            }
        )

    return payment_doc

@app.route('/')
def index():
    """Trang chu"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """API đăng nhập với MongoDB"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
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
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
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


@app.route('/api/profile', methods=['GET'])
@app.route('/api/profile/', methods=['GET'])
def get_profile():
    """Get current user profile for web frontend."""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401

    if not MONGODB_CONNECTED or users_collection is None:
        return jsonify({'success': False, 'error': 'Database không khả dụng'}), 503

    user = users_collection.find_one({'email': session['user_email']})
    if not user:
        return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404

    profile = {
        'full_name': user.get('full_name', ''),
        'email': user.get('email', ''),
        'phone': user.get('phone', ''),
        'avatar': user.get('avatar', ''),
        'subscription_tier': user.get('subscription_tier', 'free'),
        'is_admin': bool(user.get('is_admin', False)),
    }
    return jsonify({'success': True, 'profile': profile}), 200


@app.route('/api/profile', methods=['PUT'])
@app.route('/api/profile/', methods=['PUT'])
def update_profile():
    """Update current user profile fields."""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401

    if not MONGODB_CONNECTED or users_collection is None:
        return jsonify({'success': False, 'error': 'Database không khả dụng'}), 503

    data = request.json or {}
    updates = {}

    if 'full_name' in data:
        updates['full_name'] = (data.get('full_name') or '').strip()
    if 'phone' in data:
        updates['phone'] = (data.get('phone') or '').strip()

    if not updates:
        return jsonify({'success': False, 'error': 'Không có dữ liệu để cập nhật'}), 400

    updates['updated_at'] = datetime.now()
    users_collection.update_one(
        {'email': session['user_email']},
        {'$set': updates},
    )

    return jsonify({'success': True, 'message': 'Cập nhật hồ sơ thành công'}), 200


@app.route('/api/google-login', methods=['POST', 'OPTIONS'])
def google_login():
    """Đăng nhập bằng Google ID token cho web frontend."""
    if request.method == 'OPTIONS':
        return '', 200

    if not MONGODB_CONNECTED or users_collection is None:
        return jsonify({'success': False, 'error': 'Database không khả dụng'}), 503

    data = request.json or {}
    credential = data.get('credential')
    if not credential:
        return jsonify({'success': False, 'error': 'Thiếu credential từ Google'}), 400

    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
    except Exception:
        return jsonify({'success': False, 'error': 'Thiếu package google-auth trên server'}), 500

    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    try:
        payload = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            google_client_id if google_client_id else None,
        )
    except Exception:
        return jsonify({'success': False, 'error': 'Google token không hợp lệ'}), 401

    issuer = payload.get('iss')
    if issuer not in ('accounts.google.com', 'https://accounts.google.com'):
        return jsonify({'success': False, 'error': 'Nguồn token không hợp lệ'}), 401

    email = payload.get('email', '').strip().lower()
    full_name = payload.get('name', '').strip()
    email_verified = payload.get('email_verified', False)

    if not email or not email_verified:
        return jsonify({'success': False, 'error': 'Email Google chưa xác thực'}), 401

    try:
        user = users_collection.find_one({'email': email})

        if not user:
            base_username = email.split('@')[0] or 'google_user'
            username = base_username
            suffix = 1
            while users_collection.find_one({'username': username}):
                username = f"{base_username}_{suffix}"
                suffix += 1

            user_doc = {
                'username': username,
                'email': email,
                'password': generate_password_hash(secrets.token_hex(16)),
                'full_name': full_name or username,
                'auth_provider': 'google',
                'is_admin': False,
                'is_active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            insert_result = users_collection.insert_one(user_doc)
            user_id = str(insert_result.inserted_id)
        else:
            updates = {
                'auth_provider': 'google',
                'updated_at': datetime.now(),
            }
            if full_name and not user.get('full_name'):
                updates['full_name'] = full_name
            users_collection.update_one({'_id': user['_id']}, {'$set': updates})
            user_id = str(user['_id'])

        session['user_id'] = user_id
        session['user_email'] = email
        session['is_admin'] = False
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Đăng nhập Google thành công',
            'user': {
                'email': email,
                'full_name': full_name,
                'is_admin': False,
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Lỗi server: {str(e)}'}), 500


@app.route('/api/payments/vnpay/create', methods=['POST'])
def create_vnpay_payment():
    """Create VNPay payment URL and persist pending transaction."""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    # Bắt buộc MongoDB khả dụng để luôn lưu được dữ liệu thanh toán
    if not (MONGODB_CONNECTED and payments_collection is not None):
        return jsonify({
            'success': False,
            'error': 'Database không khả dụng, chưa thể tạo giao dịch thanh toán'
        }), 503

    payload = request.json or {}
    plan = payload.get('plan', 'pro')
    billing_cycle = payload.get('billing_cycle', 'monthly')
    amount = payload.get('amount')
    frontend_return_url = payload.get('return_url', FRONTEND_RETURN_URL)

    now = datetime.now()
    txn_ref = f"{int(now.timestamp())}{secrets.randbelow(100000):05d}"

    try:
        amount = int(amount) if amount is not None else get_plan_price(plan, billing_cycle)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Số tiền không hợp lệ'}), 400

    if amount <= 0:
        return jsonify({'success': False, 'error': 'Số tiền thanh toán phải lớn hơn 0'}), 400

    if not all([VNPAY_TMN_CODE, VNPAY_HASH_SECRET]):
        failed_doc = {
            'txn_ref': txn_ref,
            'user_email': session['user_email'],
            'plan': plan,
            'billing_cycle': billing_cycle,
            'amount': amount,
            'status': 'failed',
            'provider': 'vnpay',
            'failure_reason': 'missing_vnpay_config',
            'failure_message': 'Thiếu VNPAY_TMN_CODE hoặc VNPAY_HASH_SECRET',
            'return_url': frontend_return_url,
            'vnpay_return_url': VNPAY_RETURN_URL,
            'created_ip': get_client_ip(),
            'created_at': now,
            'updated_at': now,
        }
        try:
            payments_collection.insert_one(failed_doc)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Lỗi lưu giao dịch: {str(e)}'}), 500

        return jsonify({
            'success': False,
            'txn_ref': txn_ref,
            'error': 'Chưa cấu hình VNPAY_TMN_CODE hoặc VNPAY_HASH_SECRET'
        }), 500

    order_info = f"GOI_{str(plan).upper()}_{str(billing_cycle).upper()}_{txn_ref}"

    vnp_params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': VNPAY_TMN_CODE,
        'vnp_Amount': str(amount * 100),
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': txn_ref,
        'vnp_OrderInfo': order_info,
        'vnp_OrderType': 'billpayment',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': VNPAY_RETURN_URL,
        'vnp_IpAddr': get_client_ip(),
        'vnp_CreateDate': now.strftime('%Y%m%d%H%M%S'),
    }

    payment_url, _ = create_payment_url(VNPAY_PAYMENT_URL, vnp_params, VNPAY_HASH_SECRET)

    payment_doc = {
        'txn_ref': txn_ref,
        'user_email': session['user_email'],
        'plan': plan,
        'billing_cycle': billing_cycle,
        'amount': amount,
        'status': 'pending',
        'provider': 'vnpay',
        'payment_url': payment_url,
        'return_url': frontend_return_url,
        'vnpay_return_url': VNPAY_RETURN_URL,
        'created_ip': get_client_ip(),
        'created_at': now,
        'updated_at': now,
    }

    try:
        payments_collection.insert_one(payment_doc)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Lỗi lưu giao dịch: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'method': 'vnpay',
        'payment_url': payment_url,
        'txn_ref': txn_ref,
    })


@app.route('/api/payments/vnpay/return', methods=['GET'])
def vnpay_return():
    """VNPay callback endpoint: verify signature, update payment and user plan, then redirect frontend."""
    params = dict(request.args)
    is_valid_signature = verify_return_signature(params, VNPAY_HASH_SECRET)

    txn_ref = params.get('vnp_TxnRef', '')
    response_code = params.get('vnp_ResponseCode', '')
    transaction_status = params.get('vnp_TransactionStatus', '')
    is_success = is_valid_signature and response_code == '00' and transaction_status == '00'

    payment_doc = update_vnpay_payment(txn_ref, params, is_success)

    redirect_url = (
        f"{FRONTEND_RETURN_URL}"
        f"?status={'success' if is_success else 'failed'}"
        f"&txn_ref={txn_ref}"
        f"&code={response_code}"
    )
    if payment_doc and payment_doc.get('plan'):
        redirect_url += f"&plan={payment_doc.get('plan')}"

    return redirect(redirect_url)


@app.route('/api/payments/vnpay/ipn', methods=['GET', 'POST'])
def vnpay_ipn():
    """VNPay IPN endpoint for server-to-server payment confirmation."""
    params = dict(request.values)
    is_valid_signature = verify_return_signature(params, VNPAY_HASH_SECRET)

    txn_ref = params.get('vnp_TxnRef', '')
    response_code = params.get('vnp_ResponseCode', '')
    transaction_status = params.get('vnp_TransactionStatus', '')

    if not is_valid_signature:
        return jsonify({'RspCode': '97', 'Message': 'Invalid signature'}), 200

    payment_doc = None
    if MONGODB_CONNECTED and payments_collection is not None and txn_ref:
        payment_doc = payments_collection.find_one({'txn_ref': txn_ref})

    if not payment_doc:
        return jsonify({'RspCode': '01', 'Message': 'Order not found'}), 200

    if payment_doc.get('status') == 'success':
        return jsonify({'RspCode': '02', 'Message': 'Order already confirmed'}), 200

    is_success = response_code == '00' and transaction_status == '00'
    update_vnpay_payment(txn_ref, params, is_success)

    return jsonify({'RspCode': '00', 'Message': 'Confirm Success'}), 200


@app.route('/api/payments/history', methods=['GET'])
def payments_history():
    """Get current user's payment transactions."""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    if not (MONGODB_CONNECTED and payments_collection is not None):
        return jsonify({'success': True, 'payments': []})

    try:
        cursor = payments_collection.find(
            {'user_email': session['user_email']}
        ).sort('created_at', -1).limit(30)
        payments = [serialize_payment(doc) for doc in cursor]
        return jsonify({'success': True, 'payments': payments})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Không thể tải lịch sử thanh toán: {str(e)}'}), 500


@app.route('/api/payments/status/<txn_ref>', methods=['GET'])
def payment_status(txn_ref):
    """Get status of a transaction for current user."""
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    if not txn_ref:
        return jsonify({'success': False, 'error': 'Thiếu mã giao dịch'}), 400

    if not (MONGODB_CONNECTED and payments_collection is not None):
        return jsonify({'success': False, 'error': 'Database không khả dụng'}), 503

    payment = payments_collection.find_one({'txn_ref': txn_ref})
    if not payment:
        return jsonify({'success': False, 'error': 'Không tìm thấy giao dịch'}), 404

    if payment.get('user_email') != session['user_email']:
        return jsonify({'success': False, 'error': 'Không có quyền xem giao dịch này'}), 403

    return jsonify({'success': True, 'payment': serialize_payment(payment)})

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
            
            # Extract SVM results for structured data
            svm_results = result.get('svm_results', {})
            contract_type = svm_results.get('contract_type', {}).get('predicted_type', 'Không xác định')
            risk_level = svm_results.get('risk_assessment', {}).get('predicted_risk', 'medium')
            has_violation = svm_results.get('violation_check', {}).get('has_violation', False)
            
            # Extract issues from final report
            final_report = result.get('final_report', 'Không có kết quả phân tích')
            issues = []
            if '🚨' in final_report or '⚡' in final_report or 'ℹ️' in final_report:
                # Parse issues from report
                lines = final_report.split('\n')
                for line in lines:
                    if any(emoji in line for emoji in ['🚨', '⚡', 'ℹ️']):
                        issues.append(line.strip())
            
            # Create summary from first part of report
            summary_lines = final_report.split('\n')[:3]
            summary = '\n'.join(summary_lines) if summary_lines else 'Đã phân tích hợp đồng thành công'
            
            # Parse kết quả - FRONTEND FORMAT
            analysis_data = {
                'filename': filename,
                'upload_time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'contract_type': contract_type,
                'risk_level': risk_level,
                'has_violation': has_violation,
                'summary': summary,
                'ai_analysis': final_report,
                'issues': issues,
                'extractedClauses': result.get('extracted_clauses', [])[:10],
                'researchResults': result.get('research_results', [])[:5],
                'legal_references': []  # Can be populated from research_results if needed
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

    if MONGODB_CONNECTED and users_collection is not None and analysis_collection is not None:
        total_users = users_collection.count_documents({})
        total_analyses = analysis_collection.count_documents({})
        active_users = len(analysis_collection.distinct('user'))
    else:
        total_users = 0
        total_analyses = len(ANALYSIS_HISTORY)
        active_users = len(set(h['user'] for h in ANALYSIS_HISTORY))

    stats = {
        'totalUsers': total_users,
        'totalAnalyses': total_analyses,
        'activeUsers': active_users,
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
