import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()


def _split_csv(raw_value):
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-secret-key")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

default_hosts = ["localhost", "127.0.0.1", "0.0.0.0"]
raw_allowed_hosts = os.getenv("ALLOWED_HOSTS")
ALLOWED_HOSTS = _split_csv(raw_allowed_hosts) or default_hosts.copy()

render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

raw_csrf_trusted = os.getenv("CSRF_TRUSTED_ORIGINS")
if raw_csrf_trusted:
    CSRF_TRUSTED_ORIGINS = _split_csv(raw_csrf_trusted)
else:
    default_csrf = [
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0",
    ]
    if render_host:
        default_csrf.extend(
            [
                f"https://{render_host}",
                f"http://{render_host}",
            ]
        )
    CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(default_csrf))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "accounts",
    "catalog",
    "suppliers",
    "items",
    "transactions",
    "analytics",
]

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

ROOT_URLCONF = "ewaste_api.urls"

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

WSGI_APPLICATION = "ewaste_api.wsgi.application"
ASGI_APPLICATION = "ewaste_api.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

database_url = os.getenv("DATABASE_URL")
if database_url:
    DATABASES["default"] = dj_database_url.parse(
        database_url,
        conn_max_age=600,
        ssl_require=os.getenv("DATABASE_SSL_REQUIRE", "false").lower() == "true",
    )

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CORS_ALLOW_ALL_ORIGINS = True

access_minutes = int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", "15"))
refresh_days = int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", "7"))

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=access_minutes),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=refresh_days),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "E-Waste Collection & Pricing API",
    "DESCRIPTION": "API for managing e-waste categories, suppliers, collections, transactions, and analytics.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

