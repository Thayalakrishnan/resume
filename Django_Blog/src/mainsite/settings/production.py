from .base import *

# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = False
ALLOWED_HOSTS = []              # we want to add the ip addres of our server

'''
# Database
# in the case where you would have two separate database configurations, one for
# production and one for development, we can separete the two amongst these two
# files 

# furthermore, here we are setting up our database for postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'your-db-name',
        'USER': 'your-db-user-name',
        'PASSWORD': 'your-db-password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

'''

'''
STRIPE_PUBLIC_KEY=
STRIPE_PRIVATE_KEY=

'''