from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count, Min, Sum

POST_TYPE = (('1', 'статья'), ('2', 'новость'))


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING) # cвязь «один к одному» с встроенной моделью пользователей User;
    rating = models.IntegerField(default=0) # рейтинг пользователя.

    def update_rating(self):
        if Post.objects.all().exists():
            cnt1 = Post.objects.filter(author=self).aggregate(rate_sum=Sum('rating')).get('rate_sum') * 3
            cnt2 = Comment.objects.filter(author=self).aggregate(rate_sum=Sum('rating')).get('rate_sum')
            cnt3 = Comment.objects.filter(post__in=Post.objects.filter(author=self)).aggregate(rate_sum=Sum('rating')).get('rate_sum')
            self.rating = cnt1 + cnt2 + cnt3
            self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True) # Категории новостей/статей — темы, которые они отражают


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Author;
    type = models.CharField(max_length=9, choices=POST_TYPE) # поле с выбором — «статья» или «новость»;
    creation = models.DateTimeField(auto_now_add=True) # автоматически добавляемая дата и время создания;
    category = models.ManyToManyField(Category, through='PostCategory') # связь «многие ко многим» с моделью Category;
    title = models.CharField(max_length=255, null=False) # заголовок статьи/новости;
    description = models.TextField(null=False) # текст статьи/новости;
    rating = models.IntegerField(default=0) # рейтинг статьи/новости.

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.description[0:124]}...'

    def __str__(self):
        return f'{self.title}:\n {self.description[:124]}...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Post;
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Category.


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Post;
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING) # связь «один ко многим» со встроенной моделью User (комментарии может оставить любой пользователь, необязательно автор);
    text = models.TextField(null=False) # текст комментария;
    creation = models.DateTimeField(auto_now_add=True) # дата и время создания комментария;
    rating = models.IntegerField(default=0) # рейтинг комментария.

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.text}'