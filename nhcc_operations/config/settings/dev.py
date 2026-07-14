from .base import *

SECRET_KEY=env("SECRET_KEY")
DEBUG = True

ALLOWED_HOSTS=env("ALLOWED_HOSTS").split(",")
DATABASES = {
    "default": {
        "ENGINE": env("ENGINE"),
        "NAME": BASE_DIR / env("NAME"),
    }
}