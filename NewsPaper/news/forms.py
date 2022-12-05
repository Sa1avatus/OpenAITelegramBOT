from django import forms
from .models import Post, Author, Category
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm, UserForm
from django.contrib.auth.models import User, Group


class PostForm(forms.ModelForm):
    description = models.TextField()
    title = models.CharField(max_length=255)
    author = forms.ModelChoiceField(queryset=Author.objects.all())
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
    class Meta:
        model = Post
        fields = ['author', 'title', 'description', 'category']

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("description")
        title = cleaned_data.get("title")
        if description is not None and len(description) < 20:
            raise ValidationError({
                "description": "Описание не может быть менее 20 символов."
            })

        if len(title) > 255:
            raise ValidationError(
                "Наименование не может быть больше 255 символов."
            )
        return cleaned_data


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user


class BaseProfileForm(UserForm):
    def __str__(self):
        return super().user()

