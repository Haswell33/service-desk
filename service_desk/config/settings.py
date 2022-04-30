# Django settings for config project.
#   Generated by 'django-admin startproject' using Django 3.2.9.
#   More information on this file https://docs.djangoproject.com/en/3.2/topics/settings/
#   Full list of settings and their values https://docs.djangoproject.com/en/3.2/ref/settings/
#   Quick-start development settings - unsuitable for production https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Build paths inside the project like this: BASE_DIR / 'subdir'.
SECRET_KEY = 'django-insecure-z(g7^uxx3*)@ctru=wvchu5tezwzd3s@0m01rozf=-szc8%_!@'
ALLOWED_HOSTS = ['192.168.0.100', '127.0.0.1']
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
STATIC_URL = '/static/'  # Static files (CSS, JavaScript, Images) https://docs.djangoproject.com/en/3.2/howto/static-files/
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'logged_out'
LANGUAGE_CODE = 'en-us'  # Internationalization https://docs.djangoproject.com/en/3.2/topics/i18n/
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEBUG = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Default primary key field type https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [f'{BASE_DIR}/static/templates/'],
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

DATABASES = {  # https://docs.djangoproject.com/en/3.2/ref/settings/#databases
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'service-desk',
        'USER': 'sd_admin',
        'PASSWORD': 'NdhsrlBcGYY8mK2sKoy6XSLQR3hFb75giZz',
        'HOST': '192.168.0.100',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [  # https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
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
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname} {request} {status_code} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'format-request': {
            'format': '{asctime} {levelname} "{request} {status_code}" {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'request': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/request.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
        },
        'template': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/template.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
        'server': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/server.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
        'security': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/security.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
        'sql': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/sql.log',
            'maxBytes': 1024*1024*50,
            'backupCount': 15,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['template'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['server'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.security.*': {
            'handlers': ['security'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends.schema': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
