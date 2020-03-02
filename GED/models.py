import os
import sys
from datetime import date
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse

from POLYHINT import settings
from django.core.files.storage import default_storage



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
    joindate = models.DateTimeField(auto_now_add=True)
    date_birth = models.DateField(null=False)
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
    joindate = models.DateTimeField(auto_now_add=True)
    date_birth = models.DateField(null=True)
    profile = models.ImageField(upload_to='GED/img_profile/', default='GED/img_profile/rien.jpg')
    sexe = models.CharField(max_length=10, null=False, choices=[('Masculin', 'Masculin'), ('Feminin', 'Feminin')])
    about = models.TextField(max_length=250)

    def __str__(self):
        return self.userp.username

class Document(models.Model):
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
        ('ANALYSE DE DONNÉES', 'ANALYSE DE DONNÉES')
    ]
    titre_fichier = models.CharField(null=False, max_length=80, unique=True)
    description = models.TextField(max_length=250)
    type = models.CharField(null=True, max_length=25, choices=[('image', 'png'), ('document', 'fichiers')])
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

    @property
    def filename(self):
        name = self.fichier.name.split("/")[1].replace('_', ' ').replace('-', ' ')
        return name

    def get_absolute_url(self):
        return reverse('GED:document-detail', kwargs={'pk': self.pk})


class Commentaire(models.Model):
    contents = models.TextField(null=True, max_length=350)
    date_comments = models.DateTimeField(auto_now_add=True)
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
    tache_time = models.TimeField(null=True)
    state = models.BooleanField(default=False)
    eleve_id = models.ForeignKey(Eleve, on_delete=models.CASCADE)

class Notifications(models.Model):
    notifs = models.CharField(max_length=45)
    eleve_id = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    prof_id = models.ForeignKey(Professeur, on_delete=models.CASCADE)