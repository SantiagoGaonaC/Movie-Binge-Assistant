
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
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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
        

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task.'})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    

def password_reset_request(request):
    
    if request.method == 'POST':
        password_form = PasswordResetForm(request.POST)
        if password_form.is_valid():
            password_form = PasswordResetForm()
            data = password_form.cleaned_data.get['email']
            user_email = User.objects.filter(Q(email=data))
        if user_email.exists():
            for user in user_email:
                subject = 'Password Request'
                email_template_name = 'registration/password_message.txt'
                parameters = {
                    'email': user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'MovieBinge',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, parameters)
                try:
                    send_mail(subject, email, '', [user.email], fail_silently=False)
                except: 
                    return HttpResponse('Invalid Header')
                return redirect('password_reset_done')            
    else:
        context = {
            'password_form': password_form,
        }
        return render(request, 'registration/password_reset.html', context)