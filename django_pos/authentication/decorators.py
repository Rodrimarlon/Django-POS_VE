from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.utils.translation import gettext_lazy as _ # Import gettext_lazy

def admin_required(function=None, redirect_field_name=None, login_url='authentication:login'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _("You must be logged in to access this page."), extra_tags="danger")
                return redirect(login_url)
            if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
                messages.error(request, _("Access denied. Only administrators can access this page."), extra_tags="danger")
                return redirect('pos:index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator

def cashier_required(function=None, redirect_field_name=None, login_url='authentication:login'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _("You must be logged in to access this page."), extra_tags="danger")
                return redirect(login_url)
            if not hasattr(request.user, 'profile') or request.user.profile.role != 'cashier':
                messages.error(request, _("Access denied. Only cashiers can access this page."), extra_tags="danger")
                return redirect('pos:index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator

def role_required(allowed_roles=[], function=None, redirect_field_name=None, login_url='authentication:login'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _("You must be logged in to access this page."), extra_tags="danger")
                return redirect(login_url)
            if not hasattr(request.user, 'profile') or request.user.profile.role not in allowed_roles:
                messages.error(request, _("Access denied. You do not have the required role to access this page."), extra_tags="danger")
                return redirect('pos:index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator