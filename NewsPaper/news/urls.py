from django.urls import path
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    path('', (PostList.as_view()), name='post_list'),
    path('news/', (PostList.as_view()), name='post_list'),
    path('news/search/', PostSearch.as_view(), name='post_search'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('news/<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('news/create/', PostCreate.as_view(), name='post_create'),
    path('article/create/', PostCreate.as_view(), name='post_create'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
    path('article/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('article/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('accounts/profile/',
        IndexView.as_view(template_name='account/index.html'),
        name='profile'),
    path('accounts/author/', make_me_author, name = 'make_me_author'),
    path('', IndexView.as_view()),
    path('subscribe/<int:pk>', subscribe, name='subscribe'),
    path('unsubscribe/<int:pk>', unsubscribe, name='unsubscribe'),
    path('categories/<int:pk>', CategoryListView.as_view(), name='category_list'),
]