from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fms_app.models import Student, Teacher, Feedback
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds initial sample data matching the reference screenshots'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding...")

        # 1. Create Superuser (Admin)
        admin_user, created = User.objects.get_or_create(username='admin')
        if created or not admin_user.is_superuser:
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.email = 'admin@college.edu'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'admin123'."))
        else:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' password set to 'admin123'."))

        # 2. Create Teachers matching screenshots
        teachers_data = [
            {'name': 'Shiva', 'department': 'MECH', 'email': 'shiva.mech@college.edu', 'phone': '9876543211'},
            {'name': 'Mr. Kumar', 'department': 'CSE', 'email': 'kumar.cse@college.edu', 'phone': '9876543212'},
            {'name': 'Dr. Ramesh', 'department': 'ECE', 'email': 'ramesh.ece@college.edu', 'phone': '9876543213'},
            {'name': 'Mrs. Sunitha', 'department': 'IT', 'email': 'sunitha.it@college.edu', 'phone': '9876543214'},
        ]
        created_teachers = {}
        for t_info in teachers_data:
            teacher, t_created = Teacher.objects.get_or_create(
                name=t_info['name'],
                defaults={
                    'department': t_info['department'],
                    'email': t_info['email'],
                    'phone': t_info['phone']
                }
            )
            created_teachers[teacher.name] = teacher
            if t_created:
                self.stdout.write(f"Teacher '{teacher.name}' created.")

        # 3. Create Students matching screenshots
        students_data = [
            {
                'name': 'Rahul',
                'roll_number': '23CS101',
                'department': 'MECH',
                'email': 'rahul.sharma@gmail.com',
                'phone': '987456123',
                'address': 'Vijayawada, Andhra Pradesh'
            },
            {
                'name': 'Priya',
                'roll_number': '23CS102',
                'department': 'CSE',
                'email': 'priya@gmail.com',
                'phone': '9492309658',
                'address': 'Guntur, Andhra Pradesh'
            },
            {
                'name': 'Arjun Kumar',
                'roll_number': '23CS103',
                'department': 'CSE',
                'email': 'arjunkumar@gmail.com',
                'phone': '9000000001',
                'address': 'Visakhapatnam, Andhra Pradesh'
            },
        ]

        created_students = {}
        for s_info in students_data:
            user, u_created = User.objects.get_or_create(username=s_info['name'])
            user.set_password(s_info['roll_number'])
            user.email = s_info['email']
            user.save()

            student, s_created = Student.objects.get_or_create(
                roll_number=s_info['roll_number'],
                defaults={
                    'user': user,
                    'name': s_info['name'],
                    'department': s_info['department'],
                    'email': s_info['email'],
                    'phone': s_info['phone'],
                    'address': s_info['address'],
                }
            )
            created_students[student.name] = student
            if s_created:
                self.stdout.write(f"Student '{student.name}' created with login: Username='{student.name}', Password='{student.roll_number}'.")

        # 4. Create Feedback matching Screenshot 1
        # Screenshot 1 shows:
        # Student: Rahul | Teacher: Shiva | Rating: 4 stars | Date: 10 Sep 2026 14:59
        # Student: Priya | Teacher: Mr. Kumar | Rating: 4 stars | Date: 09 Sep 2026 20:36
        if not Feedback.objects.exists():
            if 'Rahul' in created_students and 'Shiva' in created_teachers:
                Feedback.objects.create(
                    student=created_students['Rahul'],
                    teacher=created_teachers['Shiva'],
                    rating=4,
                    description="Nice Teaching. Explains concepts clearly with practical examples.",
                )
                self.stdout.write("Created feedback from Rahul for Shiva.")

            if 'Priya' in created_students and 'Mr. Kumar' in created_teachers:
                Feedback.objects.create(
                    student=created_students['Priya'],
                    teacher=created_teachers['Mr. Kumar'],
                    rating=4,
                    description="Teacher explains concepts clearly and is always available for doubts.",
                )
                self.stdout.write("Created feedback from Priya for Mr. Kumar.")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
