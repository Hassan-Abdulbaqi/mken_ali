from django.db import models
from django.conf import settings


class Item(models.Model):
    """Catalog item that can be ordered."""
    
    name = models.CharField(
        max_length=200,
        verbose_name='اسم المادة'
    )
    description = models.TextField(
        blank=True,
        verbose_name='الوصف'
    )
    image = models.ImageField(
        upload_to='items/',
        blank=True,
        null=True,
        verbose_name='الصورة'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_items',
        verbose_name='أنشأ بواسطة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'مادة'
        verbose_name_plural = 'المواد'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Order(models.Model):
    """Order containing multiple items."""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        PENDING_PRICING = 'pending_pricing', 'بانتظار الموافقة'
        PENDING_APPROVAL = 'pending_approval', 'بانتظار الموافقة'
        APPROVED = 'approved', 'موافق عليه'
        PARTIALLY_APPROVED = 'partially_approved', 'موافق عليه جزئياً'
        DECLINED = 'declined', 'مرفوض'
        ACKNOWLEDGED = 'acknowledged', 'تم الإطلاع'
    
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='الشعبة'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name='أنشأ بواسطة'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='الحالة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    priced_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='priced_orders',
        verbose_name='تم التسعير بواسطة'
    )
    priced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ التسعير'
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decided_orders',
        verbose_name='تم القرار بواسطة'
    )
    decided_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ القرار'
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات المدير'
    )
    
    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'طلب #{self.id} - {self.department.name}'
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def total_price(self):
        """Calculate total price of all items in the order.
        
        Uses approved_quantity when available for decided orders,
        and excludes declined items from the total.
        """
        total = 0
        for item in self.items.all():
            # Skip declined items
            if item.item_status == 'declined':
                continue
            if item.price:
                # Use approved_quantity if set, otherwise use original quantity
                qty = item.approved_quantity if item.approved_quantity is not None else item.quantity
                total += item.price * qty
        return total
    
    def get_status_color(self):
        """Return color class based on status."""
        colors = {
            'draft': 'bg-slate-100 text-slate-800',
            'pending_pricing': 'bg-yellow-100 text-yellow-800',
            'pending_approval': 'bg-blue-100 text-blue-800',
            'approved': 'bg-green-100 text-green-800',
            'partially_approved': 'bg-orange-100 text-orange-800',
            'declined': 'bg-red-100 text-red-800',
            'acknowledged': 'bg-purple-100 text-purple-800',
        }
        return colors.get(self.status, 'bg-slate-100 text-slate-800')


class OrderItem(models.Model):
    """Individual item within an order."""
    
    class ItemStatus(models.TextChoices):
        PENDING = 'pending', 'معلق'
        APPROVED = 'approved', 'موافق عليه'
        DECLINED = 'declined', 'مرفوض'
        MODIFIED = 'modified', 'معدل'
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='الطلب'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='المادة'
    )
    # Store item details directly in case item is deleted
    item_name = models.CharField(
        max_length=200,
        verbose_name='اسم المادة'
    )
    item_description = models.TextField(
        blank=True,
        verbose_name='وصف المادة'
    )
    item_image = models.ImageField(
        upload_to='order_items/',
        blank=True,
        null=True,
        verbose_name='صورة المادة'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='الكمية'
    )
    price = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='السعر (دينار عراقي)'
    )
    item_status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.PENDING,
        verbose_name='حالة المادة'
    )
    approved_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='الكمية الموافق عليها'
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name='ملاحظة المدير'
    )
    
    class Meta:
        verbose_name = 'مادة في الطلب'
        verbose_name_plural = 'مواد الطلب'
    
    def __str__(self):
        return f'{self.item_name} x {self.quantity}'
    
    @property
    def total_price(self):
        if self.price:
            return self.price * self.quantity
        return None
    
    @property
    def approved_total_price(self):
        if self.price:
            # Use approved_quantity if set, otherwise use original quantity
            qty = self.approved_quantity if self.approved_quantity is not None else self.quantity
            return self.price * qty
        return None
    
    def get_status_color(self):
        """Return color class based on item status."""
        colors = {
            'pending': 'bg-slate-100 text-slate-800',
            'approved': 'bg-green-100 text-green-800',
            'declined': 'bg-red-100 text-red-800',
            'modified': 'bg-orange-100 text-orange-800',
        }
        return colors.get(self.item_status, 'bg-slate-100 text-slate-800')


