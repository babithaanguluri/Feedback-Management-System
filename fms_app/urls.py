from django.urls import path
from . import views

urlpatterns = [
    # Universal / Auth
    path('', views.index_redirect, name='index'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('student-login/', views.student_login_view, name='student_login'),
    path('login/', views.student_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin Dashboard & Feedback
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('feedback/', views.feedback_list_view, name='admin_feedback'),
    path('feedback/delete/<int:pk>/', views.feedback_delete_view, name='feedback_delete'),

    # Admin Students
    path('students/', views.students_list_view, name='admin_students'),
    path('students/add/', views.student_add_view, name='student_add'),
    path('students/edit/<int:pk>/', views.student_edit_view, name='student_edit'),
    path('students/delete/<int:pk>/', views.student_delete_view, name='student_delete'),

    # Admin Teachers
    path('teachers/', views.teachers_list_view, name='admin_teachers'),
    path('teachers/add/', views.teacher_add_view, name='teacher_add'),
    path('teachers/edit/<int:pk>/', views.teacher_edit_view, name='teacher_edit'),
    path('teachers/delete/<int:pk>/', views.teacher_delete_view, name='teacher_delete'),

    # Student Portal
    path('feedback/submit/', views.student_feedback_submit_view, name='student_feedback_form'),
    path('feedback/success/', views.student_feedback_success_view, name='student_feedback_success'),
    path('change-password/', views.student_change_password_view, name='student_change_password'),
]
