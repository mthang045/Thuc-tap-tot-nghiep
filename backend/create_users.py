"""
Script tạo admin user và test users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def create_users():
    """Tạo users mẫu cho hệ thống"""
    
    print("🔧 Creating users...")
    
    # Tạo admin user
    if not User.objects.filter(email='admin@genzlegal.ai').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@genzlegal.ai',
            password='admin123'
        )
        print(f"✅ Created admin user: {admin.email}")
    else:
        print("ℹ️  Admin user already exists")
    
    # Tạo test user
    if not User.objects.filter(email='user@example.com').exists():
        user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='user123'
        )
        print(f"✅ Created test user: {user.email}")
    else:
        print("ℹ️  Test user already exists")
    
    # Hiển thị tất cả users
    print("\n📋 Current users:")
    for u in User.objects.all():
        role = "Admin" if (u.is_staff or u.is_superuser) else "User"
        print(f"  - {u.email or u.username} ({role})")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    create_users()
