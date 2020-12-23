from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
import mimetypes

try:
    e = Group()
    e.name = "Eleve"
    e.save()
except:
    pass
try:
    p = Group()
    p.name = "Professeur"
    p.save()
except:
    pass



class Eleve(models.Model):

    LIST_NIVEAU = [
        ('TC1', 'TC1'),
        ('TC2', 'TC2'),
        ('DIC1', 'DIC1'),
        ('DIC2', 'DIC2'),
        ('DIC3', 'DIC3'),
    ]
    LIST_FILIERE = [
        ('GIT', 'GIT'),
        ('GEM', 'GEM'),
        ('GC', 'GC'),
        ('AERO', 'AERO'),
        ('TC', 'TC')
    ]

    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    joindate = models.DateField(auto_now_add=True)
    date_birth = models.DateField(null=True)
    profile = models.ImageField(upload_to='GED/img_profile/', default='GED/img_profile/rien.jpg')
    sexe = models.CharField(max_length=10, null=False, choices=[('Masculin', 'Masculin'), ('Feminin', 'Feminin')])
    about = models.TextField(max_length=250)
    filiere = models.CharField(max_length=50, choices=LIST_FILIERE)
    niveau = models.CharField(max_length=50, choices=LIST_NIVEAU)
    telephone = models.CharField(null=True, max_length=15)
    avertissement = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Professeur(models.Model):

    LIST_FILIERE = [
        ('GIT', 'GIT'),
        ('GEM', 'GEM'),
        ('GC', 'GC'),
        ('AERO', 'AERO'),
        ('TC', 'TC')
    ]
    userp = models.OneToOneField(User, related_name='userp', on_delete=models.CASCADE)
    joindate = models.DateField(auto_now_add=True)
    telephone = models.CharField(null=True, max_length=15)
    profile = models.ImageField(upload_to='GED/img_profile/', default='GED/img_profile/rien.jpg')
    sexe = models.CharField(max_length=10, null=False, choices=[('Masculin', 'Masculin'), ('Feminin', 'Feminin')])
    about = models.TextField(max_length=250)

    def __str__(self):
        return self.userp.username

class Document(models.Model):

    def get_extensions_for_type(general_type):
        for ext in mimetypes.types_map:
            if mimetypes.types_map[ext].split('/')[0] == general_type:
                yield ext

    extensions = list(get_extensions_for_type('image'))
    for ext in ['.pdf', '.zip', '.ppt', '.djvu', '.txt', '.docx', '.mlx']:
        extensions.append(ext)

    EXTENSIONS = list(zip(iter(extensions), tuple(extensions)))

    LIST_FILIERE = [
        ('GIT', 'GIT'),
        ('GEM', 'GEM'),
        ('GC', 'GC'),
        ('AERO', 'AERO'),
        ('TC', 'TC')
    ]

    LIST_MATIERE = [
        ('MATHEMATIQUES','MATHS'),
        ('PHYSIQUE', 'PHYSIQUE'),
        ('ANALYSE DE DONNÉES', 'ANALYSE DE DONNÉES'),
        ('DJANGO', 'DJANGO'),
        ('UML', 'UML'),
        ('HERO', 'HERO'),
        ('ALGEBRE', 'ALGEBRE')
    ]
    titre_fichier = models.CharField(null=False, max_length=80, unique=True)
    description = models.TextField(max_length=250)
    type = models.CharField(null=True, max_length=25, choices=EXTENSIONS)
    filiere = models.CharField(max_length=45, null=False, choices=LIST_FILIERE, default="GIT")
    matiere = models.CharField(null=False, max_length=50, choices=LIST_MATIERE)
    niveau = models.CharField(null=True, max_length=8, blank=True)
    fichier = models.FileField(upload_to='GED/documents', unique=True)
    updload_date = models.DateTimeField(auto_now_add=True)
    comments = models.BooleanField(default=False)
    # stars = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(5)])
    eleve_id = models.ForeignKey(Eleve, null=True, on_delete=models.CASCADE, blank=True)
    prof_id = models.ForeignKey(Professeur, null=True, on_delete=models.CASCADE, blank=True)
    note = models.IntegerField(default=0)
    share = models.BooleanField(default=False)
    def __str__(self):
        return self.titre_fichier+"\t"+str(self.eleve_id)+ "\t"+str(self.prof_id)



class Commentaire(models.Model):
    contents = models.TextField(null=True, max_length=350)
    date_comments = models.DateField(auto_now_add=True)
    user_id = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    id_doc = models.ForeignKey(Document, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    dislikes =models.IntegerField(default=0)

    def __str__(self):
        return str(self.user_id) + ":  {:|>15}".format(self.contents)
    def addLikes(self):
        self.likes = self.likes+1

class Tache(models.Model):
    tache = models.CharField(null=False, max_length=45, primary_key=True)
    tache_time = models.DateField(null=False, auto_now_add=True)
    state = models.BooleanField(default=False)
    eleve_id = models.ForeignKey(Eleve, on_delete=models.CASCADE, null=True)
    prof_id = models.ForeignKey(Professeur, on_delete=models.CASCADE, null=True)

class Notifications(models.Model):
    notifs = models.CharField(max_length=150)
    time_notif = models.DateTimeField(auto_now_add=True)
    eleve_id = models.ForeignKey(Eleve, on_delete=models.CASCADE, null=True)
    prof_id = models.ForeignKey(Professeur, on_delete=models.CASCADE, null=True)

class Sujet(models.Model):
    titre = models.CharField(max_length=45, unique=True)
    annee = models.IntegerField(null=False)
    epreuve = models.FileField(upload_to='GED/sujets', unique=True)
    uploader = models.ForeignKey(Eleve, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre

class SocialProfile(models.Model):

    LIST_MEDIA = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('google', 'Google'),
        ('linkedin', 'Linkedin'),
        ('instagram', 'Instagram')
    ]

    network = models.CharField(max_length=100, choices=LIST_MEDIA)
    url = models.URLField(max_length=500)
    eleve_id = models.ForeignKey(Eleve, on_delete=models.CASCADE, null=True)
    prof_id = models.ForeignKey(Professeur, on_delete=models.CASCADE, null=True)