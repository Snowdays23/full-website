"""
Django settings for snowdays23 project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import dj_database_url
import datetime
import os

# Quick and dirty fix for outdated library (inlinecss)
import django.utils
django.utils.encoding.smart_text = django.utils.encoding.smart_str

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2-ewnr6g+vkftbt3i__6s-^2yf%1_@co9bl%(kzj7t16d)j%#f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', 'snowdays-staging.herokuapp.com', 'localhost:3000']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'post_office',
    'snowdays23',
    'sd23payments',
    'django_inlinecss'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF_COOKIE_SECURE = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ]
}

ROOT_URLCONF = 'snowdays23.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "frontend/build")
        ],
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

POST_OFFICE_TEMPLATES_DIR = os.path.join(BASE_DIR, "mail_templates")

WSGI_APPLICATION = 'snowdays23.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


EMAIL_BACKEND = 'post_office.EmailBackend'

POST_OFFICE = {
    "DEFAULT_PRIORITY" : "medium",
    "MAX_RETRIES": 4,
    "RETRY_INTERVAL": datetime.timedelta(minutes=15)
}

EMAIL_HOST = "smtps.aruba.it"
EMAIL_PORT = 465
EMAIL_USE_SSL = True


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings                                                                                     vvv/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/build/static"),
    os.path.join(BASE_DIR, "frontend/public")
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Regex to validate bracelet ID (Mifare Ultralight 7/8 byte UID, hex)
BRACELET_ID_REGEX = "[0-9_a-f]{14,16}"

# Regex to validate phone numbers (for this use case): +<prefix 2 or 3 digits long> <number 3 to 13 digits long>
PHONE_NUMBER_REGEX = "\+[0-9]{2,3} [0-9]{3,13}"


# In the Heroku environment
if "DATABASE_URL" in os.environ:
    # Reconfigure databases using DATABASE_URL environment variable
    DATABASES["default"] = dj_database_url.config(conn_max_age=600)

    # Configure folder to collect static files
    STATIC_ROOT = '/app/static/'

    # Receive Stripe API secret as environment variable
    STRIPE_SECRET_API_KEY = os.environ["STRIPE_SK"]

    EMAIL_HOST_USER = os.environ["ARUBA_EMAIL_USER"]
    EMAIL_HOST_PASSWORD = os.environ["ARUBA_EMAIL_PASSWORD"]

    HOST = os.environ["HOST"]


STRIPE_CHECKOUT_SUCCESS_URL = "http://localhost:8000/api/payments/order/%s/stripe/success"
STRIPE_CHECKOUT_CANCEL_URL = "http://localhost:8000/api/payments/order/%s/stripe/cancel"


STRICT_ALLOWED_EMAIL_CHECK = False


try:
    from snowdays23.local_settings import *
except:
    pass

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': None,
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }