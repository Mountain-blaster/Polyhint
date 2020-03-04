from django.urls import path, include, re_path
from . import views
from rest_framework import routers
from .views import EleveViewSet
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('Eleve', EleveViewSet)

app_name = "GED"

urlpatterns = [
    path('perso/', include(router.urls)),
    ##Pages
    path('', views.home, name="Home"),
    path('add/', views.addEpreuve, name="add"),
    path('POLYHINT/connection/', views.connexion, name="connexion"),
    path('POLYHINT/inscription/', views.inscription, name="Inscription"),
    path('POLYHINT/Eleve/<int:id>', views.homeE, name="homeE"),
    path('POLYHINT/Prof/<int:id>', views.homeP, name="homeP"),
    path('POLYHINT/profile/<int:id>', views.profile, name='profile'),
    path('POLYHINT/edition/<int:id>', views.edit_profile, name='edit'),
    re_path(r'^POLYHINT/Eleve/(?P<username>[0-9A-Za-z_\-]+)/(?P<id>\d+)/$', views.otherprofile, name="others"),

    path('POLYHINT/Eleve/<int:id>/newTask', views.newtask, name='tache'),
    path('POLYHINT/Eleve/<int:id>/<str:tache>/ok', views.taskdone, name='taskdone'),

    path('POLYHINT/documentsEleve/PagePerso/<int:id>', views.pagePerso, name='pagePerso'),
    path('POLYHINT/documentsEleve/<int:id>', views.documentsEleve, name='documents'),
    path('POLYHINT/documentsEleve/Publication/<int:id>', views.PubEleve, name='PubEleve'),
    path('POLYHINT/documentsEleve/Publication/validation/<int:id>', views.Traitement, name='traitement'),
    re_path(r'^POLYHINT/documentsEleve/commentaires/(?P<titre_fichier>[-\w]+.*)/(?P<id>\d+)/$', views.commentaire, name='comments'),
    re_path(r'^POLYHINT/documentsEleve/Publie/(?P<titre_fichier>[-\w]+.*)/(?P<id>\d+)/$', views.newComments, name='newComment' ),
    path('POLYHINT/documentsEleve/SearchResult/<int:id>', views.search, name='search'),
    path('POLYHINT/documentsEleve/PagePerso/suppression/<str:titre_fichier>/<int:id>', views.deleteDoc, name='deleteDoc'),


    path('POLYHINT/Prof/document/<int:id>/', views.document_prof, name='doc_prof'),
    path('POLYHINT/Prof/document/suppression/<str:titre_fichier>/<int:id>/delete/', views.del_doc_prof, name='del_doc'),
    path('POLYHINT/Prof/document/publish/<int:id>/', views.pubProf, name="publish"),
path('POLYHINT/Prof/document/publish/<int:id>/validate', views.publish, name="traitementP"),

    ##Traitements
    path('POLYHINT/sauvegarde/', views.save, name='sauver'),
    re_path(r'^activate/(?P<username>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.activate_account, name='activate'),
    path('POLYHINT/connection/login/', views.valider, name='valider'),
    path("POLYHINT/connection/", views.logout_view, name="Deconnecter"),
    path('POLYHINT/recuperation/', views.recover, name='recover'),
    path('POLYHINT/page-recuperation/', views.recoverpage, name='recoverpage'),
    #re_path(r'^test-delete/$', views.test_delete, name='test_delete'),
    #re_path(r'^test-session/$', views.test_session, name='test_session'),
    #re_path(r'^access-session-data/$', views.access_session_data, name='access_session_data'),
    #re_path(r'^delete-session-data/$', views.delete_session_data, name='delete_session_data'),
]
