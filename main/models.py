from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    matric_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    def __str__(self):
        return self.matric_number or self.username


class AcademicSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='academic_sessions')
    academic_year = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['academic_year']
        constraints = [
            models.UniqueConstraint(fields=['user', 'academic_year'], name='unique_user_academic_year'),
        ]

    def __str__(self):
        return self.academic_year


class Semester(models.Model):
    FIRST = 'first'
    SECOND = 'second'
    SUMMER = 'summer'
    TERM_CHOICES = [
        (FIRST, 'First semester'),
        (SECOND, 'Second semester'),
        (SUMMER, 'Summer semester'),
    ]

    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='semesters')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['term']
        constraints = [
            models.UniqueConstraint(fields=['session', 'term'], name='unique_session_semester_term'),
        ]

    def __str__(self):
        return f'{self.session.academic_year} - {self.get_term_display()}'


class Course(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=120)
    credit_units = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['code', 'title']
        constraints = [
            models.CheckConstraint(condition=models.Q(credit_units__gte=1, credit_units__lte=6), name='course_credit_units_1_to_6'),
            models.CheckConstraint(condition=models.Q(score__lte=100), name='course_score_0_to_100'),
        ]

    def __str__(self):
        return f'{self.code or self.title} ({self.semester})'