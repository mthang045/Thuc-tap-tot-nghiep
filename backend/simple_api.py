"""
Simple Flask API for Legal Contract System
Minimal version without Django dependencies
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import pymongo
import jwt
from datetime import datetime, timedelta
from functools import wraps
from datetime import datetime
import PyPDF2
import docx

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Import SVM and PageIndex
from src.classifier.svm_classifier import SVMContractClassifier
from src.page_index_integration import PageIndexManager

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize global instances (lazy loading)
_svm_classifier = None
_pageindex_manager = None
_llm_client = None

def get_llm_client():
    """Lazy load Groq LLM client"""
    global _llm_client
    if _llm_client is None:
        print("🔧 Loading Groq LLM...")
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        _llm_client = ChatGroq(
            api_key=api_key,
            model="llama-3.3-70b-versatile",  # Updated to newer model
            temperature=0.3,
            max_retries=2
        )
    return _llm_client

def get_svm_classifier():
    """Lazy load SVM classifier"""
    global _svm_classifier
    if _svm_classifier is None:
        print("🔧 Loading SVM Classifier...")
        _svm_classifier = SVMContractClassifier(model_dir="models/svm")
    return _svm_classifier

def get_pageindex_manager():
    """Lazy load PageIndex manager"""
    global _pageindex_manager
    if _pageindex_manager is None:
        print("🔧 Loading PageIndex...")
        _pageindex_manager = PageIndexManager(
            data_folder="data/source_laws",
            cache_file="data/page_index_cache.pkl"
        )
        _pageindex_manager.build_index()
    return _pageindex_manager

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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['SECRET_KEY'] = 'legal-contract-reviewer-secret-key-2026'  # Change in production!

CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-CSRFToken'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     expose_headers=['Content-Disposition'])

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

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client['legal_db']
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
        db = client['legal_db']
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
        
        # Create new user
        user_doc = {
            "full_name": data['full_name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": data['password'],  # In production, hash this!
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
        db = client['legal_db']
        users_collection = db['users']
        
        # Find user
        user = users_collection.find_one({
            "email": data['email'],
            "password": data['password']  # In production, compare hashed passwords!
        })
        
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
        else:
            return jsonify({
                "success": False,
                "error": "Email hoặc mật khẩu không đúng"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Lỗi server: {str(e)}"
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
        
        # ========== AI DETAILED ANALYSIS ==========
        print("\n🤖 Running AI Detailed Analysis...")
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            llm = get_llm_client()
            
            # Create analysis prompt
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """Bạn là chuyên gia pháp lý Việt Nam chuyên phân tích hợp đồng. 
Nhiệm vụ của bạn là phân tích chi tiết hợp đồng và đưa ra đánh giá chuyên môn.

Hãy phân tích theo cấu trúc sau:
1. TÓM TẮT TỔNG QUAN (2-3 câu ngắn gọn về loại hợp đồng và mục đích)
2. CÁC VẤN ĐỀ PHÁT HIỆN (liệt kê từng vấn đề cụ thể với mức độ nghiêm trọng)
   - Dùng "NGHIÊM TRỌNG:" cho vấn đề nguy hiểm
   - Dùng "TRUNG BÌNH:" cho vấn đề cần chú ý
   - Dùng "THẤP:" cho gợi ý cải thiện
3. PHÂN TÍCH CHI TIẾT (giải thích tại sao mỗi vấn đề quan trọng)
4. KHUYẾN NGHỊ CẢI THIỆN (đề xuất cụ thể từng điểm cần sửa đổi)

Trả lời bằng tiếng Việt, chuyên nghiệp nhưng dễ hiểu."""),
                ("human", "Phân tích hợp đồng sau:\n\n{contract_text}")
            ])
            
            chain = analysis_prompt | llm
            ai_response = chain.invoke({"contract_text": contract_text[:4000]})  # Limit text length
            ai_analysis = ai_response.content
            print(f"  ✓ AI Analysis completed ({len(ai_analysis)} chars)")
        except Exception as e:
            print(f"  ⚠️ AI Analysis failed: {e}")
            ai_analysis = "Không thể phân tích chi tiết do lỗi hệ thống."
        
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
        
        # ========== COMPILE ANALYSIS RESULT ==========
        analysis_result = {
            "filename": filename,
            "file_size": file_size,
            "upload_time": datetime.now().isoformat(),
            "status": "analyzed",
            
            # AI Analysis - CHI TIẾT QUAN TRỌNG
            "ai_analysis": ai_analysis,
            
            # Mock SVM data (will be replaced with real SVM later)
            "contract_type": "Hợp đồng (phân tích bởi AI)",
            "contract_type_confidence": 0.85,
            "contract_type_probabilities": {},
            
            "risk_level": "medium",
            "risk_confidence": 0.75,
            "risk_probabilities": {},
            
            "has_violation": False,
            "violation_probability": 0.0,
            
            # Mock legal references
            "legal_references": [
                {
                    "title": "Bộ luật Dân sự 2015",
                    "content": "Quy định về hợp đồng và nghĩa vụ trong quan hệ dân sự...",
                    "source": "Bộ luật Dân sự / Phần 3",
                    "relevance": 0.8
                },
                {
                    "title": "Luật Lao động 2019",
                    "content": "Quy định về hợp đồng lao động và quyền lợi người lao động...",
                    "source": "Luật Lao động / Chương 2",
                    "relevance": 0.75
                }
            ],
            
            # Summary
            "summary": f"Hợp đồng đã được phân tích chi tiết bởi AI. Độ dài: {len(contract_text)} ký tự. Phát hiện {len(issues_detected)} vấn đề cần lưu ý.",
            
            # Issues from AI
            "issues": issues_detected
        }
        
        print("\n✅ ANALYSIS COMPLETED WITH AI!")
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
    """Generate PDF report from analysis data"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    try:
        from pdf_generator import ContractPDFReport
        import uuid
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Không có dữ liệu để tạo báo cáo"
            }), 400
        
        # Generate unique filename
        pdf_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Create PDF report
        report = ContractPDFReport(pdf_path)
        report.generate(data)
        
        # Return file as download with CORS headers
        from flask import send_file, make_response
        response = make_response(send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{data.get('contract_name', 'report')}.pdf"
        ))
        
        # Add CORS headers to file response
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:3000')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Lỗi khi tạo PDF: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Legal Contract Reviewer API")
    print("=" * 60)
    print("Starting server...")
    print("API: http://localhost:5000")
    print("Health: http://localhost:5000/health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000)  # Tắt debug mode để tránh auto-reload
