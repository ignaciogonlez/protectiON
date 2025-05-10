"""
Django settings for protectiON project
"""
import os
import sys
import logging
from pathlib import Path
from urllib.parse import urlparse

# ───────────────────────── BASE ─────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
if (BASE_DIR / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv()

# ───────────────────────── S3 ──────────────────────────────────
AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME      = os.getenv("AWS_S3_REGION_NAME", "eu-west-3")

if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
    # configuración de django-storages / S3
    AWS_DEFAULT_ACL         = None               # evita public-read
    AWS_QUERYSTRING_AUTH    = False
    AWS_S3_FILE_OVERWRITE   = False
    AWS_S3_ADDRESSING_STYLE = "virtual"
    AWS_S3_CUSTOM_DOMAIN    = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

    # Define BACKENDS modernos (Django 5+)
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

else:
    # modo local: file system storage
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    MEDIA_URL  = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ───────────────────────── SEGURIDAD ────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-¡SOLO-PARA-DESARROLLO!")
DEBUG      = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []
if DEBUG:
    # durante desarrollo local añadimos IP LAN
    ALLOWED_HOSTS += ["127.0.0.1", "localhost", "192.168.1.130"]

# ───────────────────────── APPS ─────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "storages",                      # django-storages
    "appProtectiOn.apps.AppProtectiOnConfig",
]

# ───────────────────────── MIDDLEWARE ───────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ───────────────────────── URLS / WSGI ──────────────────────────
ROOT_URLCONF     = "protectiON.urls"
WSGI_APPLICATION = "protectiON.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS":    [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

# ───────────────────────── DATABASE ─────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   BASE_DIR / "db.sqlite3",
    }
}
if (db_url := os.getenv("DATABASE_URL")):
    p = urlparse(db_url)
    DATABASES["default"] = {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     p.path.lstrip("/"),
        "USER":     p.username,
        "PASSWORD": p.password,
        "HOST":     p.hostname,
        "PORT":     p.port,
    }

# ───────────────────────── PASSWORDS ────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───────────────────────── I18N ─────────────────────────────────
LANGUAGE_CODE = "es"
TIME_ZONE     = "Europe/Madrid"
USE_I18N      = True
USE_TZ        = True

# ───────────────────────── STATICFILES ───────────────────────────
STATIC_URL            = "static/"
STATICFILES_DIRS      = [BASE_DIR / "static"]
STATIC_ROOT           = BASE_DIR / "staticfiles"
# el backend de static se lee de STORAGES["staticfiles"]

# ───────────────────────── DRF ──────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}
LOGIN_REDIRECT_URL  = "home"
LOGOUT_REDIRECT_URL = "login"

# ───────────────────────── LOGGING ───────────────────────────────
logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "boto3":   {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "botocore":{"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "storages.backends.s3boto3": {
            "handlers": ["console"], "level": "DEBUG", "propagate": False,
        },
    },
}

# ───────────────────────── POST-BOOT S3 check ───────────────────
if not DEBUG and AWS_STORAGE_BUCKET_NAME:
    from storages.backends.s3boto3 import S3Boto3Storage
    try:
        probe = S3Boto3Storage()
        print("✓ S3Boto3Storage inicializado. Bucket:", probe.bucket_name)
    except Exception as e:
        print("✗ ERROR INICIALIZANDO S3Boto3Storage:", e, file=sys.stderr)

# ───────────────────────── AUTO FIELD ────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
