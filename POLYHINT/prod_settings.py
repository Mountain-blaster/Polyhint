from .settings import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = False

SECRET_KEY = 'd%5_y%y8&cu2k%1j*k80f$+qd7ix5q$&jkplokgsdo4=o#)3ek'

ALLOWED_HOSTS = ['polyhint.herokuapp.com']

DATABASES['default'] = dj_database_url.config()

