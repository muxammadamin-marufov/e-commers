import os
from pathlib import Path
import dj_database_url # Buni o'rnatish kerak: pip install dj-database-url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- XAVFSIZLIK ---
# Hugging Face-da SECRET_KEY ni Settings > Secrets qismiga qo'shasiz
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-gtj)_gvjj*$h@118#5s4!faf%4tk&^%)8ay@5udfn)$r99mow2')

# Production-da DEBUG doim False bo'lishi kerak
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Hugging Face manzillarini qabul qilish uchun
ALLOWED_HOSTS = ['*', '.hf.space']

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
    'market', # Sizning ilovangiz
    'storages', # Supabase Storage ishlatsangiz kerak bo'ladi
]

# Unfold Admin sozlamalari
UNFOLD = {
    "SITE_TITLE": "Market Admin",
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static fayllar uchun: pip install whitenoise
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
# Eslatma: db.xxxx.supabase.co o'rniga o'zingiznikini qo'ying
SUPABASE_DB_URL = "postgresql://postgres:M1m2m3m4m5m6@db.xxxx.supabase.co:5432/postgres"

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', SUPABASE_DB_URL),
        conn_max_age=600
    )
}

# --- PAROL TEKSHIRUVCHILARI ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- TIL VA VAQT ---
LANGUAGE_CODE = 'uz-uz' # O'zbek tiliga o'girdik
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# --- STATIC VA MEDIA FAYLLAR ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise orqali statik fayllarni siqish
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'