from .settings import *
import dj_database_url
import storages




DEBUG = True
TEMPLATE_DEBUG = False

SECRET_KEY = 'd%5_y%y8&cu2k%1j*k80f$+qd7ix5q$&jkplokgsdo4=o#)3ek'

ALLOWED_HOSTS = ['polyhint.herokuapp.com', 'polyhint2.herokuapp.com']

DATABASES['default'] = dj_database_url.config()

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']

INSTALLED_APPS += ('storages',)

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorages'

#AWS_QUERYSTRING_AUTH = False
#AWS_ACCESS_KEY_ID = ['AKIAIYKJDOYIV5UATSUA']
#AWS_SECRET_ACCESS_KEY = ['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']
#AWS_STORAGE_BUCKET_NAME = ['polyhint2']
#MEDIA_URL = 'http://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
#DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_STORAGE_BUCKET_NAME = 'polyhint2'
AWS_S3_REGION_NAME = 'us-east-2'  # e.g. us-east-2
AWS_ACCESS_KEY_ID = 'AKIAIYKJDOYIV5UATSUA'
AWS_SECRET_ACCESS_KEY = 'hP9mmdCJnvbHHoz+JT0I3AqrDNKwdQGxItMxnx1P'


MEDIA_URL = 'http://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME

DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

