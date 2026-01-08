from django.contrib import admin
from .models import Branch, Department


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'created_at')
    list_filter = ('branch',)
    search_fields = ('name', 'branch__name')
    ordering = ('branch__name', 'name')
