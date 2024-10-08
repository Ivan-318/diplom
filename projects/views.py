# projects/views.py
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Review, Category, Product
from .forms import ProjectForm, ReviewForm, ProductForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.views.generic import ListView, DetailView


def index(request):
    projects = Project.objects.all().order_by('-created_at')[:3]
    return render(request, 'index.html', {'projects': projects})


def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': projects})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(project=project, user=request.user)
        except Review.DoesNotExist:
            user_review = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Для голосования необходимо войти в систему.")
            return redirect('login')

        action = request.POST.get('action')

        if action == 'vote':
            if user_review:
                form = ReviewForm(request.POST, instance=user_review)
            else:
                form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.project = project
                review.user = request.user
                review.save()
                project.get_vote_count()
                if user_review:
                    messages.success(request, "Ваш голос был обновлён.")
                else:
                    messages.success(request, "Ваш голос был учтён.")
                return redirect('project_detail', pk=project.id)
        elif action == 'reset':
            if user_review:
                user_review.delete()
                project.get_vote_count()
                messages.success(request, "Ваш голос был сброшен.")
                return redirect('project_detail', pk=project.id)

    else:
        form = ReviewForm(instance=user_review)

    reviews = project.review_set.all()
    context = {
        'project': project,
        'form': form,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'project_detail.html', context)


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Проект успешно добавлен.")
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 4


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'


def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,  # Список товаров на текущей странице
        'is_paginated': page_obj.has_other_pages(),  # Проверка наличия других страниц
        'page_obj': page_obj,  # Объект страницы для пагинации
    }

    return render(request, 'product_list.html', context)