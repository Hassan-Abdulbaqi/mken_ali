from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import LoginForm
from .models import User
from apps.orders.models import Order
from apps.storage.models import StorageItem


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'مرحباً {user.get_full_name() or user.username}!')
            return redirect('accounts:dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """Display dashboard based on user role."""
    user = request.user
    context = {'user': user}
    
    if user.is_department_user:
        # Get user's recent orders
        recent_orders = Order.objects.filter(
            created_by=user
        ).select_related('department')[:5]
        
        # Get order counts by status
        order_stats = {
            'total': Order.objects.filter(created_by=user).count(),
            'pending': Order.objects.filter(created_by=user, status__in=['draft', 'pending_pricing', 'pending_approval']).count(),
            'approved': Order.objects.filter(created_by=user, status__in=['approved', 'partially_approved']).count(),
            'declined': Order.objects.filter(created_by=user, status='declined').count(),
        }
        context['recent_orders'] = recent_orders
        context['order_stats'] = order_stats
        
    elif user.is_procurement_committee:
        # Get orders awaiting pricing
        pending_pricing = Order.objects.filter(
            status='pending_pricing'
        ).select_related('department', 'created_by')[:5]
        
        # Get orders with admin decisions awaiting acknowledgment
        pending_acknowledgment = Order.objects.filter(
            status__in=['approved', 'partially_approved', 'declined']
        ).select_related('department', 'created_by')[:5]
        
        stats = {
            'pending_pricing': Order.objects.filter(status='pending_pricing').count(),
            'pending_approval': Order.objects.filter(status='pending_approval').count(),
            'pending_acknowledgment': Order.objects.filter(
                status__in=['approved', 'partially_approved', 'declined']
            ).count(),
        }
        context['pending_pricing'] = pending_pricing
        context['pending_acknowledgment'] = pending_acknowledgment
        context['stats'] = stats
        
    elif user.is_administrator:
        # Get orders awaiting approval
        pending_approval = Order.objects.filter(
            status='pending_approval'
        ).select_related('department', 'created_by', 'priced_by')[:5]
        
        # Get recent decisions
        recent_decisions = Order.objects.filter(
            decided_by__isnull=False
        ).select_related('department', 'created_by').order_by('-decided_at')[:5]
        
        stats = {
            'pending_approval': Order.objects.filter(status='pending_approval').count(),
            'approved_today': Order.objects.filter(
                status__in=['approved', 'partially_approved'],
                decided_at__date=request.user.date_joined.date()  # Just for demo
            ).count(),
            'total_processed': Order.objects.filter(decided_by__isnull=False).count(),
        }
        context['pending_approval'] = pending_approval
        context['recent_decisions'] = recent_decisions
        context['stats'] = stats
    
    elif user.is_storage_user:
        # Get storage stats
        recent_items = StorageItem.objects.select_related(
            'department', 'branch'
        ).order_by('-created_at')[:5]
        
        stats = {
            'total_items': StorageItem.objects.count(),
            'low_stock': StorageItem.objects.filter(quantity__lt=10).count(),
            'out_of_stock': StorageItem.objects.filter(quantity=0).count(),
        }
        context['recent_items'] = recent_items
        context['stats'] = stats
    
    return render(request, 'accounts/dashboard.html', context)


