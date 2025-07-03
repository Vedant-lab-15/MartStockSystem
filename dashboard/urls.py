from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('reports/', views.dashboard_reports, name='reports'),
    path('preferences/', views.update_preferences, name='preferences'),
]