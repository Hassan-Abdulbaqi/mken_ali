from django.contrib import admin
from .models import Item, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_name', 'item_description', 'quantity', 'price', 'item_status', 'approved_quantity')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('department__name', 'created_by__username')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'order', 'quantity', 'price', 'item_status')
    list_filter = ('item_status', 'order__status')
    search_fields = ('item_name',)


