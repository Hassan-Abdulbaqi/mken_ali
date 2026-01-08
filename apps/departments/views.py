from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Department


@staff_member_required
def department_list_view(request):
    """List all departments (admin only)."""
    departments = Department.objects.all()
    return render(request, 'departments/list.html', {
        'departments': departments
    })


