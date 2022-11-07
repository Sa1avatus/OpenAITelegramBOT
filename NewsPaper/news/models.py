from django.contrib.auth.models import User
from django.db import models

POST_TYPE = (('1', 'статья'), ('2', 'новость'))


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING) # cвязь «один к одному» с встроенной моделью пользователей User;
    rating = models.IntegerField(default=0) # рейтинг пользователя.

    def update_rating(self, cnt):
        self.save()
    # Метод update_rating() модели Author, который обновляет рейтинг пользователя, переданный в аргумент этого метода.
    # Он состоит из следующего:
    # суммарный рейтинг каждой статьи автора умножается на 3;
    # суммарный рейтинг всех комментариев автора;
    # суммарный рейтинг всех комментариев к статьям автора.

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


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Post;
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Category.


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING) # связь «один ко многим» с моделью Post;
    user = models.ForeignKey(Author, on_delete=models.DO_NOTHING) # связь «один ко многим» со встроенной моделью User (комментарии может оставить любой пользователь, необязательно автор);
    text = models.TextField(null=False) # текст комментария;
    creation = models.DateTimeField(auto_now_add=True) # дата и время создания комментария;
    rating = models.IntegerField(default=0) # рейтинг комментария.

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()