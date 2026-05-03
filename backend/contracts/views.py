from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import FileResponse, HttpResponse
from django.middleware.csrf import get_token
from .models import Contract, Analysis, Issue, UserProfile
from .serializers import (
    ContractSerializer, ContractUploadSerializer, AnalysisSerializer,
    LoginSerializer, RegisterSerializer, UserProfileSerializer
)
import sys
import os
import io

try:
    from docx import Document
except Exception:
    Document = None

from .docx_formatter import format_document

# Add src to path for Legal AI agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Get CSRF token"""
    return Response({'csrfToken': get_token(request)})


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet for Contract CRUD operations"""
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contract.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get analysis results for a contract"""
        contract = self.get_object()
        if hasattr(contract, 'analysis'):
            serializer = AnalysisSerializer(contract.analysis)
            return Response(serializer.data)
        return Response({'error': 'Analysis not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def upload_contract(request):
    """Upload and analyze a contract"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = ContractUploadSerializer(data=request.data)
    if serializer.is_valid():
        file = serializer.validated_data['file']
        
        # Create contract record
        contract = Contract.objects.create(
            user=request.user,
            file_name=file.name,
            file=file,
            status='processing'
        )
        
        # TODO: Trigger async analysis task here
        # For now, create dummy analysis
        try:
            # Import and run the legal AI agent
            from src.workflow.graph import build_graph
            
            # Save file temporarily
            file_path = contract.file.path
            
            # Run analysis
            graph = build_graph()
            result = graph.invoke({
                "file_path": file_path,
                "query": "Phân tích hợp đồng này"
            })
            
            # Extract results
            issues = result.get('issues', [])
            
            # Create analysis
            analysis = Analysis.objects.create(
                contract=contract,
                total_issues=len(issues),
                high_risk=len([i for i in issues if i.get('severity') == 'high']),
                medium_risk=len([i for i in issues if i.get('severity') == 'medium']),
                low_risk=len([i for i in issues if i.get('severity') == 'low']),
            )
            
            # Create issues
            for issue_data in issues:
                Issue.objects.create(
                    analysis=analysis,
                    severity=issue_data.get('severity', 'low'),
                    title=issue_data.get('title', ''),
                    description=issue_data.get('description', ''),
                    article=issue_data.get('article', ''),
                    recommendation=issue_data.get('recommendation', ''),
                    location=issue_data.get('location', ''),
                )
            
            contract.status = 'completed'
            contract.save()
            
        except Exception as e:
            print(f"Analysis error: {e}")
            contract.status = 'failed'
            contract.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                return Response({
                    'success': True,
                    'email': user.email,
                    'is_admin': user.is_staff,
                })
        except User.DoesNotExist:
            pass
        
        return Response({'success': False, 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """User registration"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        full_name = serializer.validated_data['full_name']
        phone = serializer.validated_data.get('phone', '')
        
        # Create user
        username = email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )
        
        # Create profile
        UserProfile.objects.create(
            user=user,
            phone=phone
        )
        
        # Auto login
        login(request, user)
        
        return Response({
            'success': True,
            'email': user.email,
            'is_admin': False,
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    """User logout"""
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_view(request):
    """Get user's contract analysis history"""
    contracts = Contract.objects.filter(user=request.user)
    serializer = ContractSerializer(contracts, many=True)
    
    return Response({
        'success': True,
        'history': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    """Get admin statistics"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    total_users = User.objects.count()
    total_contracts = Contract.objects.count()
    total_analyses = Analysis.objects.count()
    
    return Response({
        'total_users': total_users,
        'total_contracts': total_contracts,
        'total_analyses': total_analyses,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def svm_classify_contract(request):
    """
    API endpoint for SVM-based contract classification
    Phân loại hợp đồng sử dụng SVM Classifier
    """
    try:
        from src.classifier import SVMContractClassifier
        
        # Get contract text from request
        contract_text = request.data.get('text', '')
        
        if not contract_text:
            return Response(
                {'error': 'Contract text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load SVM classifier
        classifier = SVMContractClassifier(model_dir="models/svm")
        
        # Analyze contract
        results = classifier.analyze_contract(contract_text)
        
        # Format response
        response_data = {
            'success': True,
            'analysis': results
        }
        
        # Add detailed information
        if 'contract_type' in results:
            response_data['contract_type'] = results['contract_type']['predicted_type']
            response_data['type_confidence'] = results['contract_type']['confidence']
        
        if 'risk_assessment' in results:
            response_data['risk_level'] = results['risk_assessment']['predicted_risk']
            response_data['risk_confidence'] = results['risk_assessment']['confidence']
        
        if 'violation_check' in results:
            response_data['has_violation'] = results['violation_check']['has_violation']
            response_data['violation_probability'] = results['violation_check']['violation_probability']
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Classification error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def svm_detect_violation(request):
    """
    API endpoint for SVM-based violation detection
    Phát hiện vi phạm pháp luật trong điều khoản hợp đồng
    """
    try:
        from src.classifier import SVMContractClassifier
        
        # Get clause text from request
        clause_text = request.data.get('text', '')
        
        if not clause_text:
            return Response(
                {'error': 'Clause text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Load SVM classifier
        classifier = SVMContractClassifier(model_dir="models/svm")
        
        # Detect violation
        result = classifier.detect_violation(clause_text)
        
        response_data = {
            'success': True,
            'has_violation': result['has_violation'],
            'violation_probability': result['violation_probability'],
            'confidence': result['confidence']
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Detection error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== TEMPLATE MANAGEMENT ====================

# Map template IDs to file paths (relative to static/templates/)
TEMPLATE_FILES = {
    'hop_dong_mua_ban_hang_hoa': 'hop_dong_mua_ban_hang_hoa.txt',
    'hop_dong_lao_dong': 'hop_dong_lao_dong.txt',
    'hop_dong_bao_mat': 'hop_dong_bao_mat.txt',
    'hop_dong_thue_nha': 'hop_dong_thue_nha.txt',
    'hop_dong_cung_cap_dich_vu': 'hop_dong_cung_cap_dich_vu.txt',
    'hop_dong_cho_vay_tien': 'hop_dong_cho_vay_tien.txt',
    'giay_uy_quyen': 'giay_uy_quyen.txt',
    'bien_ban_hop': 'bien_ban_hop.txt',
    'quyet_dinh_bo_nhiem': 'quyet_dinh_bo_nhiem.txt',
    'don_xin_nghi_viec': 'don_xin_nghi_viec.txt',
}

# Human-readable names for download filenames
TEMPLATE_NAMES = {
    'hop_dong_mua_ban_hang_hoa': 'Mau_Hop_Dong_Mua_Ban_Hang_Hoa',
    'hop_dong_lao_dong': 'Mau_Hop_Dong_Lao_Dong',
    'hop_dong_bao_mat': 'Mau_Thoa_Thuan_Bao_Mat_NDA',
    'hop_dong_thue_nha': 'Mau_Hop_Dong_Thue_Nha_O',
    'hop_dong_cung_cap_dich_vu': 'Mau_Hop_Dong_Cung_Cap_Dich_Vu',
    'hop_dong_cho_vay_tien': 'Mau_Hop_Dong_Cho_Vay_Tien',
    'giay_uy_quyen': 'Mau_Giay_Uy_Quyen',
    'bien_ban_hop': 'Mau_Bien_Ban_Hop',
    'quyet_dinh_bo_nhiem': 'Mau_Quyet_Dinh_Bo_Nhiem',
    'don_xin_nghi_viec': 'Mau_Don_Xin_Nghi_Viec',
}

# Template metadata
TEMPLATE_METADATA = {
    'hop_dong_mua_ban_hang_hoa': {
        'title': 'Hợp đồng mua bán hàng hóa',
        'category': 'Thương mại',
        'description': 'Mẫu hợp đồng mua bán hàng hóa theo quy định pháp luật Việt Nam.',
        'tags': ['thương mại', 'mua bán', 'hàng hóa'],
    },
    'hop_dong_lao_dong': {
        'title': 'Hợp đồng lao động',
        'category': 'Nhân sự',
        'description': 'Mẫu HĐLĐ theo Bộ luật Lao động 2019, bao gồm đầy đủ điều khoản về quyền và nghĩa vụ.',
        'tags': ['nhân sự', 'lao động', 'Bộ luật Lao động'],
    },
    'hop_dong_bao_mat': {
        'title': 'Thỏa thuận bảo mật (NDA)',
        'category': 'Pháp lý',
        'description': 'Thỏa thuận bảo mật thông tin giữa các bên.',
        'tags': ['bảo mật', 'NDA', 'thỏa thuận'],
    },
    'hop_dong_thue_nha': {
        'title': 'Hợp đồng thuê nhà ở',
        'category': 'Bất động sản',
        'description': 'Mẫu hợp đồng thuê nhà ở theo quy định của pháp luật.',
        'tags': ['bất động sản', 'thuê nhà', 'nhà ở'],
    },
    'hop_dong_cung_cap_dich_vu': {
        'title': 'Hợp đồng cung cấp dịch vụ',
        'category': 'Thương mại',
        'description': 'Mẫu hợp đồng cung cấp dịch vụ giữa các bên.',
        'tags': ['dịch vụ', 'thương mại', 'hợp đồng'],
    },
    'hop_dong_cho_vay_tien': {
        'title': 'Hợp đồng cho vay tiền',
        'category': 'Tài chính',
        'description': 'Mẫu hợp đồng cho vay tiền với lãi suất và điều khoản chi tiết.',
        'tags': ['tài chính', 'cho vay', 'tiền tệ'],
    },
    'giay_uy_quyen': {
        'title': 'Giấy ủy quyền',
        'category': 'Pháp lý',
        'description': 'Mẫu giấy ủy quyền cho cá nhân hoặc tổ chức.',
        'tags': ['ủy quyền', 'pháp lý', 'cá nhân'],
    },
    'bien_ban_hop': {
        'title': 'Biên bản họp',
        'category': 'Nội bộ',
        'description': 'Mẫu biên bản họp cho các cuộc họp công ty.',
        'tags': ['nội bộ', 'biên bản', 'họp'],
    },
    'quyet_dinh_bo_nhiem': {
        'title': 'Quyết định bổ nhiệm',
        'category': 'Nhân sự',
        'description': 'Mẫu quyết định bổ nhiệm chức vụ theo Luật Doanh nghiệp 2020.',
        'tags': ['nhân sự', 'bổ nhiệm', 'doanh nghiệp'],
    },
    'don_xin_nghi_viec': {
        'title': 'Đơn xin nghỉ việc',
        'category': 'Nhân sự',
        'description': 'Mẫu đơn xin nghỉ việc cho người lao động.',
        'tags': ['nhân sự', 'nghỉ việc', 'đơn từ'],
    },
}


def _build_docx_from_text(text_content, title):
    """Build a formatted DOCX in memory from text content."""
    if Document is None:
        raise RuntimeError('python-docx is not installed on the server')

    return format_document(text_content, title)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """List all available contract templates."""
    templates = []
    for template_id, metadata in TEMPLATE_METADATA.items():
        templates.append({
            'id': template_id,
            **metadata,
        })
    
    return Response({
        'success': True,
        'templates': templates,
        'total': len(templates),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_template(request, template_id):
    """Download a contract template as a properly formatted DOCX file."""
    if template_id not in TEMPLATE_FILES:
        return Response(
            {'error': f'Template not found: {template_id}'},
            status=status.HTTP_404_NOT_FOUND
        )

    filename = TEMPLATE_FILES[template_id]
    download_name = TEMPLATE_NAMES.get(template_id, template_id)
    metadata = TEMPLATE_METADATA.get(template_id, {})
    title = metadata.get('title', download_name.replace('_', ' '))

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(backend_dir, 'static', 'templates', filename)

    if not os.path.exists(file_path):
        return Response(
            {'error': f'Template file not found on server: {filename}'},
            status=status.HTTP_404_NOT_FOUND
        )

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        text_content = f.read()

    try:
        docx_buffer = _build_docx_from_text(text_content, title)
    except RuntimeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    response = HttpResponse(
        docx_buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{download_name}.docx'
    return response