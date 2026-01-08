from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    """Custom login form with Arabic labels and styling."""
    
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': 'أدخل اسم المستخدم',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': 'أدخل كلمة المرور',
        })
    )
    
    error_messages = {
        'invalid_login': 'اسم المستخدم أو كلمة المرور غير صحيحة.',
        'inactive': 'هذا الحساب غير مفعل.',
    }


