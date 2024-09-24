from django.db import models
from django.urls import reverse
from django.utils import timezone


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание проекта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # Заглушка для связи с устройствами в будущем
    # devices = models.ManyToManyField('Device', related_name='projects', blank=True, verbose_name="Устройства")

    # Заглушки для будущих функций
    # votes = models.ManyToManyField(User, through='Vote', related_name='voted_projects')
    # comments = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='project_comments')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[str(self.id)])

# заглушка для модели Vote
# class Vote(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

# аглушка для модели Comment
# class Comment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
