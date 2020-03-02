from django.contrib import admin
from django.apps import apps
from GED.models import *
# Register your models here.



class ModelEleve(admin.ModelAdmin):
    list_display = ('user', 'filiere', 'niveau', 'joindate', 'avertissement')
    list_filter = ('user', 'niveau', 'filiere')
    date_hierarchy = 'joindate'


admin.site.register(Eleve, ModelEleve)