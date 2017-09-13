import os
import django

VERSION = django.VERSION
SETTINGS_DIR = os.path.dirname(__file__)

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'avatar',
]

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

if VERSION[0] == 1 and VERSION[1] < 8:
    TEMPLATE_DIRS = (
        os.path.join(SETTINGS_DIR, 'templates'),
    )
else:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'DIRS': [
                os.path.join(SETTINGS_DIR, 'templates')
            ]
        }
    ]

ROOT_URLCONF = 'tests.urls'

SITE_ID = 1

SECRET_KEY = 'something-something'

if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

ROOT_URLCONF = 'tests.urls'

STATIC_URL = '/site_media/static/'

AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png')
AVATAR_MAX_SIZE = 1024 * 1024
AVATAR_MAX_AVATARS_PER_USER = 20
