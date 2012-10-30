# Django settings for Chasebot project.
import os
from datetime import timedelta
#import djcelery 
#djcelery.setup_loader()

LOGIN_URL = '/login/'

SITE_HOST = '127.0.0.1:8000'
DEFAULT_FROM_EMAIL = 'Chasebot <info@chasebot.com>'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'info@chasebot.com'
EMAIL_HOST_PASSWORD = 'Rahil2503'
EMAIL_USE_TLS = True
SERVER_EMAIL = 'houmie@gmail.com'
EMAIL_SUBJECT_PREFIX = '[Chasebot]'

AUTH_PROFILE_MODULE = 'chasebot_app.UserProfile'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Houman', 'houman@venuscloud.com'),
)

TEST_NAME = 'testdb_'

MANAGERS = ADMINS

GEOIP_PATH = '/home/houman/projects/chasebot/database/'
#GEOS_LIBRARY_PATH = '/opt/geos/lib/libgeos_c.so'

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'Ch4s3b0tDB',                      # Or path to database file if using sqlite3.
        'USER': 'django_user',                      # Not used with sqlite3.
        'PASSWORD': 'houmie123',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_YUI_BINARY = '/venuscloud/chasebot-env/site/chasebot/node_modules/yuglify/bin/yuglify'
PIPELINE_CSS = {
    'chasebot_css': {
        'source_filenames': (
          'chasebot/chasebot_styles.css',          
        ),
        'output_filename': 'chasebot/chasebot_styles.min.css',        
    },
}

PIPELINE_JS = {
    'chasebot_js': {
        'source_filenames': (
          'chasebot/chasebot_base.js',          
        ),
        'output_filename': 'chasebot/chasebot_base.min.js',
    }
}

FORMAT_MODULE_PATH = 'chasebot.formats'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'
#TIME_ZONE = 'US/Eastern'


# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'en-gb'

ugettext = lambda s: s

LANGUAGES = (
    ('en', ugettext('American English')),
    ('en-gb', ugettext('British English')),
    ('es', ugettext('Spanish'))
)

MODELTRANSLATION_TRANSLATION_REGISTRY = 'chasebot_app.translation'

LOCALE_PATHS = (
  '/home/houman/projects/chasebot/locale',
)


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/houman/projects/chasebot/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/houman/projects/chasebot/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/houman/projects/chasebot/static_files/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lfbmf#q3vgr%!#o%@31ta%=c6u2&amp;c)35f*ar0i#d6f@s4v&amp;@1z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',    
    'chasebot.middlewares.TimezoneMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'chasebot.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'chasebot.wsgi.application'

TEMPLATE_DIRS = (
        #os.path.join(os.path.dirname(__file__), '../templates'),
        '/home/houman/projects/chasebot/templates/'
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',    
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.gis',
    'pipeline',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'chasebot_app',  
    'south',  
    'modeltranslation',
    #'djcelery',
)

BROKER_URL = 'amqp://guest:guest@localhost:5672/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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


CELERYBEAT_SCHEDULE = {
    'runs-every-30-seconds': {
        'task': 'tasks.add',
        'schedule': timedelta(seconds=30),
        'args': (16, 16)
    },
}