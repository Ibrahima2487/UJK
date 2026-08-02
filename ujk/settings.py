from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPEND_SLASH = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z24ln_fne@z3faz%7r^hv-60j#@d+kagvh30jfb9$6h6$8#og#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'pwa',
    'tailwind',
    'theme',
]

TAILWIND_APP_NAME = 'theme'

# Tailwind uniquement si le dossier existe
"""
if DEBUG and (BASE_DIR / 'theme').exists():
    try:
        import tailwind
        INSTALLED_APPS += ['tailwind', 'theme']
        TAILWIND_APP_NAME = 'theme'
        INTERNAL_IPS = ["127.0.0.1"]
    except ImportError:
        pass
"""

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # Désactivé (pas besoin en local)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ujk.urls'

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'ujk.wsgi.application'

# Database - SQLite pure (sans Internet)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = []
if (BASE_DIR / 'theme/static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'theme/static')

# Pas de whitenoise - stockage standard
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/main/'
LOGOUT_REDIRECT_URL = '/login/'

# ========== PWA CONFIGURATION ==========
PWA_APP_NAME = 'UJK'
PWA_APP_SHORT_NAME = 'UJK'
PWA_APP_DESCRIPTION = 'Site officiel de Union des jeunes de Kakony'
PWA_APP_THEME_COLOR = "#097e93"
PWA_APP_BACKGROUND_COLOR = "#082b6f"
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'fr-FR'

PWA_APP_ICONS = [
    {
        'src': '/static/image/logo.png',
        'sizes': '1280x1280',
        'type': 'image/png'
    },
    {
        'src': '/static/image/logo.png',
        'sizes': '192x192',
        'type': 'image/png'
    },
    {
        'src': '/static/image/logo.png',
        'sizes': '512x512',
        'type': 'image/png'
    },
]

PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/image/logo.png',
        'sizes': '512x512',
        'type': 'image/png'
    }
]

PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'fr-FR'


SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False