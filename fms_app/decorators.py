from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with admin credentials to access this page.")
            return redirect('admin_login')
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Access denied. Admin privileges required.")
            if hasattr(request.user, 'student_profile'):
                return redirect('student_feedback_form')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the feedback portal.")
            return redirect('student_login')
        if not hasattr(request.user, 'student_profile'):
            if request.user.is_superuser or request.user.is_staff:
                messages.info(request, "You are logged in as an Administrator.")
                return redirect('admin_dashboard')
            messages.error(request, "No student profile found for your account.")
            return redirect('student_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
