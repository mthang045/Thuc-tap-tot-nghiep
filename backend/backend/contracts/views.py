from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
from .models import Contract, Analysis, Issue, UserProfile
from .serializers import (
    ContractSerializer, ContractUploadSerializer, AnalysisSerializer,
    LoginSerializer, RegisterSerializer, UserProfileSerializer
)
import sys
import os

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

