

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Task
from .mongodb import insert_user, verficiar_user_repetido, buscar_usuario, login, peliculas, buscar_pelicula, peliculas_user
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

from .recomendaciones_1 import recomendacion

# Create your views here.



Peliculas = peliculas()

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


def buscar(request):
    sesion = getSession(request)
    if request.method == 'POST':
        p = buscar_pelicula(request.POST['search'])
        request.session['search'] = request.POST['search']
        page = request.GET.get('page',1)
        try:
            paginator = Paginator(p, 12)
            pelis = paginator.page(page)
        except:
            raise Http404

        return render(request, 'busquedad.html', { 'pelis': pelis, 'se': sesion })
    else:

        p = buscar_pelicula(request.session['search'])
        page = request.GET.get('page',1)
        try:
            paginator = Paginator(p, 12)
            pelis = paginator.page(page)
        except:
            raise Http404

        return render(request, 'busquedad.html', { 'pelis': pelis, 'se': sesion })


def logout(request):
    deleteSession(request)
    return redirect('home')


def home(request):

    sesion = getSession(request)
    #input_file = open ('tasks/data/pelis_clean.json', encoding="utf8")

    #pelis = peliculas()
    #Peliculas = pelis
    datos = []
    for p in range(0,12):
        datos.append(Peliculas[p])

    return render(request, 'home.html',  { 'pelis': datos, 'se': sesion }) 
    

def perfil(request):
    sesion = getSession(request)
    if sesion == "no":
        return redirect('signin')
    else:
        return render(request, 'login/perfil.html', {'data': buscar_usuario(sesion), 'len':len(buscar_usuario(sesion)['pelis']) } )

def lista_peliculas(request):
    #input_file = open ('tasks/data/pelis_clean.json', encoding="utf8")
    #pelis = json.load(input_file)
    #pelis = peliculas()
    pelis = Peliculas
    page = request.GET.get('page',1)
    sesion = getSession(request)
    try:
        paginator = Paginator(Peliculas, 12)
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
    
def raking_user(request):

    if request.method == "GET":
        sesion = getSession(request)
        title = request.GET['title']
        rating = request.GET['rating']
        peliculas_user(sesion,title,int(rating))


def algoritmo_ia(request):
    sesion = getSession(request)
    if sesion != "no":
        userInput = buscar_usuario(sesion)['pelis']
        if len(userInput) == 0:
            nuevas_pelis = sorted(Peliculas, key=lambda t: t['vote_average'])
            pel = []
            for p in range(0,12):
                pel.append(nuevas_pelis[p])
            return render(request, 'recomendaciones.html', { 'pelis': pel})
        else:
            pelis = recomendacion(Peliculas,userInput)
            return render(request, 'recomendaciones.html', { 'pelis': pelis})
    else:
        return redirect('signin')
    




class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')