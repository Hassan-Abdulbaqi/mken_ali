from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Decorator to restrict view access to specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.role not in roles:
                messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة.')
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def department_user_required(view_func):
    """Decorator to restrict view to department users only."""
    return role_required('department_user')(view_func)


def procurement_committee_required(view_func):
    """Decorator to restrict view to procurement committee only."""
    return role_required('procurement_committee')(view_func)


def administrator_required(view_func):
    """Decorator to restrict view to administrators only."""
    return role_required('administrator')(view_func)


def storage_user_required(view_func):
    """Decorator to restrict view to storage users only."""
    return role_required('storage_user')(view_func)
