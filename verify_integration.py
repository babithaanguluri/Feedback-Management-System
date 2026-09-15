import urllib.request
import urllib.parse
import http.cookiejar
import re

BASE = 'http://127.0.0.1:8000'
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

def get_csrf(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = opener.open(req)
    html = res.read().decode('utf-8')
    for cookie in cookie_jar:
        if cookie.name == 'csrftoken':
            return cookie.value, html
    return None, html

print("=== 1. Testing Admin Login ===")
csrf, html = get_csrf(f"{BASE}/admin-login/")
login_payload = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf,
    'username': 'admin',
    'password': 'admin123'
}).encode('utf-8')

req = urllib.request.Request(f"{BASE}/admin-login/", data=login_payload, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': f"{BASE}/admin-login/"
})
res = opener.open(req)
print(f"Admin login -> Status: {res.status}, URL: {res.geturl()}")
assert "/dashboard/" in res.geturl(), "Admin did not land on /dashboard/"

print("=== 2. Testing Admin Dashboard Metrics & Visuals ===")
dash_html = res.read().decode('utf-8')
assert "Admin Dashboard" in dash_html
assert "Total Students" in dash_html
assert "Total Teachers" in dash_html
assert "Total Feedback" in dash_html
assert "Recent Feedback" in dash_html
assert "Rahul" in dash_html
assert "Shiva" in dash_html
print("Dashboard metrics and recent feedback verified successfully!")

print("=== 3. Testing Filters on Dashboard ===")
req = urllib.request.Request(f"{BASE}/dashboard/?department=MECH", headers={'User-Agent': 'Mozilla/5.0'})
res = opener.open(req)
filter_html = res.read().decode('utf-8')
assert "Rahul" in filter_html
assert "Priya" not in filter_html
print("Department filter working correctly!")

print("=== 4. Testing Student Management Table ===")
req = urllib.request.Request(f"{BASE}/students/", headers={'User-Agent': 'Mozilla/5.0'})
res = opener.open(req)
students_html = res.read().decode('utf-8')
assert "Student Management" in students_html
assert "23CS101" in students_html
assert "23CS102" in students_html
assert "23CS103" in students_html
print("Student list verified successfully!")

print("=== 5. Adding New Student (Auto-Credentials) ===")
csrf, _ = get_csrf(f"{BASE}/students/add/")
import time
ts = int(time.time()) % 10000
test_student_name = f"TestStudent{ts}"
test_student_roll = f"24CS{ts}"

new_student_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf,
    'name': test_student_name,
    'roll_number': test_student_roll,
    'department': 'CSE',
    'email': f'{test_student_name.lower()}@test.com',
    'phone': '9876543299',
    'address': 'Hyderabad'
}).encode('utf-8')

req = urllib.request.Request(f"{BASE}/students/add/", data=new_student_data, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': f"{BASE}/students/add/"
})
res = opener.open(req)
print(f"Student '{test_student_name}' added successfully!")

print("=== 6. Admin Logout ===")
opener.open(urllib.request.Request(f"{BASE}/logout/"))

print("=== 7. Student Login with Auto-Generated Credentials ===")
student_cookie_jar = http.cookiejar.CookieJar()
student_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(student_cookie_jar))

def get_student_csrf(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = student_opener.open(req)
    html = res.read().decode('utf-8')
    for cookie in student_cookie_jar:
        if cookie.name == 'csrftoken':
            return cookie.value, html
    return None, html

s_csrf, _ = get_student_csrf(f"{BASE}/student-login/")
s_login_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': s_csrf,
    'username': test_student_name,
    'password': test_student_roll
}).encode('utf-8')

req = urllib.request.Request(f"{BASE}/student-login/", data=s_login_data, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': f"{BASE}/student-login/"
})
res = student_opener.open(req)
print(f"Student login -> Status: {res.status}, URL: {res.geturl()}")
assert "/feedback/submit/" in res.geturl(), "Student was not redirected to /feedback/submit/"

print("=== 8. Checking Readonly Auto-filled Fields ===")
form_html = res.read().decode('utf-8')
assert test_student_roll in form_html, "Roll number not auto-filled"
assert test_student_name in form_html, "Name not auto-filled"
assert "CSE" in form_html, "Department not auto-filled"
assert "form-control-readonly" in form_html
print("Readonly auto-filled fields verified!")

print("=== 9. Submitting Feedback ===")
match = re.search(r'value="(\d+)">[^<]*Shiva', form_html)
teacher_id = match.group(1) if match else '1'

for cookie in student_cookie_jar:
    if cookie.name == 'csrftoken':
        fb_csrf = cookie.value
        break

fb_payload = urllib.parse.urlencode({
    'csrfmiddlewaretoken': fb_csrf,
    'teacher': teacher_id,
    'rating': '5',
    'description': 'Fantastic explanations and practical examples.'
}).encode('utf-8')

req = urllib.request.Request(f"{BASE}/feedback/submit/", data=fb_payload, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': f"{BASE}/feedback/submit/"
})
res = student_opener.open(req)
success_html = res.read().decode('utf-8')
print(f"Feedback submission -> Status: {res.status}, URL: {res.geturl()}")
assert "/feedback/success/" in res.geturl(), "Did not redirect to success page"
assert "Thank you for submitting your feedback!" in success_html
print("Success message verified!")

print("\n========================================================")
print("ALL LIVE INTEGRATION TESTS PASSED 100% SUCCESSFULLY!")
print("========================================================")
