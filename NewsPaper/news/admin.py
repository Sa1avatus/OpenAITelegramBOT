from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Author)
# Register your models here.
