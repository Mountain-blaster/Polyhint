from django.contrib import admin
from django.apps import apps
from GED.models import *
# Register your models here.



class ModelEleve(admin.ModelAdmin):
    list_display = ('user', 'filiere', 'niveau', 'joindate', 'avertissement')
    list_filter = ('user', 'niveau', 'filiere')
    date_hierarchy = 'joindate'

class ModelProf(admin.ModelAdmin):
    list_display = ('userp', 'joindate')
    list_filter = ('userp', )

class ModelDocument(admin.ModelAdmin):
    list_display = ('titre_fichier', 'type', 'matiere', 'niveau', 'filiere', 'updload_date', 'note')
    list_filter = ('titre_fichier', 'type', 'matiere', 'niveau', 'filiere', 'updload_date')
    date_hierarchy = 'updload_date'

class ModelComments(admin.ModelAdmin):
    list_display = ('user_id', 'id_doc', 'date_comments')
    list_filter = ('date_comments',)
    date_hierarchy = 'date_comments'


class ModelSujet(admin.ModelAdmin):
    list_display = ('titre', 'annee', 'uploader')
    list_filter = ('titre', 'annee',)


class ModelSocialProfile(admin.ModelAdmin):
    list_display = ('network', 'url')
    list_filter = ('network',)



admin.site.register(Eleve, ModelEleve)
admin.site.register(Professeur, ModelProf)
admin.site.register(Document, ModelDocument)
admin.site.register(Commentaire, ModelComments)
admin.site.register(SocialProfile, ModelSocialProfile)
admin.site.register(Tache)
admin.site.register(Notifications)
admin.site.register(Sujet, ModelSujet)