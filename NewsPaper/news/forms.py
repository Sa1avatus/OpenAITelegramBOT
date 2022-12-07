from django import forms
from django.forms import HiddenInput
from django.template.loader import render_to_string
from .models import Post, Author, Category
from django.db import models
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm, UserForm
from django.contrib.auth.models import Group
from .tasks import new_post_notification
from .triggers import send_notification


class PostForm(forms.ModelForm):
    description = models.TextField()
    title = models.CharField(max_length=255)
    #author = forms.ModelChoiceField(queryset=Author.objects.all())
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = ['author', 'type', 'title', 'description', 'category']
        widgets = {
            'author': HiddenInput(),
            'type': HiddenInput(),
        }

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


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        html_content = render_to_string(
            'notifications/greetings_new_user.html',
        )
        subject = 'Добро пожаловать на портал!'
        send_notification(html_content, user.email, subject)
        return user


class BaseProfileForm(UserForm):
    def __str__(self):
        return super().user()

