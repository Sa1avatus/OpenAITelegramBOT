import django_filters
from django.db import models
from .models import Post


class PostFilter(django_filters.FilterSet):
    #creation = django_filters.NumberFilter(field_name='creation', lookup_expr='year')
    creation__gt = django_filters.DateTimeFilter(field_name='creation', lookup_expr='year')
    #rating = django_filters.NumberFilter()
    rating__gt = django_filters.NumberFilter(field_name='rating', lookup_expr='gt')

    class Meta:
        model = Post
        fields = ['title', 'creation', 'rating']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            models.BooleanField: {
                'filter_class': django_filters.BooleanFilter,
                'extra': lambda f: {
                    'widget': forms.CheckboxInput,
                },
            },
        }



