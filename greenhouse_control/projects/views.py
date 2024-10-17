from django.core.paginator import Paginator
from .models import Project, Review
from .forms import ProjectForm, ReviewForm, SignUpForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem, Category
from .forms import OrderCreateForm
from .utils import ProductDetailView, ProductListView, Cart
from django.contrib import messages


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


# Корзина: просмотр
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart_detail.html', {'cart': cart})


# Корзина: добавление товара
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product_id=product.id, quantity=quantity)
    messages.success(request, f"Добавлено {quantity} x {product.name} в корзину.")
    return redirect('cart_detail')


# Корзина: удаление товара
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product_id=product.id)
    messages.success(request, f"Удалено {product.name} из корзины.")
    return redirect('cart_detail')


# Оформление заказа
@login_required
def order_create(request):
    cart = Cart(request)
    if not cart.cart:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Создание заказа
            order = Order.objects.create(
                user=request.user,
                status='new',
                total_price=cart.get_total_price()
            )
            # Создание элементов заказа
            for item in cart.get_cart_items():
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )
            # Обновление общей цены заказа
            order.update_total_price()
            # Очистка корзины
            cart.clear()
            messages.success(request, "Ваш заказ успешно оформлен!")
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'order_create.html', {'cart': cart, 'form': form})


# Детали заказа
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


# Просмотр истории заказов
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category).order_by('-id')

    paginator = Paginator(products, 6)  # Показывать по 6 товаров на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'products': page_obj,  # Используем page_obj для пагинации
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'products_by_category.html', context)

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
