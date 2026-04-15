from django.contrib import admin
from .models import Contract, Analysis, Issue, UserProfile


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'user', 'status', 'uploaded_at']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['file_name', 'user__email']
    readonly_fields = ['uploaded_at']


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['contract', 'total_issues', 'high_risk', 'medium_risk', 'low_risk', 'analyzed_at']
    readonly_fields = ['analyzed_at']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'analysis']
    list_filter = ['severity']
    search_fields = ['title', 'description']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'company', 'plan', 'created_at']
    list_filter = ['plan', 'created_at']
    search_fields = ['user__email', 'company']
    readonly_fields = ['created_at', 'updated_at']

