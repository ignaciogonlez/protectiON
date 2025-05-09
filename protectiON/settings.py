"""
Django settings for protectiON project
"""
import os
from pathlib import Path
from urllib.parse import urlparse

# ───────────────────────── BASE
BASE_DIR = Path(__file__).resolve().parent.parent

if (BASE_DIR / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv()

# ───────────────────────── SEGURIDAD
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-DEV-ONLY")
DEBUG      = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []
)

# ───────────────────────── APPS
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party
    "rest_framework",
    "rest_framework.authtoken",
    "storages",          # S3
    # Local
    "appProtectiOn.apps.AppProtectiOnConfig",
]

# ───────────────────────── MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # inmediatamente después
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ───────────────────────── URLS / WSGI
ROOT_URLCONF  = "protectiON.urls"
WSGI_APPLICATION = "protectiON.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

# ───────────────────────── BD
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME"  : BASE_DIR / "db.sqlite3",
    }
}
if (db := os.getenv("DATABASE_URL")):
    p = urlparse(db)
    DATABASES["default"] = {
        "ENGINE"  : "django.db.backends.postgresql",
        "NAME"    : p.path.lstrip("/"),
        "USER"    : p.username,
        "PASSWORD": p.password,
        "HOST"    : p.hostname,
        "PORT"    : p.port,
    }

# ───────────────────────── PASSWORDS
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───────────────────────── I18N
LANGUAGE_CODE = "es"
TIME_ZONE     = "Europe/Madrid"
USE_I18N = True
USE_TZ   = True

# ───────────────────────── STATIC / MEDIA
STATIC_URL  = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL  = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ───────────────────────── DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ]
}

LOGIN_REDIRECT_URL  = "home"
LOGOUT_REDIRECT_URL = "login"

# ───────────────────────── S3
AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME      = os.getenv("AWS_S3_REGION_NAME", "eu-west-3")

print("S3-ENV:",
      AWS_ACCESS_KEY_ID[:4] if AWS_ACCESS_KEY_ID else None,
      AWS_SECRET_ACCESS_KEY[:4] if AWS_SECRET_ACCESS_KEY else None,
      AWS_STORAGE_BUCKET_NAME)

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_QUERYSTRING_AUTH = False     # URLs limpias
    AWS_DEFAULT_ACL      = None      # bucket owner enforced
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"

# ───────────────────────── DEBUG helper
if DEBUG:
    from django.core.files.storage import default_storage
    print(">>> DEFAULT STORAGE =", default_storage.__class__)

# ───────────────────────── OTHER
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
