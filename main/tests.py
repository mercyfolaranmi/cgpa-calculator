from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Course, Semester


class CgpaCalculatorTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='student-1', matric_number='student-1', password='StrongTestPass123!'
		)
		self.client.login(username='student-1', password='StrongTestPass123!')

	def save_semester(self, year, term, code, title, units, score):
		return self.client.post('/cgpa/', {
			'academic_year': year,
			'term': term,
			'courses-TOTAL_FORMS': '3',
			'courses-INITIAL_FORMS': '0',
			'courses-MIN_NUM_FORMS': '1',
			'courses-MAX_NUM_FORMS': '30',
			'courses-0-code': code,
			'courses-0-title': title,
			'courses-0-credit_units': str(units),
			'courses-0-score': str(score),
		}, follow=True)

	def test_results_are_saved_and_cgpa_combines_sessions_by_credit_weight(self):
		self.save_semester('2024/2025', 'first', 'COS 101', 'Programming', 3, 80)
		response = self.save_semester('2025/2026', 'second', 'COS 201', 'Data structures', 1, 60)

		self.assertEqual(Semester.objects.count(), 2)
		self.assertEqual(Course.objects.count(), 2)
		self.assertContains(response, '4.75')

	def test_blank_extra_course_rows_are_ignored(self):
		self.save_semester('2024/2025', 'first', 'COS 101', 'Programming', 3, 80)

		self.assertEqual(Course.objects.count(), 1)

	def test_course_can_have_zero_credit_units(self):
		response = self.save_semester('2024/2025', 'first', 'COS 100', 'Zero-unit course', 0, 85)

		course = Course.objects.get(code='COS 100')
		self.assertEqual(course.credit_units, 0)
		self.assertContains(response, '0 total credit units')

	def test_semester_accepts_more_than_three_courses(self):
		data = {
			'academic_year': '2024/2025',
			'term': 'first',
			'courses-TOTAL_FORMS': '4',
			'courses-INITIAL_FORMS': '0',
			'courses-MIN_NUM_FORMS': '1',
			'courses-MAX_NUM_FORMS': '30',
		}
		for index in range(4):
			data.update({
				f'courses-{index}-code': f'COS 10{index}',
				f'courses-{index}-title': f'Course {index}',
				f'courses-{index}-credit_units': '3',
				f'courses-{index}-score': '70',
			})

		self.client.post('/cgpa/', data)

		self.assertEqual(Course.objects.count(), 4)

	def test_student_cannot_view_another_students_results(self):
		self.save_semester('2024/2025', 'first', 'COS 101', 'Private course', 3, 80)
		self.client.logout()
		get_user_model().objects.create_user(username='student-2', password='StrongTestPass123!')
		self.client.login(username='student-2', password='StrongTestPass123!')

		response = self.client.get('/cgpa/')

		self.assertNotContains(response, 'Private course')

	def test_signup_saves_full_name_and_displays_name_and_matric_number(self):
		response = self.client.post('/signup/', {
			'full_name': '  Mercy   Folaranmi  ',
			'matric': 'REG/2026/001',
			'password': 'StrongTestPass123!',
			'confirm_password': 'StrongTestPass123!',
		})

		self.assertRedirects(response, '/')
		student = get_user_model().objects.get(username='REG/2026/001')
		self.assertEqual(student.get_full_name(), 'Mercy Folaranmi')
		self.assertEqual(student.matric_number, 'REG/2026/001')

		self.client.login(username='REG/2026/001', password='StrongTestPass123!')
		record = self.client.get('/cgpa/')
		self.assertContains(record, 'Mercy Folaranmi')
		self.assertContains(record, 'REG/2026/001')

	def test_another_student_can_sign_up_and_log_in(self):
		response = self.client.post('/signup/', {
			'full_name': 'Student Two',
			'matric': 'REG/2026/002',
			'password': 'StrongTestPass123!',
			'confirm_password': 'StrongTestPass123!',
		})

		self.assertRedirects(response, '/')
		student = get_user_model().objects.get(matric_number='REG/2026/002')
		self.client.logout()
		response = self.client.post('/', {
			'matric': 'REG/2026/002',
			'password': 'StrongTestPass123!',
		})

		self.assertRedirects(response, '/cgpa/')
		self.assertEqual(self.client.session['_auth_user_id'], str(student.pk))

	def test_login_uses_matric_number_when_it_differs_from_username(self):
		student = get_user_model().objects.create_user(
			username='student-account',
			matric_number='REG/2026/003',
			password='StrongTestPass123!',
		)
		self.client.logout()

		response = self.client.post('/', {
			'matric': 'REG/2026/003',
			'password': 'StrongTestPass123!',
		})

		self.assertRedirects(response, '/cgpa/')
		self.assertEqual(self.client.session['_auth_user_id'], str(student.pk))
