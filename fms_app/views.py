from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Student, Teacher, Feedback
from .forms import StudentForm, TeacherForm, FeedbackSubmissionForm, StudentPasswordChangeForm
from .decorators import admin_required, student_required


def index_redirect(request):
    """Entry point: redirect authenticated users or show student login."""
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'student_profile'):
            return redirect('student_feedback_form')
    return redirect('student_login')


def admin_login_view(request):
    """Admin login page."""
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'student_profile'):
            return redirect('student_feedback_form')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser or user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, Administrator {user.username}!")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access restricted. This login is for Administrators only.")
        else:
            messages.error(request, "Invalid admin username or password.")

    return render(request, 'admin_login.html')


def student_login_view(request):
    """Student login page."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'student_profile'):
            return redirect('student_feedback_form')
        elif request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'student_profile'):
                login(request, user)
                messages.success(request, f"Welcome {user.student_profile.name}!")
                return redirect('student_feedback_form')
            else:
                # User exists but isn't student
                if user.is_superuser or user.is_staff:
                    login(request, user)
                    return redirect('admin_dashboard')
                messages.error(request, "No student profile associated with this account.")
        else:
            messages.error(request, "Invalid username or password. Please check your credentials.")

    return render(request, 'student_login.html')


def logout_view(request):
    """Universal logout."""
    is_admin = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    if is_admin:
        return redirect('admin_login')
    return redirect('student_login')


# ==========================================
# ADMIN VIEWS
# ==========================================

@admin_required
def admin_dashboard_view(request):
    """Admin Dashboard with summary cards, recent feedback, and filters."""
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_feedback = Feedback.objects.count()

    # Search & filters for Recent Feedback
    search_query = request.GET.get('search', '').strip()
    selected_department = request.GET.get('department', '').strip()
    selected_teacher = request.GET.get('teacher', '').strip()

    feedback_qs = Feedback.objects.select_related('student', 'teacher').all()

    if search_query:
        feedback_qs = feedback_qs.filter(
            Q(student__name__icontains=search_query) |
            Q(student__roll_number__icontains=search_query) |
            Q(teacher__name__icontains=search_query)
        )

    if selected_department:
        feedback_qs = feedback_qs.filter(student__department__iexact=selected_department)

    if selected_teacher:
        feedback_qs = feedback_qs.filter(teacher__id=selected_teacher)

    recent_feedback = feedback_qs.order_by('-created_at')

    # Dropdown lists for filter options
    departments = Student.objects.values_list('department', flat=True).distinct().order_by('department')
    teachers = Teacher.objects.all().order_by('name')

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_feedback': total_feedback,
        'recent_feedback': recent_feedback,
        'departments': departments,
        'teachers': teachers,
        'search_query': search_query,
        'selected_department': selected_department,
        'selected_teacher': selected_teacher,
    }
    return render(request, 'admin/dashboard.html', context)


@admin_required
def students_list_view(request):
    """Student management list view."""
    students = Student.objects.all().order_by('id')
    return render(request, 'admin/students.html', {'students': students})


@admin_required
def student_add_view(request):
    """Admin adds a new student; credentials automatically created."""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student '{student.name}' added successfully! Login credentials created: Username = '{student.name}', Password = '{student.roll_number}'"
            )
            return redirect('admin_students')
    else:
        form = StudentForm()

    return render(request, 'admin/student_form.html', {'form': form, 'title': 'Add Student'})


@admin_required
def student_edit_view(request, pk):
    """Admin edits existing student."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{student.name}' updated successfully.")
            return redirect('admin_students')
    else:
        form = StudentForm(instance=student)

    return render(request, 'admin/student_form.html', {'form': form, 'title': 'Edit Student', 'student': student})


@admin_required
@require_POST
def student_delete_view(request, pk):
    """Admin deletes a student and their login user account."""
    student = get_object_or_404(Student, pk=pk)
    student_name = student.name
    user = student.user
    student.delete()
    if user:
        user.delete()
    messages.success(request, f"Student '{student_name}' and associated login credentials deleted successfully.")
    return redirect('admin_students')


@admin_required
def teachers_list_view(request):
    """Teacher management list view."""
    teachers = Teacher.objects.all().order_by('id')
    return render(request, 'admin/teachers.html', {'teachers': teachers})


@admin_required
def teacher_add_view(request):
    """Admin adds a teacher."""
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher '{teacher.name}' added successfully.")
            return redirect('admin_teachers')
    else:
        form = TeacherForm()

    return render(request, 'admin/teacher_form.html', {'form': form, 'title': 'Add Teacher'})


@admin_required
def teacher_edit_view(request, pk):
    """Admin edits a teacher."""
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f"Teacher '{teacher.name}' updated successfully.")
            return redirect('admin_teachers')
    else:
        form = TeacherForm(instance=teacher)

    return render(request, 'admin/teacher_form.html', {'form': form, 'title': 'Edit Teacher', 'teacher': teacher})


@admin_required
@require_POST
def teacher_delete_view(request, pk):
    """Admin deletes a teacher."""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher_name = teacher.name
    teacher.delete()
    messages.success(request, f"Teacher '{teacher_name}' deleted successfully.")
    return redirect('admin_teachers')


@admin_required
def feedback_list_view(request):
    """Admin Feedback Management view with all feedback, search, and filters."""
    search_query = request.GET.get('search', '').strip()
    selected_department = request.GET.get('department', '').strip()
    selected_teacher = request.GET.get('teacher', '').strip()

    feedback_qs = Feedback.objects.select_related('student', 'teacher').all()

    if search_query:
        feedback_qs = feedback_qs.filter(
            Q(student__name__icontains=search_query) |
            Q(student__roll_number__icontains=search_query) |
            Q(teacher__name__icontains=search_query)
        )

    if selected_department:
        feedback_qs = feedback_qs.filter(student__department__iexact=selected_department)

    if selected_teacher:
        feedback_qs = feedback_qs.filter(teacher__id=selected_teacher)

    feedbacks = feedback_qs.order_by('-created_at')
    departments = Student.objects.values_list('department', flat=True).distinct().order_by('department')
    teachers = Teacher.objects.all().order_by('name')

    context = {
        'feedbacks': feedbacks,
        'departments': departments,
        'teachers': teachers,
        'search_query': search_query,
        'selected_department': selected_department,
        'selected_teacher': selected_teacher,
    }
    return render(request, 'admin/feedback.html', context)


@admin_required
@require_POST
def feedback_delete_view(request, pk):
    """Delete a feedback entry."""
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    messages.success(request, "Feedback deleted successfully.")
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'admin_dashboard'
    return redirect(next_url)


# ==========================================
# STUDENT VIEWS
# ==========================================

@student_required
def student_feedback_submit_view(request):
    """Student feedback submission form with auto-filled, read-only details."""
    student = request.user.student_profile

    if request.method == 'POST':
        form = FeedbackSubmissionForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = student
            feedback.save()
            return redirect('student_feedback_success')
        else:
            messages.error(request, "Please fix the errors below to submit your feedback.")
    else:
        form = FeedbackSubmissionForm()

    context = {
        'student': student,
        'form': form,
    }
    return render(request, 'student/feedback_form.html', context)


@student_required
def student_feedback_success_view(request):
    """Success page after submitting feedback."""
    return render(request, 'student/success.html')


@student_required
def student_change_password_view(request):
    """Student change password view."""
    if request.method == 'POST':
        form = StudentPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('student_feedback_form')
    else:
        form = StudentPasswordChangeForm(request.user)

    return render(request, 'student/change_password.html', {'form': form})
