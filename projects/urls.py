from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('signup/', views.signup, name='signup'),
]
