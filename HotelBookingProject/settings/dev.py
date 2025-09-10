import os
from .base import *
from datetime import timedelta

#Development Security Key
SECRET_KEY = os.environ['DEV_SECRET_KEY']

#DEBUG mode enabled 
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

SITE_PROTOCOL = 'http'
SITE_DOMAIN = 'localhost:8000'

#Flag to check if application is dockerized or not 
IS_DOCKERIZED = os.getenv('IS_DOCKERIZED', 'False') == 'True'
if IS_DOCKERIZED:  #use service names
    REDIS_HOST = 'redis'
    DB_HOST = 'postgres'
    EMAIL_HOST = 'smtp4dev'
    EMAIL_PORT = 25
else:  #use localhost 
    REDIS_HOST = 'localhost'
    DB_HOST = 'localhost'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025


#Apps and middleware used only in development 
INSTALLED_APPS += ['debug_toolbar', 'silk'] 

MIDDLEWARE += [
               'debug_toolbar.middleware.DebugToolbarMiddleware', 
               'silk.middleware.SilkyMiddleware'
               ]

#Internal IPS for Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',   
]

#Development database 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DEV_DB_NAME'], 
        'USER': os.environ['DEV_DB_USER'], 
        'PASSWORD': os.environ['DEV_DB_PASSWORD'], 
        'HOST': DB_HOST,
        'PORT': os.environ['DEV_DB_PORT'],
        'CONN_MAX_AGE': 60,  
        'CONN_HEALTH_CHECKS': True, 
        'OPTIONS': {
                    'connect_timeout': 10,
                }     
    }
}


#Development email settings 
EMAIL_HOST = EMAIL_HOST 
EMAIL_PORT = EMAIL_PORT   
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'no-reply@KhalifaHotels.com'  
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


#Configure Celery settings
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379/0' 


#Caching settings for production  
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache', 
        'LOCATION': f'redis://{REDIS_HOST}:6379/0', 
        'TIMEOUT': 60 * 10,  #10 minutes 
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                "max_connections": 50,      
                "retry_on_timeout": True 
            },
        }
    }
}


#Simple JWT configuration
SIMPLE_JWT = {
            'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
            'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
            'ROTATE_REFRESH_TOKENS': True,  
            'BLACKLIST_AFTER_ROTATION': True, 
            'UPDATE_LAST_LOGIN': True, 
            'AUTH_HEADER_TYPES': ('Bearer', ), 
        }


#disable timezone support in development
USE_TZ = False 

#Session security for development
SESSION_COOKIE_SECURE = False
