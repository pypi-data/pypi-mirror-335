import os



TEST_PROJECT_ROOT = os.path.abspath(
    os.environ.get('TEST_PROJECT_ROOT', '/tmp/'),
)

BASE_DIR = TEST_PROJECT_ROOT

NODE_MODULES_ROOT = os.path.join(TEST_PROJECT_ROOT, 'node_modules')

STATIC_ROOT = os.path.join(TEST_PROJECT_ROOT, 'yarnpkg_static')

STATIC_URL = '/static/'

YARN_INSTALLED_APPS = (
    'jquery#1.9',
    'underscore',
)

SECRET_KEY = 'iamdjangoyarnpkg'

INSTALLED_APPS = (
    'django_yarnpkg',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]
