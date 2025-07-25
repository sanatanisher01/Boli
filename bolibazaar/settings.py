import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here')

DEBUG = True

ALLOWED_HOSTS = ['*', 'bolibazaar.onrender.com', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'auction',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bolibazaar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bolibazaar.wsgi.application'

import os

# Database configuration
# Use PostgreSQL in production, SQLite in development
if 'RENDER' in os.environ:
    # Production database (PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'bolibazaar',
            'USER': 'bolibazaar_user',
            'PASSWORD': 'PUJXzqq6jS20SoU5uFO8VrLaqhd7Ja2d',
            'HOST': 'dpg-d1cgqaeuk2gs73an89jg-a',
            'PORT': '5432',
        }
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sanatanisofindia@gmail.com'
EMAIL_HOST_PASSWORD = 'hjdy ppcu yzbs qubd'
DEFAULT_FROM_EMAIL = 'BoliBazaar <sanatanisofindia@gmail.com>'

# Site URL for emails
SITE_URL = 'https://bolibazaar.onrender.com'

# OmniDimension API Key
OMNIDIMENSION_API_KEY = 'P-rBV6jy7fmjIzrFHzMcx_IuWq0cVZsm5NV-CRCfews'

# Account activation
ACCOUNT_ACTIVATION_DAYS = 7

# Cloudinary Configuration
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name='dtx6fiyie',
    api_key='267355732654919',
    api_secret='CXAQ47Wob--lrFOF8CuYduSjRo4'
)

# Use Cloudinary for media storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dtx6fiyie',
    'API_KEY': '267355732654919',
    'API_SECRET': 'CXAQ47Wob--lrFOF8CuYduSjRo4',
}