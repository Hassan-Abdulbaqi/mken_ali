from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator

from apps.accounts.decorators import department_user_required
from apps.storage.models import StorageItem
from .models import Item, Order, OrderItem
from .forms import OrderItemForm


@login_required
@department_user_required
def create_order_view(request):
    """Create a new order with items."""
    # Get or create draft order for this user
    draft_order = Order.objects.filter(
        created_by=request.user,
        status=Order.Status.DRAFT
    ).first()
    
    if not draft_order and request.user.department:
        draft_order = Order.objects.create(
            department=request.user.department,
            created_by=request.user,
            status=Order.Status.DRAFT
        )
    elif not request.user.department:
        messages.error(request, 'يجب أن تكون منتسباً لشعبة لإنشاء طلب.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if using existing item
            existing_item_id = form.cleaned_data.get('existing_item_id')
            if existing_item_id:
                item = Item.objects.filter(id=existing_item_id).first()
            else:
                item = None
            
            # Create order item
            order_item = OrderItem.objects.create(
                order=draft_order,
                item=item,
                item_name=form.cleaned_data['item_name'],
                item_description=form.cleaned_data.get('item_description', ''),
                item_image=form.cleaned_data.get('item_image'),
                quantity=form.cleaned_data['quantity']
            )
            
            # Create item record for future reuse if new
            if not item:
                Item.objects.create(
                    name=form.cleaned_data['item_name'],
                    description=form.cleaned_data.get('item_description', ''),
                    image=form.cleaned_data.get('item_image'),
                    created_by=request.user
                )
            
            messages.success(request, 'تمت إضافة المادة بنجاح.')
            
            # Check if HTMX request
            if request.htmx:
                return render(request, 'orders/partials/order_items_list.html', {
                    'order': draft_order
                })
            
            return redirect('orders:create')
    else:
        form = OrderItemForm()
    
    # Get past items for quick selection
    past_items = Item.objects.filter(
        Q(created_by=request.user) | 
        Q(order_items__order__created_by=request.user)
    ).distinct().order_by('-created_at')[:20]
    
    return render(request, 'orders/create.html', {
        'form': form,
        'order': draft_order,
        'past_items': past_items
    })


@login_required
@department_user_required
def submit_order_view(request, order_id):
    """Submit a draft order for pricing."""
    order = get_object_or_404(Order, id=order_id, created_by=request.user, status=Order.Status.DRAFT)
    
    if order.items.count() == 0:
        messages.error(request, 'لا يمكن تقديم طلب فارغ.')
        return redirect('orders:create')
    
    order.status = Order.Status.PENDING_PRICING
    order.save()
    
    messages.success(request, 'تم تقديم الطلب بنجاح.')
    return redirect('orders:my_orders')


@login_required
@department_user_required
def my_orders_view(request):
    """View user's orders."""
    orders = Order.objects.filter(
        created_by=request.user
    ).exclude(status=Order.Status.DRAFT).select_related('department').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'orders/my_orders.html', {
        'page_obj': page_obj
    })


@login_required
def order_detail_view(request, order_id):
    """View order details."""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions
    user = request.user
    if user.is_department_user:
        if order.created_by != user:
            messages.error(request, 'ليس لديك صلاحية لعرض هذا الطلب.')
            return redirect('accounts:dashboard')
    
    # Department users should not see prices
    show_prices = not user.is_department_user
    
    return render(request, 'orders/detail.html', {
        'order': order,
        'show_prices': show_prices
    })


@login_required
@department_user_required
def remove_order_item_view(request, item_id):
    """Remove an item from a draft order."""
    order_item = get_object_or_404(
        OrderItem, 
        id=item_id, 
        order__created_by=request.user,
        order__status=Order.Status.DRAFT
    )
    
    order = order_item.order
    order_item.delete()
    
    messages.success(request, 'تم حذف المادة.')
    
    if request.htmx:
        return render(request, 'orders/partials/order_items_list.html', {
            'order': order
        })
    
    return redirect('orders:create')


@login_required
@department_user_required
def search_items_view(request):
    """HTMX endpoint for searching past items and storage items."""
    query = request.GET.get('item_name', '').strip()
    
    if len(query) < 2:
        return HttpResponse('')
    
    # Search past items (user's own past items and items they've ordered before)
    past_items = Item.objects.filter(
        Q(name__icontains=query) &
        (Q(created_by=request.user) | Q(order_items__order__created_by=request.user))
    ).distinct()[:10]
    
    # Search ALL storage items with available quantity
    storage_items = StorageItem.objects.filter(
        Q(name__icontains=query) &
        Q(quantity__gt=0)  # Only show items with available quantity
    ).select_related('department', 'branch').order_by('-quantity')[:15]
    
    return render(request, 'orders/partials/item_suggestions.html', {
        'items': past_items,
        'storage_items': storage_items,
    })


@login_required
@department_user_required
def quick_add_item_view(request, item_id):
    """Quickly add a past item to the current order."""
    item = get_object_or_404(Item, id=item_id)
    
    # Get or create draft order
    draft_order = Order.objects.filter(
        created_by=request.user,
        status=Order.Status.DRAFT
    ).first()
    
    if not draft_order and request.user.department:
        draft_order = Order.objects.create(
            department=request.user.department,
            created_by=request.user,
            status=Order.Status.DRAFT
        )
    
    if not draft_order:
        messages.error(request, 'يجب أن تكون منتسباً لشعبة لإنشاء طلب.')
        return redirect('accounts:dashboard')
    
    # Add item to order
    OrderItem.objects.create(
        order=draft_order,
        item=item,
        item_name=item.name,
        item_description=item.description,
        item_image=item.image,
        quantity=1
    )
    
    messages.success(request, f'تمت إضافة "{item.name}" للطلب.')
    
    if request.htmx:
        return render(request, 'orders/partials/order_items_list.html', {
            'order': draft_order
        })
    
    return redirect('orders:create')


