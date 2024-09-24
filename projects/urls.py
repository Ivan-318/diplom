from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
]