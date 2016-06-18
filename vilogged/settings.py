"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import platform
from config_manager import ConfigManager
DB_CONFIG = ConfigManager().get_config('database')
EMAIL_CONFIG = ConfigManager().get_config('email')
SYS_OS = platform.system()
AUTH_USER_MODEL = 'users.UserProfile'

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p%3nl3upl&9%z%elui)7&s053u+oq0g_)v@*zzbwl^tzlhy-7&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = (
    'django_nose',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'django_extensions',
    'vilogged',
    'vilogged.appointments',
    'vilogged.company',
    'vilogged.department',
    'vilogged.entrance',
    'vilogged.users',
    'vilogged.vehicles',
    'vilogged.visitors',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=vilogged/',
    '--cover-html',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'vilogged.middleware.DisableCSRF',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'vilogged.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'vilogged.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {}
}
DATABASES['default']['NAME'] = DB_CONFIG['name']
DATABASES['default']['ENGINE'] = DB_CONFIG['engine']
DATABASES['default']['HOST'] = DB_CONFIG['host']
DATABASES['default']['USER'] = DB_CONFIG['user']
DATABASES['default']['PASSWORD'] = DB_CONFIG['password']
if DB_CONFIG.get('port'):
    DATABASES['default']['PORT'] = DB_CONFIG['port']
if DB_CONFIG.get('options'):
    DATABASES['default']['OPTIONS'] = DB_CONFIG['options']


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

#USE_I18N = True

#USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/


STATIC_ROOT = '/var/www/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # # Use Django's standard `django.contrib.auth` permissions,
    # # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ]
    # Allow anything
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    # http://www.django-rest-framework.org/api-guide/filtering
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CORS_ORIGIN_ALLOW_ALL = True

APPEND_SLASH = False

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = EMAIL_CONFIG.get('host')
EMAIL_PORT = EMAIL_CONFIG.get('port')
EMAIL_USE_TLS = EMAIL_CONFIG.get('use_tls', True)
EMAIL_HOST_USER = EMAIL_CONFIG.get('user')
EMAIL_HOST_PASSWORD = EMAIL_CONFIG.get('password')