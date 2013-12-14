# Django settings for Chasebot project.
import os
from datetime import timedelta
import djcelery

djcelery.setup_loader()
 
LOGIN_URL = '/login/'

SITE_HOST = '127.0.0.1:8000'
DEFAULT_FROM_EMAIL = 'Chasebot <info@chasebot.com>'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'info@chasebot.com'
EMAIL_HOST_PASSWORD = 'expired'
EMAIL_USE_TLS = True
SERVER_EMAIL = 'info@chasebot.com'
EMAIL_SUBJECT_PREFIX = '[Chasebot]'

AUTH_PROFILE_MODULE = 'chasebot_app.UserProfile'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Hooman', 'info@chasebot.com'),
)

TEST_NAME = 'testdb_'

MANAGERS = ADMINS

GEOIP_PATH = '/home/hooman/venuscloud/chasebot-env/site/database/'
#GEOS_LIBRARY_PATH = '/opt/geos/lib/libgeos_c.so'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'chasebotDB',                      # Or path to database file if using sqlite3.
        'USER': 'django_user',                      # Not used with sqlite3.
        'PASSWORD': 'houmie123',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}


PIPELINE_YUGLIFY_BINARY = '/home/hooman/venuscloud/chasebot-env/node_modules/yuglify/bin/yuglify'
PIPELINE_CLOSURE_BINARY = '/home/hooman/venuscloud/chasebot-env/bin/closure'
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
#PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.closure.ClosureCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'

PIPELINE_CSS = {
    'chasebot_css': {
        'source_filenames': (
          'chasebot/chasebot.css',          
        ),
        'output_filename': 'chasebot/chasebot.min.css',        
    },
    'bootstrap_datepicker_css': {
        'source_filenames': (
          'bootstrap-datepicker/css/datepicker.css',          
        ),
        'output_filename': 'bootstrap-datepicker/css/datepicker.min.css',        
    },
    'bootstrap_timepicker_css': {
        'source_filenames': (
          'bootstrap-timepicker/compiled/timepicker.css',          
        ),
        'output_filename': 'bootstrap-timepicker/compiled/timepicker.min.css',        
    },
    'chosen_css': {
        'source_filenames': (
          'chosen/chosen/chosen.css',
        ),
        'output_filename': 'chosen/chosen/chosen.min.css',        
    },
    'famfamfam_flags_css': {
        'source_filenames': (
          'famfamfam_flags/famfamfam-flags.css',
        ),
        'output_filename': 'famfamfam_flags/famfamfam-flags.min.css',        
    },
    'tablesorter_pager_css': {
        'source_filenames': (
          'tablesorter/addons/pager/jquery.tablesorter.pager.css',
        ),
        'output_filename': 'tablesorter/addons/pager/jquery.tablesorter.pager.min.css',        
    },
    'tablesorter_theme_css': {
        'source_filenames': (
          'tablesorter/css/theme.bootstrap.css',
        ),
        'output_filename': 'tablesorter/css/theme.bootstrap.min.css',        
    },
}

PIPELINE_JS = {
    'chasebot_js': {
        'source_filenames': (
          'chasebot/chasebot.js',          
        ),
        'output_filename': 'chasebot/chasebot.min.js',
    },
#    'bigdecimal_js': {
#        'source_filenames': (
#          'bigdecimal.js/bigdecimal.js',          
#        ),
#        'output_filename': 'bigdecimal.js/bigdecimal.min.js',
#    },
   'bootstrap_datepicker_js': {
        'source_filenames': (
          'bootstrap-datepicker/js/bootstrap-datepicker.js',
        ),
        'output_filename': 'bootstrap-datepicker/js/bootstrap-datepicker.min.js',
    },
   'bootstrap_timepicker_js': {
        'source_filenames': (
          'bootstrap-timepicker/js/bootstrap-timepicker.js',
        ),
        'output_filename': 'bootstrap-timepicker/js/bootstrap-timepicker.min.js',
    },
   'jquery_fix_clone_js': {
        'source_filenames': (
          'jquery.fix.clone/jquery.fix.clone.js',          
        ),
        'output_filename': 'jquery.fix.clone/jquery.fix.clone.min.js',
    },
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
    ('en-gb', ugettext('British English'))
)

#MODELTRANSLATION_TRANSLATION_REGISTRY = 'chasebot_app.translation'
MODELTRANSLATION_TRANSLATION_FILES = (
  'chasebot_app.translation',
)

LOCALE_PATHS = (
  '/home/hooman/venuscloud/chasebot-env/site/locale',
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
MEDIA_ROOT = '/home/hooman/venuscloud/chasebot-env/site/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/hooman/venuscloud/chasebot-env/site/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/hooman/venuscloud/chasebot-env/site/static_files/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lfbsf#q3vgr%!#o%@31ta%=c6u2&amp;c)35f*ar0i#d6f@s4v&amp;@1z'

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
    'django.middleware.transaction.TransactionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'chasebot.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'chasebot.wsgi.application'

TEMPLATE_DIRS = (
        #os.path.join(os.path.dirname(__file__), '../templates'),
        '/home/hooman/venuscloud/chasebot-env/site/templates/'
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
    'widget_tweaks',
    'chasebot_app',  
    'south',  
    'modeltranslation',
    'djcelery',
)

BROKER_BACKEND = "SQS"
BROKER_URL = 'sqs://xxxx@'
BROKER_TRANSPORT_OPTIONS = {'queue_name_prefix': '-sqs', 'visibility_timeout': 300}
CELERY_RESULT_BACKEND="database"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

CELERY_DEFAULT_QUEUE = "chasebot_queue"
CELERY_DEFAULT_EXCHANGE = CELERY_DEFAULT_QUEUE
CELERY_DEFAULT_EXCHANGE_TYPE = CELERY_DEFAULT_QUEUE
CELERY_DEFAULT_ROUTING_KEY = CELERY_DEFAULT_QUEUE
CELERY_QUEUES = {
    CELERY_DEFAULT_QUEUE: {
        'exchange': CELERY_DEFAULT_QUEUE,
        'binding_key': CELERY_DEFAULT_QUEUE,
        }
}

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