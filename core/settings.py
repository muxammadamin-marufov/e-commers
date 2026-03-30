import os
from pathlib import Path
# import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- XAVFSIZLIK ---
# Hugging Face Settings > Secrets qismiga DJANGO_SECRET_KEY qo'shing
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-uz-2026')

# Production-da DEBUG False bo'ladi, agar Secret-ga DEBUG=True qo'shmasangiz
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# DEBUG = True
# Hugging Face manzillarini aniq ko'rsatish xavfsizroq
ALLOWED_HOSTS = ['*', '.hf.space', 'localhost', '127.0.0.1']

# CSRF xavfsizligi (Hugging Face uchun shart)
CSRF_TRUSTED_ORIGINS = ['https://*.hf.space']

# --- ILOVALAR ---
INSTALLED_APPS = [
    'unfold',
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'market',
    'storages',
]

# Unfold Admin sozlamalari
UNFOLD = {
    "SITE_TITLE": "Electro Market Admin",
    "SITE_SYMBOL": "shopping_cart", # Simvolni o'zgartirdim
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static fayllar uchun
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'core.wsgi.application'

# --- MA'LUMOTLAR BAZASI (SUPABASE) ---
# Siz bergan yangi URL: https://fslryydojcmqrpchiysf.supabase.co
# Connection string: postgresql://postgres:M1m2m3m4m5m6@db.fslryydojcmqrpchiysf.supabase.co:5432/postgre
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# --- PAROL TEKSHIRUVCHILARI ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- TIL VA VAQT ---
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# --- STATIC VA MEDIA FAYLLAR ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise optimizatsiyasi
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
