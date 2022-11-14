import django_filters
from django import forms
from django_filters import ModelChoiceFilter, DateTimeFilter, NumberFilter, IsoDateTimeFilter
from django.db import models
from .models import Post, Author


class PostFilter(django_filters.FilterSet):
    rating = NumberFilter(field_name='rating', lookup_expr='gt')
    creation = DateTimeFilter(field_name='creation',
                                           widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                                           lookup_expr='gt', label='creation')

    class Meta:
        model = Post
        fields = {
            'author__user': ['exact'],
            'title': ['icontains'],
        }



