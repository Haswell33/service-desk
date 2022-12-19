from pathlib import Path

CUST_TYPE = 'customer'
OPER_TYPE = 'operator'
DEV_TYPE = 'developer'
SD_ENV_TYPE = 'service-desk'
SOFT_ENV_TYPE = 'software'
DEFAULT_ISSUE_TYPE_ID = 1
DEFAULT_PRIORITY_ID = 3
SD_INITIAL_STATUS = 15
SOFT_INITIAL_STATUS = 26
ROLES = [
    ('customer', 'Customer'),
    ('operator', 'Operator'),
    ('developer', 'Developer')
]
ENV_TYPES = [
    ('service-desk', 'Service Desk'),
    ('software', 'Software')
]
ALLOW_FILE_EXTENSIONS = [
    '.pdf', '.txt', '.doc', '.docx', '.odt', '.rtf', '.html', '.pptx',  # documents
    '.csv', '.xlsx', '.ods', '.tsv',  # sheets
    '.jpg', '.jpeg', '.png', '.svg', '.webp', '.ico', '.bmp', '.tiff', '.jfif'  # img
    '.mp3',  # music
    '.mp4', '.mkv', '.avi', '.webm', '.gif', '.gifv'  # video
    '.zip', '.rar', '.7zip', '.tar', '.gz',  # zip
    'java', '.py', '.c', '.cpp', '.js', '.gs', '.groovy', '.sh'  # code ,
]
FILE_EXTENSIONS = {
    'pdf': ['pdf'],
    'doc': ['txt', 'doc', 'docx', 'odt', 'rtf', 'html', 'pptx'],
    'sheet': ['csv', 'xlsx', 'ods', 'tsv'],
    'img': ['jpg', 'jpeg', 'png', 'svg', 'webp', '.ico', 'bmp', 'tiff', 'jfif'],
    'music': ['mp3'],
    'video': ['mp4', 'mkv', 'avi', 'webm', 'gif', 'gifv'],
    'zip': ['zip', 'rar', '7zip', 'tar', 'gz'],
    'code': ['java', 'py', 'c', 'cpp', 'js', 'gs', 'groovy', 'sh']
}

BASE_DIR = Path(__file__).resolve().parent.parent  # Build paths inside the project like this: BASE_DIR / 'subdir'.
SECRET_KEY = 'django-insecure-z(g7^uxx3*)@ctru=wvchu5tezwzd3s@0m01rozf=-szc8%_!@'
ALLOWED_HOSTS = ['192.168.0.100', '192.168.0.101', '127.0.0.1', '*']
ROOT_URLCONF = 'conf.urls'
WSGI_APPLICATION = 'conf.wsgi.application'
# STATIC_URL = '/static/'  # Static files (CSS, JavaScript, Images) https://docs.djangoproject.com/en/3.2/howto/static-files/
# STATIC_ROOT = f'{BASE_DIR}'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'logged_out'
LANGUAGE_CODE = 'en-us'  # Internationalization https://docs.djangoproject.com/en/3.2/topics/i18n/
SITE_NAME = 'ServiceDeskApp'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEBUG = False
TIME_ZONE = 'Europe/Zagreb'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Default primary key field type https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
AUTH_USER_MODEL = 'core.User'
USE_X_FORWARED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
INSTALLED_APPS = [
    'core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'tinymce',
    'django_extensions',
    'django_prometheus'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

STATICFILES_DIRS = [
    f'{BASE_DIR}/static'
]

LOCALE_PATH = [
    f'{BASE_DIR}/locale'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [f'{BASE_DIR}/staticfiles/site/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.context_tenant_session',
                'core.context_processors.get_user_icon',
                'core.context_processors.get_media',
                'core.context_processors.get_tenants',
            ]
        },
    },
]

DATABASES = {  # https://docs.djangoproject.com/en/3.2/ref/settings/#databases
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<DB_NAME>>',
        'USER': '<DB_USER>>',
        'PASSWORD': '<DB_PASS>>',
        'HOST': '<DB_HOST>',
        'PORT': '<DB_PORT>>',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.11211'
    }
}

CACHE_MIDDLEWARE_ALIAS = 'default'  # which cache alias to use
CACHE_MIDDLEWARE_SECONDS = '600'    # number of seconds to cache a page for (TTL)
CACHE_MIDDLEWARE_KEY_PREFIX = ''    # should be used if the cache is shared across multiple sites that use the same Django instance


AUTH_PASSWORD_VALIDATORS = [  # https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table, paste, searchreplace, link, image, code, autoresize",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'toolbar1': 'formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | table | link image',
    'menubar': True,
    'selector': 'textarea'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'format-request': {
            'format': "{asctime} {levelname} {request.user.username} {request.method} {status_code} {message}",
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'format-sql': {
            'format': "{asctime} {levelname} {alias} {sql} {params} [{duration}]",
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
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
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'format-request',
            'filename': f'{BASE_DIR}/logs/request.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 5,
        },
        'template': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/template.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 5,
        },
        'django': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'format-request',
            'filename': f'{BASE_DIR}/logs/django.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 5,
        },
        'security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/security.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 5,
        },
        'sql': {
            'level': 'DEBUG',
            #'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'format-sql',
            'filename': f'{BASE_DIR}/logs/sql.log',
            'maxBytes': 1024*1024*50,
            'backupCount': 5,
        },
        'app': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/app.log',
            'maxBytes': 1024*1024*50,
            'backupCount': 5,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['request'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['request'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['template'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security.*': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends.schema': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'app': {
            'handlers': ['app'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['django'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
