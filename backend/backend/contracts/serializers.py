from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Contract, Analysis, Issue, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'phone', 'company', 'position', 'plan', 'created_at', 'updated_at']


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'severity', 'title', 'description', 'article', 'recommendation', 'location']


class AnalysisSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True, read_only=True)
    
    class Meta:
        model = Analysis
        fields = ['id', 'total_issues', 'high_risk', 'medium_risk', 'low_risk', 'analyzed_at', 'issues']


class ContractSerializer(serializers.ModelSerializer):
    analysis = AnalysisSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Contract
        fields = ['id', 'user_email', 'file_name', 'file', 'uploaded_at', 'status', 'analysis']
        read_only_fields = ['uploaded_at', 'status']


class ContractUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Validate file extension
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = '.' + value.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError("File must be PDF, DOC, DOCX, or TXT")
        
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
