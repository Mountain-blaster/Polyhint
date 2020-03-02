from django.contrib import admin
from django.apps import apps
# Register your models here.

mode = apps.get_models()
for mod in mode:
    try:
        admin.site.register(mod)
    except admin.sites.AlreadyRegistered:
        pass
