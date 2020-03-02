import datetime
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
    return render(request, 'GED/home.html')


@login_required(login_url="POLYHINT/connection/")
def homeE(request, id):
    newuser = User.objects.get(pk=id)
    user = Eleve.objects.get(user=newuser)
    taches = Tache.objects.filter(eleve_id=user, state=False).order_by('tache_time')
    taskfinish = Tache.objects.filter(eleve_id=user, state=True).order_by('tache_time')
    return render(request, 'GED/index.html', {'user': user,
                                              'taches': taches,
                                              'taskfinish': taskfinish})


def homeP(request, id):
    newuser = User.objects.get(pk=id)
    user = Professeur.objects.get(userp=newuser)
    return render(request, 'GED/indexP.html', {'user': user})


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
    if nbre_comments==0:
        nocomment = "soyez le premier a commenter"
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'nocomment': nocomment,
                                                     'nbre_comments': nbre_comments,
                                                     'uploader': uploader})
    else:
        listuser = [i.user_id for i in com]
        comments = list(zip(listuser, com))
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'comments': comments,
                                                     'nbre_comments': nbre_comments,
                                                     'uploader': uploader})



def newComments(request, titre_fichier, id):
    newComment = Commentaire()
    newComment.user_id = Eleve.objects.get(user=User.objects.get(pk=id))
    titre = str(titre_fichier)
    doc = Document.objects.get(titre_fichier=titre)
    newComment.id_doc = doc
    newComment.contents = request.POST['contents']
    newComment.save()
    user = Eleve.objects.get(user=User.objects.get(pk=id))
    com = Commentaire.objects.filter(id_doc=doc)
    nbre_comments = len(com)
    uploader = Eleve.objects.get(user=User.objects.get(user=doc.eleve_id))
    if nbre_comments == 0:
        nocomment = "soyez le premier a commenter"
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'nocomment': nocomment,
                                                     'nbre_comments': nbre_comments,
                                                     'uploader': uploader})
    else:
        listuser = [i.user_id for i in com]
        comments = list(zip(listuser, com))
        return render(request, 'GED/comments.html', {'user': user,
                                                     'doc': doc,
                                                     'comments': comments,
                                                     'nbre_comments': nbre_comments,
                                                     'uploader': uploader})


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
        return render(request, 'GED/userprofile.html', {'user': e, 'role': role, 'age': 12})

    elif role == 'Professeur':
        p = Professeur.objects.get(userp=newuser)
        age = datetime.date.today().year - p.date_birth.year
        return render(request, 'GED/userprofile.html', {'user': p, 'role': role, 'age': age})

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
            return render(request, 'GED/editer_profile.html', {'user': e, 'role': role})

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
                return render(request, 'GED/editer_profile.html', {'user': e, 'role': role})
            else:
                erreur = "<h4>Desolé une erreur est survenue</h4>Veuillez Reessayer plus tard!!"
                return render(request, 'GED/404.html', {'user': e, 'role': role, 'erreur': erreur})



        elif 'btnform0' in request.POST:
            form = ElProfileForm(request.POST, request.FILES)
            if form.is_multipart():
                a = e.profile.path
                e.profile = request.FILES['profile']
                e.save()
                os.remove(a)
                role = "Eleve"
                return render(request, 'GED/editer_profile.html', {'user': e, 'role': role})
            else:
                role = "Eleve"
                erreur = "<h4>Desolé une erreur est survenue</h4>Veuillez Reessayer plus tard!!"
                return render(request, 'GED/404.html', {'user': e, 'role': role, 'erreur': erreur})




        return render(request, 'GED/editer_profile.html', {'user': e, 'role': role})

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
                    erreur = form.errors
                    return render(request, 'GED/404.html', {'user': p, 'role': role, 'erreur': erreur})

            elif 'btnform2' in request.POST:
                form = ProfForm(request.POST)
                if form.is_valid():
                    p.telephone = request.POST['telephone']
                    p.save()
                else:
                    erreur = form.errors
                    return render(request, 'GED/404.html', {'user': p, 'role': role, 'erreur': erreur})

            elif 'btnform3' in request.POST:
                form = ProfForm(request.POST)
                if form.is_valid():

                    p.about = request.POST['about']
                    p.save()
                else:
                    erreur = form.errors
                    return render(request, 'GED/404.html', {'user': p, 'role': role, 'erreur': erreur})

            elif 'btnform4' in request.POST:
                form = PassForm(request.POST)
                if form.is_valid():

                    newuser.set_password(request.POST['password'])
                    newuser.save()
                else:
                    erreur = form.errors
                    return render(request, 'GED/404.html', {'user': p, 'role': role, 'erreur': erreur})

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
                    return render(request, 'GED/404.html', {'user': p, 'role': role, 'erreur': erreur, 'link':link})

        return render(request, 'GED/editer_profile.html', {'user': p, 'role': role})


def otherprofile(request, username, id):
    newuser = User.objects.get(pk=id)
    user = Eleve.objects.get(user=newuser)
    role = "Eleve"
    newother = User.objects.get(username=username)
    other = Eleve.objects.get(user=newother)

    return render(request, 'GED/othersprofile.html', {'other': other, 'user': user, 'role': role})


##################################################################################################



def documentsEleve(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    mats = Document.LIST_MATIERE
    fils = Document.LIST_FILIERE
    doc = Document.objects.all()
    tops = list(Document.objects.order_by('updload_date'))[-8:]
    listuser = [i.eleve_id for i in tops]
    top = list(zip(listuser, tops))
    top.reverse()
    list1 = top[:4]
    list2 = top[4:]
    return render(request, "GED/table.html", {'user': e, 'docs': doc, 'list1': list1, 'list2': list2, 'fils': fils, 'mats': mats})


def PubEleve(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    doc = Document.LIST_MATIERE
    matiere = [j for (i, j) in doc]
    fil = Document.LIST_FILIERE
    filiere = [j for (i,j) in fil]
    return render(request, 'GED/PubEleve.html', {'user': e, 'matieres': matiere, 'filieres': filiere})


def Traitement(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    files = request.FILES.getlist('fichier')
    i=0
    for f in files:
        newDoc = Document()
        newDoc.eleve_id = e
        newDoc.fichier = f
        newDoc.titre_fichier = request.POST['titre_fichier']+"_"+str(i)
        i+=1
        newDoc.matiere = request.POST['matiere']
        newDoc.filiere = request.POST['filiere']
        newDoc.description = request.POST['description']
        if request.POST['comments'] == "OUI":
            newDoc.comments = True
        else:
            newDoc.comments = False
        newDoc.save()
    return render(request, 'GED/PubEleve.html', {'user': e})



def search(request, id):
    e = Eleve.objects.get(user=User.objects.get(pk=id))
    doc = list(Document.objects.all())
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

    return render(request, 'GED/table.html', {'docs': doc,
                                              'user': e,
                                              'list1': list1,
                                              'list2': list2,
                                              'fils': fils,
                                              'mats': mats})


def pagePerso(request, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    mydocs = Document.objects.filter(eleve_id=e)
    docprof = Document.objects.filter(eleve_id=None, niveau=e.niveau, filiere=e.filiere, share=True)
    lastdoc = list(docprof.order_by('updload_date'))[-4:]
    listprof = [e.prof_id for e in lastdoc]
    lastdoc = list(zip(listprof, lastdoc))
    lastdoc.reverse()
    context={'user': e,
             'docs': mydocs,
             'profs': docprof,
             'lastdoc': lastdoc}
    return render(request, 'GED/pagePerso.html', context)

def deleteDoc(request, titre_fichier, id):
    newuser = User.objects.get(pk=id)
    e = Eleve.objects.get(user=newuser)
    mydocs = Document.objects.filter(eleve_id=e)
    doc = Document.objects.get(titre_fichier=titre_fichier)
    doc.delete()
    return render(request, 'GED/pagePerso.html', {'user': e, 'docs': mydocs})



###PROF#####

def pubProf(request, id):
    newuser = User.objects.get(pk=id)
    p = Professeur.objects.get(userp=newuser)
    doc = Document.LIST_MATIERE
    matiere = [j for (i, j) in doc]
    fil = Document.LIST_FILIERE
    filiere = [j for (i,j) in fil]
    return render(request, 'GED/publish.html', {'user': p, 'matieres': matiere, 'filieres': filiere})


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
    doc = Document.objects.filter(prof_id=p)
    return render(request, "GED/table_prof.html", {'doc': doc,
                                                   'user': p})

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

@login_required(login_url='POLYHINT/connection/')
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
                taches = Tache.objects.filter(eleve_id=e, state=False).order_by('tache_time')
                taskfinish = Tache.objects.filter(eleve_id=e, state=True).order_by('tache_time')
                return render(request, 'GED/index.html', {'user': e,
                                                          'taches': taches,
                                                          'taskfinish': taskfinish})
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


def save(request):
    # Instanciations
    newEleve = Eleve()
    newProf = Professeur()

    # recuperation
    username = request.GET['username']
    password = request.GET['password']
    email = request.GET['email']
    try:
        role = request.GET['role']
    except MultiValueDictKeyError:
        erreur = 'Vous devez definir votre profile: Eleve ou Professeur'
        return render(request, 'GED/404page.html', {'erreur': erreur})
    repassword = request.GET['repassword']

    # Creation
    user = User.objects.create_user(username=username, email=email, password=password)
    user.first_name = request.GET['prenom']
    user.last_name = request.GET['nom']
    user.is_active = False

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

def some_view(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

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
