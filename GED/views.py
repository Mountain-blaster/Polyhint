import datetime
import os
import random
import string
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import viewsets
from .serializers import EleveSerializer
from rest_framework.authentication import TokenAuthentication
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from GED.permis import *
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from .forms import *


class EleveViewSet(viewsets.ModelViewSet):
    serializer_class = EleveSerializer
    queryset = Eleve.objects.all()
    authentication_classes = (TokenAuthentication,)


##LES PAGES

def home(request):
    sujets = Sujet.objects.all()
    list4 = list(Sujet.objects.filter(annee__gte=2016).order_by('annee'))[-4:]
    list4.reverse()
    return render(request, 'GED/home.html',{'sujets': sujets,
                                             'list4': list4})


@login_required(login_url="POLYHINT/connection/")
def homeE(request, id):
    newuser = User.objects.get(pk=id)
    user = Eleve.objects.get(user=newuser)
    taches = Tache.objects.filter(eleve_id=user, state=False).order_by('tache_time')
    taskfinish = Tache.objects.filter(eleve_id=user, state=True).order_by('tache_time')
    notifs = list(Notifications.objects.exclude(eleve_id=user).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, 'GED/index.html', {'user': user,
                                              'taches': taches,
                                              'taskfinish': taskfinish,
                                              'notifs': notifs,
                                              'nbre': nbre})


def homeP(request, id):
    newuser = User.objects.get(pk=id)
    user = Professeur.objects.get(userp=newuser)
    notifs = list(Notifications.objects.exclude(prof_id=user).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, 'GED/indexP.html', {'user': user,
                                               'notifs': notifs,
                                               'nbre': nbre})


def inscription(request):
    dept = Eleve.objects.all()
    return render(request, 'GED/inscription.html', {'departements': dept})


def recoverpage(request):
    return render(request, 'GED/forgotpassword.html')


def connexion(request):
    return render(request, "GED/connexion.html")


def commentaire(request, titre_fichier, id):
    doc = Document.objects.get(titre_fichier=titre_fichier)
    newuser = User.objects.get(pk=id)
    user = Eleve.objects.get(user=newuser)
    uploader = Eleve.objects.get(user=User.objects.get(user=doc.eleve_id))
    com = Commentaire.objects.filter(id_doc=doc)
    nbre_comments = len(com)
    notifs = list(Notifications.objects.exclude(eleve_id=user).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    if nbre_comments==0:
        nocomment = "soyez le premier a commenter"
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'nocomment': nocomment,
                                                     'nbre_comments': nbre_comments,
                                                     'uploader': uploader,
                                                     'notifs': notifs,
                                                     'nbre': nbre})
    else:
        listuser = [i.user_id for i in com]
        comments = list(zip(listuser, com))
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'comments': comments,
                                                     'nbre_comments': nbre_comments,
                                                     'uploader': uploader})



def newComments(request, titre_fichier, id):
    titre = str(titre_fichier)
    doc = Document.objects.get(titre_fichier=titre)
    user = Eleve.objects.get(user=User.objects.get(pk=id))
    uploader = Eleve.objects.get(user=User.objects.get(user=doc.eleve_id))
    notifs = list(Notifications.objects.exclude(eleve_id=user).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    if doc.comments == True:
        newComment = Commentaire()
        newComment.user_id = Eleve.objects.get(user=User.objects.get(pk=id))
        newComment.id_doc = doc
        newComment.contents = request.POST['contents']
        newComment.save()
        com = Commentaire.objects.filter(id_doc=doc)
        nbre_comments = len(com)
        notifsCom = Notifications()
        contenu = user.user.first_name+" a commenté "+titre+" publié par "+uploader.user.first_name
        notifsCom.notifs = contenu
        notifsCom.eleve_id = user
        notifsCom.save()
        if nbre_comments == 0:
            nocomment = "soyez le premier a commenter"
            return render(request, 'GED/comments.html', {'user': user,
                                                         'doc': doc,
                                                         'nocomment': nocomment,
                                                         'nbre_comments': nbre_comments,
                                                         'uploader': uploader,
                                                         'notifs': notifs,
                                                         'nbre': nbre})
        else:
            listuser = [i.user_id for i in com]
            comments = list(zip(listuser, com))
            return render(request, 'GED/comments.html', {'user': user,
                                                         'doc': doc,
                                                         'comments': comments,
                                                         'nbre_comments': nbre_comments,
                                                         'uploader': uploader})
    else:
        nocomment = "commentaire non autorisé pour ce document!"
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'nocomment': nocomment,
                                                     'nbre_comments': 0,
                                                     'uploader': uploader,
                                                     'notifs': notifs,
                                                     'nbre': nbre})


def profile(request, id):

    newuser = User.objects.get(pk=id)

    try:
        e = Eleve.objects.get(user=newuser)
        role = 'Eleve'

    except Eleve.DoesNotExist:
        p = Professeur.objects.get(userp=newuser)
        role = 'Professeur'

    if role == 'Eleve':
        e = Eleve.objects.get(user=newuser)
        age = datetime.date.today().year - e.date_birth.year
        notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
        notifs.reverse()
        nbre = len(notifs)
        return render(request, 'GED/userprofile.html', {'user': e,
                                                        'role': role,
                                                        'age': age,
                                                        'notifs': notifs,
                                                        'nbre': nbre})

    elif role == 'Professeur':
        p = Professeur.objects.get(userp=newuser)
        age = datetime.date.today().year - p.date_birth.year
        notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
        notifs.reverse()
        nbre = len(notifs)
        return render(request, 'GED/userprofile.html', {'user': p,
                                                        'role': role,
                                                        'age': age,
                                                        'notifs': notifs,
                                                        'nbre': nbre})

    else:
        erreur = "<h4>Impossible d'afficher le profile!!</h4> Une erreur technique veuillez réessayer lors de votre prochaine connection"
        return render(request, 'GED/404.html', {'erreur', erreur})



def edit_profile(request, id):
    newuser = User.objects.get(pk=id)
    try:
        Eleve.objects.get(user=newuser)
        role = 'Eleve'
    except Eleve.DoesNotExist:
        Professeur.objects.get(userp=newuser)
        role = 'Professeur'

##################################################################################################

    if role == 'Eleve':
        e = Eleve.objects.get(user=newuser)

        if 'btnform1' in request.POST:

            newuser.username = request.POST['username']
            newuser.first_name = request.POST['first_name']
            newuser.last_name = request.POST['last_name']
            newuser.email = request.POST['email']
            newuser.save()
            role = "Eleve"
            notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
            notifs.reverse()
            nbre = len(notifs)
            return render(request, 'GED/editer_profile.html', {'user': e,
                                                               'role': role,
                                                               'notifs': notifs,
                                                               'nbre': nbre})

        elif 'btnform2' in request.POST:
            e.telephone = request.POST['telephone']
            e.filiere = request.POST['filiere']
            e.niveau = request.POST['niveau']
            e.save()
            role = "Eleve"
        elif 'btnform3' in request.POST:
            e.about = request.POST['about']
            e.save()
            role = "Eleve"
        elif 'btnform4' in request.POST:
            form = PassForm(request.POST)
            if form.is_valid():
                newuser.set_password(request.POST['password'])
                newuser.save()
                role = "Eleve"
                notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
                notifs.reverse()
                nbre = len(notifs)
                return render(request, 'GED/editer_profile.html', {'user': e,
                                                                   'role': role,
                                                                   'notifs': notifs,
                                                                   'nbre': nbre})
            else:
                notifs = list(Notifications.objects.exclude(eleve_id=id))
                nbre = len(notifs)
                erreur = "<h4>Desolé une erreur est survenue</h4>Veuillez Reessayer plus tard!!"
                return render(request, 'GED/404.html', {'user': e,
                                                        'role': role,
                                                        'erreur': erreur,
                                                        'notifs': notifs,
                                                        'nbre': nbre})



        elif 'btnform0' in request.POST:
            form = ElProfileForm(request.POST, request.FILES)
            if form.is_multipart():
                a = e.profile.path
                e.profile = request.FILES['profile']
                e.save()
                os.remove(a)
                role = "Eleve"
                notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
                notifs.reverse()
                nbre = len(notifs)
                return render(request, 'GED/editer_profile.html', {'user': e,
                                                                   'role': role,
                                                                   'notifs': notifs,
                                                                   'nbre': nbre})
            else:
                notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
                notifs.reverse()
                nbre = len(notifs)
                role = "Eleve"
                erreur = "<h4>Desolé une erreur est survenue</h4>Veuillez Reessayer plus tard!!"
                return render(request, 'GED/404.html', {'user': e,
                                                        'role': role,
                                                        'erreur': erreur,
                                                        'notifs': notifs,
                                                        'nbre': nbre})

        notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
        notifs.reverse()
        nbre = len(notifs)
        return render(request, 'GED/editer_profile.html', {'user': e,
                                                           'role': role,
                                                           'notifs': notifs,
                                                           'nbre': nbre})

##################################################################################################

    elif role == 'Professeur':

        p = Professeur.objects.get(userp=newuser)

        if request.method == 'POST':
            if 'btnform1' in request.POST:
                form = UserForm(request.POST)
                if form.is_valid():
                    newuser.username = request.POST['username']
                    newuser.first_name = request.POST['first_name']
                    newuser.last_name = request.POST['last_name']
                    newuser.email = request.POST['email']
                    newuser.save()
                else:
                    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
                    notifs.reverse()
                    nbre = len(notifs)
                    erreur = form.errors
                    return render(request, 'GED/404.html', {'user': p,
                                                            'role': role,
                                                            'erreur': erreur,
                                                            'notifs': notifs,
                                                            'nbre': nbre})

            elif 'btnform2' in request.POST:
                form = ProfForm(request.POST)
                if form.is_valid():
                    p.telephone = request.POST['telephone']
                    p.save()
                else:
                    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
                    notifs.reverse()
                    nbre = len(notifs)
                    erreur = form.errors
                    return render(request, 'GED/404.html', {'user': p,
                                                            'role': role,
                                                            'erreur': erreur,
                                                            'notifs': notifs,
                                                            'nbre': nbre})

            elif 'btnform3' in request.POST:
                form = ProfForm(request.POST)
                if form.is_valid():

                    p.about = request.POST['about']
                    p.save()
                else:
                    erreur = form.errors
                    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
                    notifs.reverse()
                    nbre = len(notifs)
                    return render(request, 'GED/404.html', {'user': p,
                                                            'role': role,
                                                            'erreur': erreur,
                                                            'notifs': notifs,
                                                            'nbre': nbre})

            elif 'btnform4' in request.POST:
                form = PassForm(request.POST)
                if form.is_valid():

                    newuser.set_password(request.POST['password'])
                    newuser.save()
                else:
                    erreur = form.errors
                    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
                    notifs.reverse()
                    nbre = len(notifs)
                    return render(request, 'GED/404.html', {'user': p,
                                                            'role': role,
                                                            'erreur': erreur,
                                                            'notifs': notifs,
                                                            'nbre': nbre})

            elif 'btnform0' in request.POST:
                form = ProfProfileForm(request.POST, request.FILES)
                try:
                    if form.is_multipart():
                        a = p.profile.path
                        p.profile = request.FILES['profile']
                        p.save()
                        os.remove(a)

                except:
                    erreur = "request.FILES n'a pas pu obtenir l'image téléchargée de l'entrée"
                    link = "{% url 'edit' user.user.id %}"
                    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
                    notifs.reverse()
                    nbre = len(notifs)
                    return render(request, 'GED/404.html', {'user': p,
                                                            'role': role,
                                                            'erreur': erreur,
                                                            'link': link,
                                                            'notifs': nbre,
                                                            'nbre': nbre})
        notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
        notifs.reverse()
        nbre = len(notifs)
        return render(request, 'GED/editer_profile.html', {'user': p,
                                                           'role': role,
                                                           'notifs':notifs,
                                                           'nbre': nbre})


def otherprofile(request, username, id):
    newuser = User.objects.get(pk=id)
    user = Eleve.objects.get(user=newuser)
    role = "Eleve"
    newother = User.objects.get(username=username)
    other = Eleve.objects.get(user=newother)
    notifs = list(Notifications.objects.exclude(eleve_id=user).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, 'GED/othersprofile.html', {'other': other,
                                                      'user': user,
                                                      'role': role,
                                                      'notifs': notifs,
                                                      'nbre':nbre})


##################################################################################################



def documentsEleve(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    mats = Document.LIST_MATIERE
    fils = Document.LIST_FILIERE
    doc = Document.objects.filter(prof_id=None)
    tops = list(Document.objects.filter(prof_id=None).order_by('updload_date'))[-8:]
    listuser = [i.eleve_id for i in tops]
    top = list(zip(listuser, tops))
    top.reverse()
    list1 = top[:4]
    list2 = top[4:]
    notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, "GED/table.html", {'user': e,
                                              'docs': doc,
                                              'list1': list1,
                                              'list2': list2,
                                              'fils': fils,
                                              'mats': mats,
                                              'notifs': notifs,
                                              'nbre': nbre})


def PubEleve(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    doc = Document.LIST_MATIERE
    matiere = [j for (i, j) in doc]
    fil = Document.LIST_FILIERE
    filiere = [j for (i,j) in fil]
    notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, 'GED/PubEleve.html', {'user': e,
                                                 'matieres': matiere,
                                                 'filieres': filiere,
                                                 'notifs':notifs,
                                                 'nbre':nbre})


def Traitement(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    files = request.FILES.getlist('fichier')
    i = 0
    for f in files:
        newDoc = Document()
        newDoc.eleve_id = e
        newDoc.fichier = f
        newDoc.titre_fichier = request.POST['titre_fichier']+"_"+str(i)
        i += 1
        newDoc.matiere = request.POST['matiere']
        newDoc.filiere = request.POST['filiere']
        newDoc.description = request.POST['description']
        if request.POST['comments'] == "OUI":
            newDoc.comments = True
        else:
            newDoc.comments = False
        newDoc.save()
        newnotif = Notifications()
        newnotif.eleve_id = e
        notif = str(e.user.first_name) + " a publier un document"
        newnotif.notifs = notif
        newnotif.save()
    notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    success = 'cest fait!! <a href ="{% url "GED:documents" user.user.id %}">Retourner</a> à la page précedente'
    return render(request, 'GED/PubEleve.html', {'user': e,
                                                 'success': success,
                                                 'notifs':notifs,
                                                 'nbre':nbre})



def search(request, id):
    e = Eleve.objects.get(user=User.objects.get(pk=id))
    doc = list(Document.objects.filter(prof_id=None))
    mats = Document.LIST_MATIERE
    fils = Document.LIST_FILIERE
    tops = list(Document.objects.order_by('updload_date'))[-8:]
    listuser = [i.eleve_id for i in tops]
    top = list(zip(listuser, tops))
    top.reverse()
    list1 = top[:4]
    list2 = top[4:]
    titre = request.GET['titre_fichier']
    if request.GET['titre_fichier'] == "":
        doc = doc + list(Document.objects.all())
    else:
        doc = doc+list(Document.objects.filter(titre_fichier__contains=titre))
    doc = list(set(doc) & set(Document.objects.filter(matiere__icontains=request.GET['matiere'])))
    doc = list(set(doc) & set(Document.objects.filter(filiere__icontains=request.GET['filiere'])))
    doc = list(set(doc) & set(Document.objects.filter(updload_date__year=request.GET['year'])))
    doc = list(set(doc) & set(Document.objects.filter(updload_date__month=request.GET['month'])))
    notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)

    return render(request, 'GED/table.html', {'docs': doc,
                                              'user': e,
                                              'list1': list1,
                                              'list2': list2,
                                              'fils': fils,
                                              'mats': mats,
                                              'notifs':notifs,
                                              'nbre':nbre})


def pagePerso(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    mydocs = Document.objects.filter(eleve_id=e)
    docprof = Document.objects.filter(eleve_id=None, niveau=e.niveau, filiere=e.filiere, share=True)
    lastdoc = list(docprof.order_by('updload_date'))[-4:]
    listprof = [e.prof_id for e in lastdoc]
    lastdoc = list(zip(listprof, lastdoc))
    lastdoc.reverse()
    notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    context={'user': e,
             'docs': mydocs,
             'profs': docprof,
             'lastdoc': lastdoc,
             'notifs':notifs,
             'nbre':nbre}
    return render(request, 'GED/pagePerso.html', context)

def deleteDoc(request, titre_fichier, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    mydocs = Document.objects.filter(eleve_id=e)
    doc = Document.objects.get(titre_fichier=titre_fichier)
    doc.delete()
    notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, 'GED/pagePerso.html', {'user': e,
                                                  'docs': mydocs,
                                                  'notifs':notifs,
                                                  'nbre':nbre})



###PROF#####

def pubProf(request, id):
    newuser = User.objects.get(pk=id)
    p = Professeur.objects.get(userp=newuser)
    doc = Document.LIST_MATIERE
    matiere = [j for (i, j) in doc]
    fil = Document.LIST_FILIERE
    filiere = [j for (i,j) in fil]
    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    return render(request, 'GED/publish.html', {'user': p,
                                                'matieres': matiere,
                                                'filieres': filiere,
                                                'notifs':notifs,
                                                'nbre':nbre})


def publish(request, id):
    files = request.FILES.getlist('fichier')
    newuser = User.objects.get(pk=id)
    p = Professeur.objects.get(userp=newuser)
    i=0
    for f in files:
        prof_id = p
        titre_fichier = request.POST['titre_fichier']+str(i)
        i+=1
        description = request.POST['description']
        filiere = request.POST['filiere']
        niveau = request.POST['niveau']
        matiere = request.POST['matiere']
        fichier = f
        type= os.path.splitext(str(f))[1]
        newdoc = Document(fichier=fichier, titre_fichier=titre_fichier, description=description, filiere=filiere, type=type, niveau=niveau, matiere=matiere, prof_id=prof_id)
        if request.POST['share'] == "OUI":
            newdoc.share = True
        newdoc.save()
        newnotif = Notifications()
        newnotif.prof_id=p
        notif = str(p.userp.first_name)+" a publier un document"
        newnotif.notifs = notif
        newnotif.save()
    notifs = list(Notifications.objects.exclude(prof_id=p).order_by('time_notif'))[-8:]
    notifs.reverse()
    nbre = len(notifs)
    doc = Document.objects.filter(prof_id=p)
    return render(request, "GED/table_prof.html", {'doc': doc,
                                                   'user': p,
                                                   'notifs':notifs,
                                                   'nbre':nbre})

def document_prof(request, id):

    newuser = User.objects.get(pk=id)
    p = Professeur.objects.get(userp=newuser)
    doc = Document.objects.filter(prof_id=p)
    return render(request, "GED/table_prof.html", {'doc': doc,
                                                   'user': p})

def del_doc_prof(request, titre_fichier, id):
    newuser = User.objects.get(pk=id)
    p = Professeur.objects.get(userp=newuser)
    mydocs = Document.objects.filter(prof_id=p)
    doc = Document.objects.get(titre_fichier=titre_fichier)
    doc.delete()
    return render(request, "GED/delete_prof.html")


def valider(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        try:
            e = Eleve.objects.get(user=user)
            role = "Eleve"
            del e
        except Eleve.DoesNotExist:
            p = Professeur.objects.get(userp=user)
            role = "Professeur"
            del p
        except:
            role = "admin"
        if role == "Eleve":
            if user.is_active:
                login(request, user)
                e = Eleve.objects.get(user=user)
                notifs = list(Notifications.objects.exclude(eleve_id=e).order_by('time_notif'))[-8:]
                notifs.reverse()
                nbre = len(notifs)
                taches = Tache.objects.filter(eleve_id=e, state=False).order_by('tache_time')
                taskfinish = Tache.objects.filter(eleve_id=e, state=True).order_by('tache_time')
                return render(request, 'GED/index.html', {'user': e,
                                                          'taches': taches,
                                                          'taskfinish': taskfinish,
                                                          'notifs': notifs,
                                                          'nbre': nbre})
            else:
                erreur = "Compte pas encore activé"
                return render(request, 'GED/connexion.html', {'errno': erreur})
        elif role == "Professeur":
            if user.is_active:
                login(request, user)
                p = Professeur.objects.get(userp=user)
                return render(request, 'GED/indexP.html', {'user': p})
            else:
                erreur = "Compte pas encore activé"
                return render(request, 'GED/connexion.html', {'errno': erreur})
        elif role == "admin":
            login(request, user)
            return redirect('/admin/')
    else:
        erreur = "nom d'utilisiteur ou mot de passe incorrecte"
        return render(request, 'GED/connexion.html', {'errno': erreur})

def csrf_failure(request, reason=""):
    erreur = {'erreur': 'some custom messages'}
    return render(request, 'GED/404page.html', erreur)


# DECONNECTION
@login_required(login_url="POLYHINT/connection/")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('POLYHINT/connection/')


def email_test(email):
    if User.objects.filter(email=email).exists():
        return True
    return False


def save(request):
    # Instanciations
    newEleve = Eleve()
    newProf = Professeur()

    # recuperation
    username = request.GET['username']
    password = request.GET['password']
    email = request.GET['email']
    if email.split("@")[-1] != "ept.sn":
        erreur = "les emails doivent se terminer par @ept.sn"
        return render(request, 'GED/inscription.html', {'errno': erreur})
    try:
        role = request.GET['role']
    except MultiValueDictKeyError:
        erreur = 'Vous devez definir votre profile: Eleve ou Professeur'
        return render(request, 'GED/404page.html', {'erreur': erreur})
    repassword = request.GET['repassword']

    test = email_test(email)
    if test == False:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = request.GET['prenom']
        user.last_name = request.GET['nom']
        user.is_active = False
    else:
        erreur = "cet email est associé à un compte!"
        return render(request, 'GED/inscription.html', {'errno': erreur})

    if role == "Eleve":
        choix = request.GET['filiere']
        newEleve.sexe = request.GET['gender']
        newEleve.user = user
        newEleve.date_birth = request.GET['birth']
        newEleve.telephone = request.GET['telephone']
        newEleve.niveau = request.GET['niveau']
        newEleve.filiere = choix

        if password == repassword:
            current_site = get_current_site(request)
            email_subject = 'Activer votre compte'
            message = render_to_string('GED/activate_account.html', {
                'user': newEleve,
                'domain': current_site.domain,
                'username': user.username,
                'token': account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            user.groups.add(Group.objects.get(name='Eleve'))
            user.save()
            newEleve.save()
            succes = "Votre compte a ete crée avec succès veuillez ouvrir votre boite email pour l'activer"
            return render(request, 'GED/inscription.html', {'success': succes})
        else:
            choix = Eleve.objects.all()
            error = "Incorrect"
            return HttpResponse(render(request, 'GED/inscription.html', {'erreur': error, 'departements': choix}))

    else:

        newProf.sexe = request.GET['gender']
        newProf.userp = user
        newProf.date_birth = request.GET['birth']

        if password == repassword:
            current_site = get_current_site(request)
            email_subject = 'Activer votre compte'
            message = render_to_string('GED/activate_account.html', {
                'user': newProf,
                'domain': current_site.domain,
                'username': user.username,
                'token': account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            user.groups.add(Group.objects.get(name='Professeur'))
            user.save()
            newProf.save()
            succes = "Votre compte a ete crée avec succès veuillez ouvrir votre boite email pour l'activer"
            return render(request, 'GED/inscription.html', {'success': succes})
        else:
            dept = Eleve.objects.all()
            error = "Incorrect"
            return render(request, 'GED/inscription.html', {'erreur': error, 'departements': dept})


def activate_account(request, username, token):
    user = User.objects.get(username=username)
    user.is_active = True
    user.save()
    ok = "Compte activé avec succès!!"
    return render(request, 'GED/connexion.html', {'ok': ok})


def recover(request):
    recup = request.POST['recup']
    if recup is not None:
        try:
            userforget = User.objects.get(email=recup)
        except:
            userforget = User.objects.get(username=recup)
        alert1 = "Nous vous avons envoyé un lien a l'adresse :"
        alert2 = "Veuillez ouvrir votre boite de reception"
        current_site = get_current_site(request)
        email_subject = 'Demande de recuperation de mot de passe'
        #####################Generation d'un mot de passe aleatoire#####################
        chaine = string.ascii_letters + string.digits
        randpass = "".join(random.choice(chaine) for i in range(random.randint(8, 16)))
        ################################################################################
        message = render_to_string('GED/recupPass.html', {
            'userforget': userforget,
            'domain': current_site.domain,
            'username': userforget.username,
            'password': randpass,
            'token': account_activation_token.make_token(userforget),
        })
        to_email = userforget.email
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        userforget.set_password(randpass)
        userforget.save()
        return render(request, 'GED/forgotpassword.html', {'alert1': alert1,
                                                           'alert2': alert2,
                                                           'userforget': userforget})
    else:
        alert1 = "Compte inexistant.. Veuillez renseigner les bonnes informations"
        return render(request, 'GED/forgotpassword.html', {'alert1': alert1})


#Some greats!!!!

def newtask(request, id):
    newuser = User.objects.get(pk=id)
    user = Eleve.objects.get(user=newuser)
    try:
        newtache = Tache()
        newtache.tache = request.GET['tache']
        newtache.tache_time = request.GET['tache_time']
        newtache.eleve_id = user
        newtache.save()
        taches = Tache.objects.filter(eleve_id=user, state=False).order_by('tache_time')
        taskfinish = Tache.objects.filter(eleve_id=user, state=True).order_by('tache_time')
        return render(request, 'GED/index.html', {'user': user,
                                                  'taches': taches,
                                                  'taskfinish': taskfinish})
    except:
        taskfinish = Tache.objects.filter(eleve_id=user, state=True).order_by('tache_time')
        taches = Tache.objects.filter(eleve_id=user, state=False).order_by('tache_time')
        return render(request, 'GED/index.html', {'user': user,
                                                  'taches': taches,
                                                  'taskfinish': taskfinish})


def taskdone(request, id, tache):
    user = Eleve.objects.get(user=User.objects.get(pk=id))
    task = Tache.objects.get(tache=tache)
    if 'done' in request.GET:

        task.state = True
        task.save()
        tache = Tache.objects.filter(eleve_id=user, state=False).order_by('tache_time')
        taskfinish = Tache.objects.filter(eleve_id=user, state=True).order_by('tache_time')
        return render(request, 'GED/index.html', {'user':user,
                                                  'taches': tache,
                                                  'taskfinish': taskfinish})


def addEpreuve(request):
    if len(request.POST) != 0:
        username = request.POST['username']
        password = request.POST['password']
        newuser = authenticate(username=username, password=password)
        if newuser is not None:
            eleve = Eleve.objects.get(user=newuser)
            newSujet = Sujet()
            newSujet.uploader = eleve
            newSujet.titre = request.POST['titre']
            newSujet.annee = int(request.POST['annee'])
            newSujet.epreuve = request.FILES['epreuve']
            newSujet.save()
            succes = "Partage réussi!"
            return redirect('GED:Home')
        else:
            erreur = "Vous n\'êtes pas autorisé pour ce service!"
            sujets = Sujet.objects.all()
            list4 = list(Sujet.objects.filter(annee__gte=2016).order_by('annee'))[-4:]
            list4.reverse()
            return render(request, 'GED/home.html', {'erreur': erreur,
                                                     'sujets': sujets,
                                                     'list4': list4})
