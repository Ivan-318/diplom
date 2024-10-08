from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(verbose_name="Описание категории", blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание товара")
    image = models.ImageField(upload_to="products/%Y/%m/%d", verbose_name="Изображение товара")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products",
                                 verbose_name="Категория")

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание проекта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    featured_image = models.ImageField(default="default.jpg", upload_to="projects/%Y/%m/%d",
                                       verbose_name="Изображение проекта")
    vote_total = models.IntegerField(default=0, blank=True, verbose_name="Общее количество голосов")
    vote_ratio = models.IntegerField(default=0, blank=True, verbose_name="Соотношение голосов")
    products = models.ManyToManyField(Product, related_name='projects', blank=True, verbose_name="Товары")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[str(self.id)])

    def get_vote_count(self):
        reviews = self.review_set.all()
        up_votes = reviews.filter(value='up').count()
        total_votes = reviews.count()

        if total_votes > 0:
            ratio = (up_votes / total_votes) * 100
        else:
            ratio = 0
        self.vote_total = total_votes
        self.vote_ratio = ratio
        self.save()


class Review(models.Model):
    VOTE_TYPE = (
        ('up', 'За'),
        ('down', 'Против'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    value = models.CharField(max_length=10, choices=VOTE_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')  # Один пользователь может голосовать только один раз за проект

    def __str__(self):
        return f"{self.user.username} - {self.value} - {self.project.title}"
