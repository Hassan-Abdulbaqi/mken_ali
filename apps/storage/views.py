from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from apps.accounts.decorators import storage_user_required
from apps.departments.models import Department, Branch
from .models import StorageItem, StorageItemHistory
from .forms import StorageItemForm


@login_required
def storage_list_view(request):
    """View storage items based on user role."""
    user = request.user
    
    # Base queryset
    items = StorageItem.objects.select_related('department', 'branch', 'created_by')
    
    # Filter by role
    if user.is_department_user:
        # Department users can only see items for their department
        if user.department:
            items = items.filter(department=user.department)
        else:
            items = items.none()
    # Storage users, procurement committee, and administrators can see all
    
    # Apply filters from query params
    branch_id = request.GET.get('branch')
    department_id = request.GET.get('department')
    search = request.GET.get('search', '').strip()
    
    if branch_id:
        items = items.filter(branch_id=branch_id)
    if department_id:
        items = items.filter(department_id=department_id)
    if search:
        items = items.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    branches = Branch.objects.all()
    departments = Department.objects.all()
    if branch_id:
        # Include departments that belong to this branch OR have no branch assigned
        departments = departments.filter(Q(branch_id=branch_id) | Q(branch__isnull=True))
    
    context = {
        'page_obj': page_obj,
        'branches': branches,
        'departments': departments,
        'selected_branch': branch_id,
        'selected_department': department_id,
        'search_query': search,
        'can_manage': user.is_storage_user,
    }
    
    return render(request, 'storage/list.html', context)


@login_required
@storage_user_required
def storage_add_view(request):
    """Add a new storage item."""
    if request.method == 'POST':
        form = StorageItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            
            # Record creation in history
            StorageItemHistory.objects.create(
                storage_item=item,
                action=StorageItemHistory.ActionType.CREATED,
                changed_by=request.user,
                new_name=item.name,
                new_quantity=item.quantity,
                new_description=item.description,
                notes='تم إنشاء المادة'
            )
            
            messages.success(request, 'تم إضافة المادة بنجاح.')
            return redirect('storage:list')
    else:
        form = StorageItemForm()
    
    return render(request, 'storage/form.html', {
        'form': form,
        'title': 'إضافة مادة جديدة',
        'submit_text': 'إضافة',
    })


@login_required
@storage_user_required
def storage_edit_view(request, item_id):
    """Edit an existing storage item."""
    item = get_object_or_404(StorageItem, id=item_id)
    
    # Store old values for history
    old_name = item.name
    old_quantity = item.quantity
    old_description = item.description
    
    if request.method == 'POST':
        form = StorageItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save()
            
            # Check if anything changed and record history
            if (old_name != updated_item.name or 
                old_quantity != updated_item.quantity or 
                old_description != updated_item.description):
                
                StorageItemHistory.objects.create(
                    storage_item=updated_item,
                    action=StorageItemHistory.ActionType.UPDATED,
                    changed_by=request.user,
                    old_name=old_name,
                    new_name=updated_item.name,
                    old_quantity=old_quantity,
                    new_quantity=updated_item.quantity,
                    old_description=old_description,
                    new_description=updated_item.description,
                )
            
            messages.success(request, 'تم تحديث المادة بنجاح.')
            return redirect('storage:list')
    else:
        form = StorageItemForm(instance=item)
    
    # Get history for this item
    history = item.history.select_related('changed_by').all()[:10]
    
    return render(request, 'storage/form.html', {
        'form': form,
        'item': item,
        'history': history,
        'title': f'تعديل: {item.name}',
        'submit_text': 'حفظ التغييرات',
    })


@login_required
@storage_user_required
def storage_delete_view(request, item_id):
    """Delete a storage item."""
    item = get_object_or_404(StorageItem, id=item_id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'تم حذف المادة بنجاح.')
        return redirect('storage:list')
    
    return render(request, 'storage/confirm_delete.html', {
        'item': item,
    })


@login_required
def get_departments_by_branch(request):
    """AJAX endpoint to get departments for a specific branch."""
    branch_id = request.GET.get('branch_id')
    
    if branch_id:
        # Include departments that belong to this branch OR have no branch assigned
        departments = Department.objects.filter(
            Q(branch_id=branch_id) | Q(branch__isnull=True)
        ).values('id', 'name')
        return JsonResponse(list(departments), safe=False)
    
    # Return all departments if no branch selected
    departments = Department.objects.all().values('id', 'name')
    return JsonResponse(list(departments), safe=False)

