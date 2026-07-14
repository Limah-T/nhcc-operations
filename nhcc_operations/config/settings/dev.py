from .base import *

SECRET_KEY=env("SECRET_KEY")
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '172.20.10.4']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}