from django.contrib import admin
from .models import StorageItem, StorageItemHistory


class StorageItemHistoryInline(admin.TabularInline):
    model = StorageItemHistory
    extra = 0
    readonly_fields = ('action', 'changed_by', 'changed_at', 'old_name', 'new_name', 
                       'old_quantity', 'new_quantity', 'old_description', 'new_description', 'notes')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(StorageItem)
class StorageItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'department', 'branch', 'created_by', 'created_at')
    list_filter = ('branch', 'department', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    inlines = [StorageItemHistoryInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StorageItemHistory)
class StorageItemHistoryAdmin(admin.ModelAdmin):
    list_display = ('storage_item', 'action', 'changed_by', 'changed_at')
    list_filter = ('action', 'changed_at')
    search_fields = ('storage_item__name', 'changed_by__username')
    ordering = ('-changed_at',)
    readonly_fields = ('storage_item', 'action', 'changed_by', 'changed_at', 
                       'old_name', 'new_name', 'old_quantity', 'new_quantity',
                       'old_description', 'new_description', 'notes')
