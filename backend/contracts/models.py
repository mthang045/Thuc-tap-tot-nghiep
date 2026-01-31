from django.db import models
from django.contrib.auth.models import User


class Contract(models.Model):
    """Model for uploaded contracts"""
    STATUS_CHOICES = [
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Lỗi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts')
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='contracts/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.user.email}"


class Analysis(models.Model):
    """Model for contract analysis results"""
    SEVERITY_CHOICES = [
        ('high', 'Nghiêm trọng'),
        ('medium', 'Trung bình'),
        ('low', 'Thấp'),
    ]
    
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='analysis')
    total_issues = models.IntegerField(default=0)
    high_risk = models.IntegerField(default=0)
    medium_risk = models.IntegerField(default=0)
    low_risk = models.IntegerField(default=0)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Analyses'
    
    def __str__(self):
        return f"Analysis for {self.contract.file_name}"


class Issue(models.Model):
    """Model for individual issues found in contract"""
    SEVERITY_CHOICES = [
        ('high', 'Nghiêm trọng'),
        ('medium', 'Trung bình'),
        ('low', 'Thấp'),
    ]
    
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='issues')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    article = models.CharField(max_length=255, blank=True)
    recommendation = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.severity}: {self.title}"


class UserProfile(models.Model):
    """Extended user profile"""
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile: {self.user.email}"

