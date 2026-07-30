from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages
import os

BASE_DIR = Path(__file__).resolve().parent.parent
environment = os.environ.get("DJANGO_SETTINGS_MODULE").split(".")[-1]
env_file = BASE_DIR / f".env.{environment}"

if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    raise FileNotFoundError(f"Environment file {env_file} not found.")

def env(key, default=None):
    return os.getenv(key, default)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 'silk',
    'account',
    'dashboard',
    'finance',
    'finance.expense',
    'report',
    'staff',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'nhcc_operations.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nhcc_operations.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "account.CustomUser"
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
LOGIN_URL="login"

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

EMAIL_BACKEND = env("EMAIL_BACKEND")

EMAIL_HOST = env("SMTP_SERVER")

EMAIL_PORT = env("SMTP_PORT", default=587)

EMAIL_USE_TLS = True

EMAIL_USE_SSL = False

EMAIL_HOST_USER = env("SMTP_USERNAME")

EMAIL_HOST_PASSWORD = env("SMTP_PASSWORD")

DEFAULT_FROM_EMAIL = env("SENDER_EMAIL")

HTTP_ONLY_SECURE=bool(env("HTTP_ONLY_SECURE"))

