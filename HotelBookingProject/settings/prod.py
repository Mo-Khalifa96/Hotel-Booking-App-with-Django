import os 
from .base import * 
import dj_database_url   
from datetime import timedelta


#Production Security Key
SECRET_KEY = os.environ['PROD_SECRET_KEY']  

#Debugging mode off
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

SITE_PROTOCOL = os.getenv('SITE_PROTOCOL')
SITE_DOMAIN = os.getenv('SITE_DOMAIN')


#Database for production
DATABASES = {
    'default': dj_database_url.config()
}


#Email Settings for production
EMAIL_HOST = os.environ['BREVO_SMTP_SERVER']
EMAIL_HOST_USER = os.environ['BREVO_SMTP_USER']
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
            'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
            'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
            'ROTATE_REFRESH_TOKENS': True,  
            'BLACKLIST_AFTER_ROTATION': True,
            'UPDATE_LAST_LOGIN': True, 
            'AUTH_HEADER_TYPES': ('Bearer', ), 
        }


#Security configurations 
SESSION_COOKIE_SECURE = True 
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
