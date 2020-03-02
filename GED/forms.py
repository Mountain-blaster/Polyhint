from django.forms import ModelForm, Form, FileField, ClearableFileInput
from .models import *

class ElProfileForm(ModelForm):
    class Meta:
        model = Eleve
        fields = ('profile',)


class ProfProfileForm(ModelForm):
    class Meta:
        model = Professeur
        fields = ('profile',)


class PassForm(ModelForm):
    class Meta:
        model = User
        fields = ('password',)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email')


class ElForm(ModelForm):
    class Meta:
        model = Eleve
        fields = ('telephone','filiere', 'niveau')


class ProfForm(ModelForm):
    class Meta:
        model = Professeur
        fields = ('about',)

class EleveForm(ModelForm):
    class Meta:
        model = Professeur
        fields = ('about',)

class FileFieldForm(Form):
    file_field = FileField(widget=ClearableFileInput(attrs={'multiple': True}))