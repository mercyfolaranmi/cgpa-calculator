from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import AcademicSession, Course, Semester, User


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0


class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 0

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Matric Info', {'fields': ('matric_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Matric Info', {'fields': ('matric_number',)}),
    )
    list_display = ['username', 'matric_number', 'email', 'first_name', 'last_name', 'is_staff']


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'user', 'created_at']
    search_fields = ['academic_year', 'user__username', 'user__matric_number']
    inlines = [SemesterInline]


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['session', 'term', 'created_at']
    list_filter = ['term', 'session__academic_year']
    inlines = [CourseInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'semester', 'credit_units', 'score']
    search_fields = ['code', 'title', 'semester__session__user__username']