from django.conf.urls.defaults import patterns, include, handler500, handler404
 
DEFAULT_CHARSET = 'utf-8'
 
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'
 
ROOT_URLCONF = 'settings'

STATIC_URL = '/site_media/static/'

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.comments',
    'avatar',
)
 
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)
 
urlpatterns = patterns('',
    (r'^avatar/', include('avatar.urls')),
)

def __exported_functionality__():
    return (handler500, handler404)