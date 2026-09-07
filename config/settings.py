"""
Django settings for config project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subfolder'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  

    # Custom Apps
    'accounts',
    'berita',
    'core',
    'harga',
    'komoditas',
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

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'id'  

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True

USE_L10N = False
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (untuk upload file/gambar)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CONFIGURATION FOR AUTHENTICATION REDIRECTS ---
LOGIN_REDIRECT_URL = 'harga_komoditas'
LOGOUT_REDIRECT_URL = 'beranda'
LOGIN_URL = 'login'


# --- JAZZMIN ADMIN SETTINGS ---
JAZZMIN_SETTINGS = {
    "site_title": "SIPHP Admin",
    "site_header": "SIPHP Dashboard",
    "site_brand": "Sistem Informasi Pangan",
    "welcome_sign": "Selamat Datang di Panel Admin SIPHP",
    "copyright": "SIPHP Ltd",
    "search_model": "komoditas.Komoditas",
    "show_sidebar": True,
    "navigation_expanded": True,
}

# --- JAZZMIN THEME (TEMA HIJAU SEGAR) ---
JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-success navbar-dark",       # Header atas warna hijau
    "theme": "minty",                             # Tema warna hijau segar
    "sidebar": "sidebar-dark-success",            # Sidebar menu hijau gelap
    "accent": "accent-success",                   # Akses warna hijau
    "button_classes": {
        "primary": "btn-success",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# --- CONFIGURATION FOR TUNNELING (PINGGY) ---
CSRF_TRUSTED_ORIGINS = [
    'https://*.pinggy.link',
    'https://*.pinggy.net',
    'https://*.free.pinggy.net',
    'https://*.run.pinggy-free.link',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')