from .base import *

# ------------------------
# BASIC
# ------------------------

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

# ------------------------
# CSRF
# ------------------------

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.0.1:8000",
]

# ------------------------
# COOKIES
# ------------------------

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ------------------------
# HTTPS
# ------------------------

SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

# ------------------------
# HSTS
# ------------------------

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ------------------------
# SECURITY HEADERS
# ------------------------

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "strict-origin"

# ------------------------
# STATIC FILES
# ------------------------

STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------
# MEDIA FILES
# ------------------------

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# ------------------------
# DATABASE
# ------------------------

DATABASES = {
    "default": {
        "ENGINE": env("ENGINE"),
        "NAME": BASE_DIR / env("NAME"),
    }
}

# ------------------------
# EMAIL
# ------------------------

# ------------------------
# LOGGING
# ------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}