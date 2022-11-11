from django.urls import path
from .views import *

urlpatterns = [
   path('', PostList.as_view(), name='post_list'),
   path('<int:pk>', PostDetail.as_view(), name='post_detail'),
   path('news/create/', NewsCreate.as_view(), name='post_create'),
   path('article/create/', ArticleCreate.as_view(), name='post_create'),
   path('news/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
   path('article/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
   path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('article/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
]