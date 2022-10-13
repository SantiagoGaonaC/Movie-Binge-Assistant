
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Task
from .mongodb import insert_user, verficiar_user_repetido, buscar_usuario, login
from .forms import TaskForm
from .session import createSession, getSession, deleteSession
from django.core.paginator import Paginator
import json
from django.http import Http404
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


from tasks import mongodb

# Create your views here.


def signup(request):
    sesion = getSession(request)
    if request.method == 'GET':
        return render(request, 'signup.html', {'se': sesion})
    else:
        
        if request.POST["password1"] == request.POST["password2"]:
                if(verficiar_user_repetido(request.POST['email'])):
                    insert_user(request.POST['name'],request.POST['email'],request.POST['password1'])
                    return redirect('home')
                else:
                    return render(request, 'signup.html', {"error": "Username already exists.", 'se': sesion})
        else:
            return render(request, 'signup.html', {"error": "Passwords did not match.", 'se': sesion})




def logout(request):
    deleteSession(request)
    return redirect('home')


def home(request):
    sesion = getSession(request)
    input_file = open ('tasks/data/pelis_clean.json', encoding="utf8")
    pelis = json.load(input_file)
    datos = []
    for p in range(0,12):
        datos.append(pelis[p])

    return render(request, 'home.html',  { 'pelis': datos, 'se': sesion }) 
    

def perfil(request):
    sesion = getSession(request)
    if sesion == "no":
        return redirect('signin')
    else:
        return render(request, 'login/perfil.html', {'data': buscar_usuario(sesion), 'len':len(buscar_usuario(sesion)['pelis']) } )

def lista_peliculas(request):
    input_file = open ('tasks/data/pelis_clean.json', encoding="utf8")
    pelis = json.load(input_file)
    page = request.GET.get('page',1)
    sesion = getSession(request)
    try:
        paginator = Paginator(pelis, 12)
        pelis = paginator.page(page)
    except:
        raise Http404

    return render(request, 'pelis.html', { 'pelis': pelis, 'se': sesion })





def signin(request):
    sesion = getSession(request)
    if request.method == 'GET':
        return render(request, 'signin.html', {'se': sesion})
    else:
        if(str(type(buscar_usuario(request.POST['email']))) == "<class 'dict'>"):
            if(login(request.POST['email'],request.POST['passwd'])):
                createSession(request,request.POST['email'])
                return redirect('home')
            else:
                return render(request, 'signin.html', {"error": "Username or password is incorrect.", 'se': sesion})
        else:
            return render(request, 'signin.html', {"error": "Username not exists.", 'se': sesion})
        
   

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')