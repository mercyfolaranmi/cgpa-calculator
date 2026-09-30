from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect
from .forms import AcademicSessionForm, CourseFormSet
from .cgpa_utils import calculate_gpa
from .models import Course

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        matric = request.POST.get('matric', '').strip()
        password = request.POST.get('password', '')
        account = User.objects.filter(matric_number=matric).first()
        username = account.username if account else matric
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('cgpa_calculator')
        messages.error(request, 'Invalid matric number or password.')
    return render(request, 'index.html')

@login_required
def dashboard_view(request):
    return redirect('cgpa_calculator')

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        full_name = ' '.join(request.POST.get('full_name', '').split())
        matric = request.POST.get('matric', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not full_name or len(full_name) > 300:
            messages.error(request, 'Enter your full name (up to 300 characters).')
            return redirect('signup')
        if not matric:
            messages.error(request, 'Enter your matric number.')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        try:
            validate_password(password)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)
            return redirect('signup')
        
        if User.objects.filter(username=matric).exists() or User.objects.filter(matric_number=matric).exists():
            messages.error(request, 'Matric number already registered.')
            return redirect('signup')
        
        first_name, _, last_name = full_name.partition(' ')
        user = User.objects.create_user(
            username=matric,
            matric_number=matric,
            first_name=first_name[:150],
            last_name=last_name[:150],
            password=password,
        )

        messages.success(request, 'Account created! Please log in.')
        return redirect('login')
    
    return render(request, 'account/signup.html')

def download_cgpa_pdf(request):
    return redirect('cgpa_calculator')


@login_required
def cgpa_calculator_view(request):
    session_form = AcademicSessionForm(request.POST or None)
    course_formset = CourseFormSet(request.POST or None, prefix='courses')

    if request.method == 'POST' and session_form.is_valid() and course_formset.is_valid():
        academic_year = session_form.cleaned_data['academic_year']
        term = session_form.cleaned_data['term']
        academic_session = request.user.academic_sessions.filter(academic_year=academic_year).first()
        if academic_session and academic_session.semesters.filter(term=term).exists():
            session_form.add_error('term', 'A result for this semester already exists. Choose another semester or academic year.')
        else:
            with transaction.atomic():
                academic_session, _ = request.user.academic_sessions.get_or_create(academic_year=academic_year)
                semester = academic_session.semesters.create(term=term)
                for course_form in course_formset:
                    if not course_form.has_changed():
                        continue
                    course = course_form.cleaned_data
                    Course.objects.create(
                        semester=semester,
                        code=course['code'].strip().upper(),
                        title=course['title'].strip(),
                        credit_units=course['credit_units'],
                        score=course['score'],
                    )
                messages.success(request, 'Semester results saved.')
                return redirect('cgpa_calculator')

    semesters = request.user.academic_sessions.prefetch_related('semesters__courses').all()
    semester_results = []
    all_courses = []
    for academic_session in semesters:
        for semester in academic_session.semesters.all():
            courses = list(semester.courses.all())
            result = calculate_gpa([
                {'code': course.code, 'name': course.title, 'credit_unit': course.credit_units, 'score': course.score}
                for course in courses
            ])
            semester_results.append({'semester': semester, 'result': result})
            all_courses.extend(
                {'code': course.code, 'name': course.title, 'credit_unit': course.credit_units, 'score': course.score}
                for course in courses
            )

    context = {
        'session_form': session_form,
        'course_formset': course_formset,
        'semester_results': semester_results,
        'cgpa': calculate_gpa(all_courses),
        'has_results': bool(all_courses),
    }
    return render(request, 'account/cgpa_form.html', context)