import os 
from .base import * 
from datetime import timedelta
import dj_database_url   

#Production Security Key
SECRET_KEY = os.environ['PROD_SECRET_KEY']  

#Debugging mode off
DEBUG = False

#ALLOWED_HOSTS = ['domain-name-here']

SITE_PROTOCOL = 'https'
#SITE_DOMAIN = 'domain-name-here.com' 


#Database for production
DATABASES = {
    'default': dj_database_url.config()  #automatically identifies and configures database from the DATABASE_URL env variable
}


#Email Settings for production
EMAIL_HOST = os.environ['BREVO_SMTP_SERVER']
EMAIL_HOST_USER = os.environ['MBREVOSMTP_USER']
EMAIL_HOST_PASSWORD = os.environ['BREVO_SMTP_PASSWORD']
EMAIL_PORT = int(os.environ['BREVO_SMTP_PORT'])
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@KhalifaHotels.com'  
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


#Celery Broker
CELERY_BROKER_URL = os.environ['REDIS_URL']  


#Caching settings for production 
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache', 
        'LOCATION': os.environ['REDIS_URL'], 
        'TIMEOUT': 60*10,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                "max_connections": 50,
                "retry_on_timeout": True 
            },
        }
    }
}


#JWT's settings for authentication 
SIMPLE_JWT = {
            'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
            'REFRESH_TOKEN_LIFETIME': timedelta(days=60*12),
            'ROTATE_REFRESH_TOKENS': True,  
            'BLACKLIST_AFTER_ROTATION': True,
            'UPDATE_LAST_LOGIN': True, 
            'AUTH_HEADER_TYPES': ('Bearer', ), 
        }


#Session security for production
SESSION_COOKIE_SECURE = True 