from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access."""
    
    class Role(models.TextChoices):
        DEPARTMENT_USER = 'department_user', 'مسؤول الشعبة'
        PROCUREMENT_COMMITTEE = 'procurement_committee', 'لجنة المشتريات'
        ADMINISTRATOR = 'administrator', 'المدير'
        STORAGE_USER = 'storage_user', 'مخزن'
    
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.DEPARTMENT_USER,
        verbose_name='الدور'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='الشعبة'
    )
    branch = models.ForeignKey(
        'departments.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='الفرع'
    )
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    @property
    def is_department_user(self):
        return self.role == self.Role.DEPARTMENT_USER
    
    @property
    def is_procurement_committee(self):
        return self.role == self.Role.PROCUREMENT_COMMITTEE
    
    @property
    def is_administrator(self):
        return self.role == self.Role.ADMINISTRATOR
    
    @property
    def is_storage_user(self):
        return self.role == self.Role.STORAGE_USER
