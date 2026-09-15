from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, Teacher, Feedback

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'department', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rahul'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 23CS101'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CSE or MECH'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. student@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9876543210'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Student name is required.")
        return name

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number', '').strip()
        if not roll_number:
            raise ValidationError("Roll number is required.")
        
        # Check uniqueness across students
        qs = Student.objects.filter(roll_number__iexact=roll_number)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A student with this Roll Number already exists.")
        return roll_number

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        if name:
            # Check User model username conflict if new or name changed
            qs = User.objects.filter(username__iexact=name)
            if self.instance and self.instance.pk and hasattr(self.instance, 'user') and self.instance.user:
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                self.add_error('name', f"A user account with username '{name}' already exists. Please use a distinctive name/initial.")
        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)
        name = self.cleaned_data['name']
        roll_number = self.cleaned_data['roll_number']
        email = self.cleaned_data.get('email', '')

        if not student.pk or not hasattr(student, 'user') or not student.user:
            # Creating new student and user credentials
            # Username = Name, Password = Roll Number
            user = User.objects.create_user(
                username=name,
                email=email,
                password=roll_number
            )
            student.user = user
        else:
            # Updating existing user credentials
            user = student.user
            if user.username != name:
                user.username = name
            user.email = email
            user.save()

        if commit:
            student.save()
        return student


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'department', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Shiva or Mr. Kumar'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MECH or CSE'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. teacher@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9876543210'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Teacher name is required.")
        return name

    def clean_department(self):
        department = self.cleaned_data.get('department', '').strip()
        if not department:
            raise ValidationError("Department is required.")
        return department


class FeedbackSubmissionForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.HiddenInput(attrs={'id': 'rating-value'}),
        error_messages={
            'required': 'Please select a rating between 1 and 5 stars.',
            'min_value': 'Rating must be at least 1 star.',
            'max_value': 'Rating cannot exceed 5 stars.'
        }
    )

    class Meta:
        model = Feedback
        fields = ['teacher', 'rating', 'description']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-select', 'id': 'select-teacher'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your feedback here (e.g. Nice Teaching, explains concepts clearly...)',
                'id': 'rating-description'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].empty_label = "Select Teacher"
        self.fields['teacher'].queryset = Teacher.objects.all().order_by('name')
        self.fields['description'].required = True


class StudentPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'})
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', "New passwords do not match.")
        return cleaned_data
