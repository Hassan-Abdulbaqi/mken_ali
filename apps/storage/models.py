from django.db import models
from django.conf import settings


class StorageItem(models.Model):
    """Storage item model (مادة في المخزن)."""
    
    name = models.CharField(
        max_length=200,
        verbose_name='اسم المادة'
    )
    description = models.TextField(
        blank=True,
        verbose_name='الوصف'
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='الكمية'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='storage_items',
        verbose_name='الشعبة'
    )
    branch = models.ForeignKey(
        'departments.Branch',
        on_delete=models.CASCADE,
        related_name='storage_items',
        verbose_name='الفرع'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_storage_items',
        verbose_name='أضيف بواسطة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'مادة في المخزن'
        verbose_name_plural = 'مواد المخزن'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.quantity})'


class StorageItemHistory(models.Model):
    """History of changes to storage items."""
    
    class ActionType(models.TextChoices):
        CREATED = 'created', 'إنشاء'
        UPDATED = 'updated', 'تعديل'
        DELETED = 'deleted', 'حذف'
    
    storage_item = models.ForeignKey(
        StorageItem,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='المادة'
    )
    action = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        verbose_name='الإجراء'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='storage_item_changes',
        verbose_name='تم بواسطة'
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التغيير'
    )
    # Store what changed
    old_name = models.CharField(max_length=200, blank=True, verbose_name='الاسم السابق')
    new_name = models.CharField(max_length=200, blank=True, verbose_name='الاسم الجديد')
    old_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='الكمية السابقة')
    new_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='الكمية الجديدة')
    old_description = models.TextField(blank=True, verbose_name='الوصف السابق')
    new_description = models.TextField(blank=True, verbose_name='الوصف الجديد')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    
    class Meta:
        verbose_name = 'سجل تعديل'
        verbose_name_plural = 'سجل التعديلات'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f'{self.get_action_display()} - {self.storage_item.name} - {self.changed_by}'
    
    def get_changes_summary(self):
        """Get a summary of what changed."""
        changes = []
        if self.old_name and self.old_name != self.new_name:
            changes.append(f'الاسم: {self.old_name} ← {self.new_name}')
        if self.old_quantity is not None and self.old_quantity != self.new_quantity:
            changes.append(f'الكمية: {self.old_quantity} ← {self.new_quantity}')
        if self.old_description != self.new_description:
            changes.append('تم تعديل الوصف')
        return changes if changes else ['لا توجد تغييرات']
