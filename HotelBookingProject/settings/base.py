import os 
from pathlib import Path
from dotenv import load_dotenv
from .filters import RequestsFilter


#Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parents[2]

#Load environment
dotenv_path = BASE_DIR / '.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


#Apps list 
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'bookings.apps.BookingsConfig',
    'APIs.apps.ApisConfig',
    'widget_tweaks',
    'rest_framework',
    'djoser',
    'django_filters',
    'django_celery_beat',
    'django_celery_results',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

#Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'bookings.middleware.StartupSchedulerMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HotelBookingProject.urls'

#Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'HotelBookingProject.wsgi.application'



#Default User model 
AUTH_USER_MODEL = 'accounts.User'


#Set password reset time out 
PASSWORD_RESET_TIMEOUT = 60*60*12  # 12 hours in seconds: 43200


#Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,   
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


#(custom) Authentication backend
AUTHENTICATION_BACKENDS = [
    'accounts.backend.EmailOrPhoneBackend',  # custom backend to login with email or phone number
    'django.contrib.auth.backends.ModelBackend',  # default fallback
]


#Internationalization
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', 'English'),
    ('ar', 'Arabic'),  
]

LOCALE_PATHS = [    
    BASE_DIR / 'locale',                 
]

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True

USE_TZ = True  


#Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

#URL to access the uploaded media 
MEDIA_URL = '/media/'

#paths for static and media files are stored (as derivative from the base directory)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


#Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#Configure session settings for security (not applicable for JWT)
SESSION_COOKIE_AGE = 3600   # 1 hour
SESSION_SAVE_EVERY_REQUEST = True   
SESSION_EXPIRE_AT_BROWSER_CLOSE = True 
SESSION_COOKIE_HTTPONLY = True   
CSRF_COOKIE_HTTPONLY = True  
SESSION_COOKIE_NAME = 'sessionid' 
SESSION_COOKIE_SAMESITE = 'Lax'  


#Settings for Celery 
#Accepted content type
CELERY_ACCEPT_CONTENT = ['json']

#Enable celery start state tracking
CELERY_TASK_TRACK_STARTED = True

#Set timezone
CELERY_TIMEZONE = 'Africa/Cairo'

#Set celery beat scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

#Celery results database backend 
CELERY_RESULT_BACKEND = 'django-db'


#Django REST's settings 
REST_FRAMEWORK = {
            'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
            'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
            
            'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
            
            'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
            'PAGE_SIZE': 25, 

            'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle', 
                                         'rest_framework.throttling.UserRateThrottle'],
            
            'DEFAULT_THROTTLE_RATES': {
                'anon': '100/hour',   
                'user': '1000/hour',  
            },
        }


#Configure Djoser's settings
DJOSER = {
    'LOGIN_FIELD': 'email',
    'TOKEN_MODEL': None,   #None uses JWT authentication
    'HIDE_USERS': True,
    'SET_PASSWORD_RETYPE': True, 
    'PASSWORD_RESET_CONFIRM_RETYPE': True, 
    'LOGOUT_ON_PASSWORD_CHANGE': True,  

    #email-related settings 
    'SEND_ACTIVATION_EMAIL': False,  
    'SEND_PASSWORD_RESET_EMAIL': True,   #sends password reset link 
    'SEND_PASSWORD_CHANGED_EMAIL': True,  #sends confirmation email after reset (by unauthorized users)
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True, #sends confirmation email after reset (by authorized users)

    #url pattern for password resets
    'PASSWORD_RESET_CONFIRM_URL': 'api/accounts/password-reset/{uidb64}/{token}/',

    #Serializers settings 
    'SERIALIZERS': {
        'set_password': 'djoser.serializers.SetPasswordRetypeSerializer',
        'password_reset': 'djoser.serializers.SendEmailResetSerializer',
        'password_reset_confirm': 'djoser.serializers.PasswordResetConfirmRetypeSerializer',
    },
    
    #Customizing emails
    'EMAILS': {
        'password_reset': 'APIs.emails.CustomPasswordResetEmail',
        'password_changed_confirmation': 'APIs.emails.CustomPasswordChangedConfirmationEmail',
    }
}


#Configure the logger 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  
    'formatters': {
        'verbose': {
            'format': '(%(asctime)s) [%(levelname)s] - \'%(name)s\':  %(message)s',
            'datefmt': '%d/%m/%Y %H:%M:%S',
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s - \'%(name)s\':  %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',  
            'filename': f'{BASE_DIR}/logs/general.log',
            'formatter': 'verbose',   
            'level': 'DEBUG',
            'maxBytes': 10 * 1024 * 1024,  #10MB max file size
            'filters': ['ignore_requests'],
            'backupCount': 5,  
            'encoding': 'utf-8',
        },
    },
    'filters': {
        'ignore_requests': {
            '()': RequestsFilter,
        },
    },
    #configure loggers
    'loggers': {
        '': {  
            'handlers': ['console', 'file'],
            'level': 'WARNING',  
            'propagate': False,
        },
    
        #configure django's logger 
        'django': { 
            'handlers': ['console', 'file'],
            'level': 'WARNING', 
            'propagate': False,
        },

        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'filters': ['ignore_requests'],
            'propagate': False,
        },

        #configure celery's logger
        'celery': {   
            'handlers': ['console', 'file'],
            'level': 'INFO', 
            'propagate': False,
        },

    },
 }


