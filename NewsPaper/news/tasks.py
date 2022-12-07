import datetime
from celery import shared_task
from django.template.loader import render_to_string
from NewsPaper.settings import *
from news.models import Post, Category
from news.triggers import send_notification, notify_new_post


@shared_task
def weekly_notification():
    last_week = datetime.datetime.now() - datetime.timedelta(days=7)
    posts = Post.objects.filter(creation__gte=last_week)
    categories = set(posts.values_list('category__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'notifications/weekly_news.html',
        {'posts': posts,
         'link': f'{SITE_URL}'}
    )
    subject = 'Еженедельная рассылка новостей'
    for subscriber in subscribers:
        if subscriber and len(subscriber) > 0:
            send_notification(html_content, subscriber, subject)


@shared_task
def new_post_notification(post):
    notify_new_post(post, action='post_add')