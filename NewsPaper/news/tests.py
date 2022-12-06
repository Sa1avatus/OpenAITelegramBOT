import os
from dotenv import load_dotenv
load_dotenv()
from django.test import TestCase
import redis

red = redis.Redis(
    host = os.getenv('REDIS_ENDPONT'),
    port = int(os.getenv('REDIS_PORT')),
    #user = os.getenv('REDIS_USERNAME'),
    password = os.getenv('REDIS_PASSWORD'),
)

# Create your tests here.
