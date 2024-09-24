from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm


def index(request):
    # Отображаем последние 3 проекта на главной странице
    projects = Project.objects.all().order_by('-created_at')[:3]
    return render(request, 'index.html', {'projects': projects})


def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': projects})


def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})
