from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('cgpa/', views.cgpa_calculator_view, name='cgpa_calculator'),
    path('signup/', views.signup_view, name='signup'),
]