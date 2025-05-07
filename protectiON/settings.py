"""
Django settings for protectiON project.
"""

import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── SECURITY ────────────────────────────────────────────────────────────────
if os.path.exists(BASE_DIR / '.env'):
    from dotenv import load_dotenv
    load_dotenv()

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-&u-$eak0!uyb(_$5pif3o-^^xpqtf@(dk2=ts(tcalyj8gnc+)'  # solo dev
)

DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

# ─── APPLICATION DEFINITION ─────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third‑party
    'rest_framework',
    'rest_framework.authtoken',
    'storages',               #  S3 backend

    # local
    'appProtectiOn.apps.AppProtectiOnConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'protectiON.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'protectiON.wsgi.application'

# ─── DATABASE ───────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME'  : BASE_DIR / 'db.sqlite3',
    }
}

if db_url := os.getenv('DATABASE_URL'):
    p = urlparse(db_url)
    DATABASES['default'] = {
        'ENGINE'  : 'django.db.backends.postgresql',
        'NAME'    : p.path.lstrip('/'),
        'USER'    : p.username,
        'PASSWORD': p.password,
        'HOST'    : p.hostname,
        'PORT'    : p.port,
    }

# ─── PASSWORD VALIDATORS ────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNATIONALIZATION ───────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─── STATIC & MEDIA ─────────────────────────────────────────────────────────
STATIC_URL       = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT      = BASE_DIR / 'staticfiles'

MEDIA_URL  = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── DEFAULT PK FIELD ───────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── DRF ─────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# ─── LOGIN REDIRECTS ────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL  = 'home'
LOGOUT_REDIRECT_URL = 'login'

# ─── AWS S3 STORAGE ─────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME      = os.getenv('AWS_S3_REGION_NAME', 'eu-west-3')

# usar S3 en producción (DEBUG False); local FS en desarrollo
if not DEBUG and all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
    DEFAULT_FILE_STORAGE   = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE    = 'storages.backends.s3boto3.S3Boto3Storage'   # opcional

    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_QUERYSTRING_AUTH     = False
    AWS_DEFAULT_ACL          = None              # bucket con ACLs deshabilitadas

    MEDIA_URL  = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'
    STATIC_URL = MEDIA_URL  # estáticos en el mismo bucket (ajusta si quieres otro)

