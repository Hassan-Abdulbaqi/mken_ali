"""
Setup script to create initial data for the procurement system.
Run this after migrations: python setup_data.py
"""

import os
import sys
import io
import django

# Fix Unicode output for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.accounts.models import User
from apps.departments.models import Department


def create_departments():
    """Create sample departments."""
    departments = [
        'شعبة تقنية المعلومات',
        'شعبة الموارد البشرية',
        'شعبة المحاسبة',
        'شعبة الإدارة',
        'شعبة الخدمات',
    ]
    
    created = []
    for name in departments:
        dept, was_created = Department.objects.get_or_create(name=name)
        if was_created:
            created.append(name)
    
    if created:
        print(f'✓ تم إنشاء الشعب: {", ".join(created)}')
    else:
        print('✓ الشعب موجودة مسبقاً')
    
    return Department.objects.all()


def create_users(departments):
    """Create sample users for each role."""
    # Get first department for demo users
    dept = departments.first()
    
    users_data = [
        {
            'username': 'department_user',
            'password': 'demo123456',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'email': 'dept@example.com',
            'role': User.Role.DEPARTMENT_USER,
            'department': dept,
        },
        {
            'username': 'procurement',
            'password': 'demo123456',
            'first_name': 'علي',
            'last_name': 'حسين',
            'email': 'procurement@example.com',
            'role': User.Role.PROCUREMENT_COMMITTEE,
            'department': None,
        },
        {
            'username': 'admin',
            'password': 'demo123456',
            'first_name': 'المدير',
            'last_name': 'العام',
            'email': 'admin@example.com',
            'role': User.Role.ADMINISTRATOR,
            'department': None,
        },
    ]
    
    created = []
    for data in users_data:
        username = data.pop('username')
        password = data.pop('password')
        
        user, was_created = User.objects.get_or_create(
            username=username,
            defaults=data
        )
        
        if was_created:
            user.set_password(password)
            user.save()
            created.append(f'{username} ({user.get_role_display()})')
    
    if created:
        print(f'✓ تم إنشاء المستخدمين: {", ".join(created)}')
    else:
        print('✓ المستخدمين موجودين مسبقاً')


def create_superuser():
    """Create superuser for admin panel."""
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='superadmin123',
            first_name='مدير',
            last_name='النظام'
        )
        print('✓ تم إنشاء المستخدم الخارق: superadmin / superadmin123')
    else:
        print('✓ المستخدم الخارق موجود مسبقاً')


def main():
    print('\n' + '='*50)
    print('إعداد البيانات الأولية لنظام المشتريات')
    print('='*50 + '\n')
    
    departments = create_departments()
    create_users(departments)
    create_superuser()
    
    print('\n' + '='*50)
    print('بيانات تسجيل الدخول التجريبية:')
    print('='*50)
    print('مسؤول الشعبة: department_user / demo123456')
    print('لجنة المشتريات: procurement / demo123456')
    print('المدير: admin / demo123456')
    print('مدير النظام: superadmin / superadmin123')
    print('='*50 + '\n')


if __name__ == '__main__':
    main()

