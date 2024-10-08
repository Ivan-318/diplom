from django.contrib import admin
from .models import Project, Review, Category, Product

admin.site.register(Project)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Product)