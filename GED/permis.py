from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, user_logged_in



def nonAuthentifie(view_dest):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('valider')
        else:
            return view_dest(request, *args, **kwargs)
    return wrapper_func


def allowed_user(role=[]):
    def maFonc(view_dest):
        def wrapper_func(request, *args, **kwargs):
            group1 = None
            if request.user.groups.exists():
                group1 = request.user.groups.all()[0].name

            if group1 in role:
                return view_dest(request, *args, **kwargs)

            else:
                return HttpResponse('Pas autorisé!')
        return wrapper_func
    return maFonc

def compte_autorise(view_dest):
    def wrapper_func(request, *args, **kwargs):

        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == "Eleve" or group=='Professeur':
            return redirect('valider')
        if group == "admin":
            return view_dest(request, *args, **kwargs)
        else:
            return HttpResponse('Vous n\'êtes pas autorisé!')
    return wrapper_func