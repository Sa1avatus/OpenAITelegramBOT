import os
import smtplib
from email.mime.text import MIMEText

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from NewsPaper.settings import SITE_URL
from .models import PostCategory
from dotenv import load_dotenv
load_dotenv()


def send_notification(instance, subscriber):
    server = smtplib.SMTP_SSL(os.getenv('SMTP_EMAIL_HOST'), int(os.getenv('EMAIL_PORT')))
    server.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
    post = instance
    html_content = render_to_string(
        'notifications/new_news_notification.html',
        {'post': post,
         'link': f'{SITE_URL}/news/{post.pk}'}
    )
    msg = MIMEText(html_content, 'html')
    msg['To'] = subscriber
    msg['Subject'] = f'{post.title}'
    server.send_message(msg)


@receiver(m2m_changed, sender=PostCategory)
def notify_new_post(instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.category.all()
        subscribers = []
        for category in categories:
            subscribers += category.subscribers.all()
        subscribers = [s.email for s in subscribers]
        print(subscribers)
        for subscriber in subscribers:
            if len(subscriber) > 0:
                send_notification(instance, subscriber)

