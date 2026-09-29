from django import forms
from django.forms import formset_factory


class AcademicSessionForm(forms.Form):
    academic_year = forms.RegexField(
        regex=r'^\d{4}/\d{4}$',
        max_length=9,
        error_messages={'invalid': 'Enter an academic year like 2025/2026.'},
        widget=forms.TextInput(attrs={'placeholder': '2025/2026'}),
    )
    term = forms.ChoiceField(choices=(
        ('first', 'First semester'),
        ('second', 'Second semester'),
        ('summer', 'Summer semester'),
    ))

    def clean_academic_year(self):
        academic_year = self.cleaned_data['academic_year']
        start, end = map(int, academic_year.split('/'))
        if end != start + 1:
            raise forms.ValidationError('The end year must follow the start year.')
        return academic_year


class CourseForm(forms.Form):
    code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. COS 201'}))
    title = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'placeholder': 'Course title'}))
    credit_units = forms.IntegerField(min_value=1, max_value=6, widget=forms.NumberInput(attrs={'min': 1, 'max': 6}))
    score = forms.IntegerField(min_value=0, max_value=100, widget=forms.NumberInput(attrs={'min': 0, 'max': 100}))


CourseFormSet = formset_factory(CourseForm, extra=3, min_num=1, validate_min=True, max_num=30, validate_max=True)