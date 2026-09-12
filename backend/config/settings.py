"""
FreshMart backend settings.
Reads all secrets/config from environment variables (see .env.example).

Local development is HTTP-only (http://127.0.0.1:8000 <-> http://localhost:5173).
Nothing in this file forces HTTPS unless you explicitly set the relevant env
vars (SECURE_SSL_REDIRECT / SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE) to
True -- which you should only do once the app is actually served over HTTPS
(e.g. behind an nginx/TLS-terminating proxy in production).
"""
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-insecure-key-change-me")
# Defaults to True so the project runs out of the box with no .env file.
# Set DEBUG=False (and configure ALLOWED_HOSTS / SECRET_KEY properly) for production.
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_yasg",

    # local apps
    "accounts",
    "categories",
    "products",
    "cart",
    "wishlist",
    "coupons",
    "orders",
    "payments",
    "reviews",
    "dashboard",
    "notifications",
]

# NOTE on ordering: CorsMiddleware is placed FIRST (before SecurityMiddleware and
# any middleware that can short-circuit and return a redirect). django-cors-headers'
# own docs call this out explicitly: if a response-generating middleware runs before
# CorsMiddleware, its response (e.g. an HTTPS redirect) goes out with NO CORS headers
# attached, and the browser rejects the preflight with exactly the error this project
# was hitting: "Redirect is not allowed for a preflight request." Combined with
# SECURE_SSL_REDIRECT being off for local HTTP dev (below), this is now defense in depth.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database (SQLite only) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / config("DB_NAME", default="db.sqlite3"),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# In DEBUG, use WhiteNoise's finder-backed serving so admin/DRF-browsable-API CSS
# works immediately without requiring `collectstatic` first (this is what was causing
# "Admin opens but CSS is missing" -- CompressedManifestStaticFilesStorage requires a
# manifest that only exists after collectstatic has been run). In production, keep the
# compressed+hashed manifest storage for cache-busting, and run collectstatic in the
# deploy step (already done in Dockerfile / docker-compose).
if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cloudinary (media storage) ---
if config("USE_CLOUDINARY", default=False, cast=bool):
    INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
        "API_KEY": config("CLOUDINARY_API_KEY", default=""),
        "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
    }
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- CORS ---
# Both the localhost and 127.0.0.1 forms are included by default because browsers treat
# them as different origins -- the frontend dev server can be opened as either, and the
# API must allow whichever one the browser is actually using or every preflight fails.
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="https://freshmart-frontend-0p6f.onrender.com",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# --- SEO ---
# Used to build absolute URLs in the sitemap (frontend routes, not API routes).
# In production this should be the single public domain nginx serves both
# frontend and backend under (see deploy/nginx/default.conf).
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")

# --- Redis / Celery ---
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")

# In DEBUG, use Django's built-in in-memory cache so local dev never depends on a
# running Redis server. This is what was actually causing the ConnectionError /
# ConnectionInterrupted tracebacks -- IGNORE_EXCEPTIONS is meant to make DRF's
# throttle classes fail silently when Redis is unreachable, but that behavior isn't
# consistently honored across django-redis versions, so it's not something to rely on
# for local dev. In production (DEBUG=False), Redis is used as configured, with
# IGNORE_EXCEPTIONS kept as a safety net so a Redis blip doesn't take the API down.
if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
# In DEBUG, run tasks synchronously in-process instead of publishing to a Redis broker.
# Without this, any `.delay()` call (order confirmation emails/SMS, low-stock alerts --
# see orders/services.py, notifications/tasks.py) raises the same "Redis refused
# connection" error as the cache did, the moment you exercise checkout/order flows
# without a Redis server and Celery worker running locally.
CELERY_TASK_ALWAYS_EAGER = DEBUG
CELERY_TASK_EAGER_PROPAGATES = DEBUG

EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- HTTPS-related settings: OFF by default, and independent of DEBUG. ---
# Previously these were gated on `if not DEBUG`, which meant simply running with
# DEBUG=False (e.g. because no .env file was present, so DEBUG fell back to its
# default) silently turned SECURE_SSL_REDIRECT on. That made Django's
# SecurityMiddleware 301-redirect every http:// request -- including CORS preflight
# OPTIONS requests -- to https://127.0.0.1:8000, which the dev server cannot serve
# (hence ERR_SSL_PROTOCOL_ERROR / "you're accessing the development server over
# HTTPS" / "Redirect is not allowed for a preflight request"). These now default to
# False unconditionally and must be explicitly opted into via env vars once the app
# is actually deployed behind HTTPS (e.g. behind the nginx TLS-terminating proxy).
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)
STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
