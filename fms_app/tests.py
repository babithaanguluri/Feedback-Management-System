from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from fms_app.models import Student, Teacher, Feedback

class FMSSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            password='adminpassword',
            email='admin@test.com'
        )

        # Teacher
        self.teacher = Teacher.objects.create(
            name='Shiva',
            department='MECH',
            email='shiva@test.com',
            phone='1234567890'
        )

        # Student User & Profile
        self.student_user = User.objects.create_user(
            username='Rahul',
            password='23CS101',
            email='rahul@test.com'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            name='Rahul',
            roll_number='23CS101',
            department='MECH',
            email='rahul@test.com',
            phone='987456123',
            address='Vijayawada'
        )

    def test_access_control_unauthenticated(self):
        """Unauthenticated requests to admin dashboard redirect to admin login."""
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_login'), response.url)

        # Unauthenticated request to student form redirects to student login
        response = self.client.get(reverse('student_feedback_form'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('student_login'), response.url)

    def test_student_cannot_access_admin_dashboard(self):
        """Logged-in student cannot access admin pages."""
        self.client.login(username='Rahul', password='23CS101')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('student_feedback_form'))

    def test_admin_dashboard_counts(self):
        """Admin dashboard displays accurate counts."""
        self.client.login(username='admin_test', password='adminpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_students'], 1)
        self.assertEqual(response.context['total_teachers'], 1)
        self.assertEqual(response.context['total_feedback'], 0)

    def test_admin_add_student_auto_credentials(self):
        """Admin adding a student automatically creates User account with Name and Roll No."""
        self.client.login(username='admin_test', password='adminpassword')
        response = self.client.post(reverse('student_add'), {
            'name': 'Priya',
            'roll_number': '23CS102',
            'department': 'CSE',
            'email': 'priya@test.com',
            'phone': '9876543210',
            'address': 'Guntur'
        })
        self.assertEqual(response.status_code, 302)

        # Verify Student exists
        student = Student.objects.get(roll_number='23CS102')
        self.assertEqual(student.name, 'Priya')

        # Verify User credentials
        user = User.objects.get(username='Priya')
        self.assertTrue(user.check_password('23CS102'))

        # Verify student can login
        client2 = Client()
        login_success = client2.login(username='Priya', password='23CS102')
        self.assertTrue(login_success)

    def test_student_delete_cascades_user(self):
        """Deleting a student deletes the associated user account."""
        self.client.login(username='admin_test', password='adminpassword')
        student_id = self.student.id
        user_id = self.student.user.id

        response = self.client.post(reverse('student_delete', kwargs={'pk': student_id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Student.objects.filter(id=student_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_student_feedback_submission(self):
        """Student submits feedback and it is saved with correct student details."""
        self.client.login(username='Rahul', password='23CS101')
        response = self.client.post(reverse('student_feedback_form'), {
            'teacher': self.teacher.id,
            'rating': 5,
            'description': 'Excellent professor, very interactive classes!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('student_feedback_success'), response.url)

        # Check DB
        feedback = Feedback.objects.filter(student=self.student, teacher=self.teacher).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.description, 'Excellent professor, very interactive classes!')

    def test_feedback_filter_and_delete(self):
        """Admin can search/filter feedback and delete an entry."""
        # Create a feedback entry
        feedback = Feedback.objects.create(
            student=self.student,
            teacher=self.teacher,
            rating=4,
            description="Good experience."
        )

        self.client.login(username='admin_test', password='adminpassword')

        # Search by student name
        response = self.client.get(reverse('admin_dashboard') + '?search=Rahul')
        self.assertEqual(response.status_code, 200)
        self.assertIn(feedback, response.context['recent_feedback'])

        # Search by nonexistent teacher
        response = self.client.get(reverse('admin_dashboard') + '?search=NonExistent')
        self.assertEqual(len(response.context['recent_feedback']), 0)

        # Delete feedback
        del_response = self.client.post(reverse('feedback_delete', kwargs={'pk': feedback.id}))
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(Feedback.objects.filter(id=feedback.id).exists())
