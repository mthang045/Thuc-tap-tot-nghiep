from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contracts', views.ContractViewSet, basename='contract')

urlpatterns = [
    path('', include(router.urls)),
    path('csrf/', views.get_csrf_token, name='csrf'),
    path('upload/', views.upload_contract, name='upload'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history_view, name='history'),
    path('admin/stats/', views.stats_view, name='stats'),
    # SVM Classification endpoints
    path('svm/classify/', views.svm_classify_contract, name='svm_classify'),
    path('svm/detect-violation/', views.svm_detect_violation, name='svm_detect_violation'),
]
