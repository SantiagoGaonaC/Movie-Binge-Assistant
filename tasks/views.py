from django.shortcuts import render, redirect

from djangocrud import settings
from .mongodb import insert_user, verficiar_user_repetido, buscar_usuario, login, buscar_pelicula, peliculas_user, buscar_peli_id, existe_usuario, cambio_passwd, update_perfil

from .session import createSession, getSession, deleteSession
from django.core.paginator import Paginator

from django.http import Http404
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from urllib import request
import json
from .recomendaciones_1 import recomendacion
from django.template.loader import render_to_string
from cryptography.fernet import Fernet


# Create your views here.



Genres_url = request.urlopen("https://imgmovies.blob.core.windows.net/data/genres.json")
Genres = json.load(Genres_url)

Peliculas_url = request.urlopen("https://imgmovies.blob.core.windows.net/data/peliculas.json")
Peliculas = json.load(Peliculas_url)


@csrf_exempt
def change_password(request):
    sesion = getSession(request)
    if sesion != "no":
        if request.method == 'GET':
            return render(request, 'login/change_passwd.html', {'se': sesion, 'email': sesion, 'er': False}) 
        elif request.method == 'POST':
            email = request.POST['email']
            passwd1 = request.POST['new_password1']
            passwd2 = request.POST['new_password2']
            if passwd1 == passwd2:
                cambio_passwd(email,passwd1)
                return render(request, 'login/change_passwd_complete.html', {'se': sesion}) 
            else:
                return render(request, 'login/change_passwd.html', {'se': sesion, 'email': sesion, 'error': 'Passwords do not match', 'er':True})
    else:
        return redirect('signin')


@csrf_exempt
def complete_reset(request):
    sesion = getSession(request)
    email = request.POST['email']
    passwd1 = request.POST['new_password1']
    passwd2 = request.POST['new_password2']

    if passwd1 == passwd2:
        cambio_passwd(email,passwd1)
        return render(request, 'registration/reset_complete.html', {'se': sesion}) 
    else:
        return render(request, 'registration/reset_passwd.html', {'se': sesion, 'email': email, 'error': 'Passwords do not match', 'er': True}) 

@csrf_exempt
def reset_passwd(request, email):
    sesion = getSession(request)
    k = str(request.GET.get('k'))
    f = Fernet(k.encode())
    token = str(email).encode()
    e = f.decrypt(token).decode()
    return render(request, 'registration/reset_passwd.html', {'se': sesion, 'email': e, 'er': False}) 
   


@csrf_exempt
def mail(request):
    sesion = getSession(request)

    if sesion != "no":
        return redirect('change_password')

    if request.method == 'GET':
        return render(request, 'registration/send_mail.html', {'se': sesion, 'error': True})
    elif request.method == 'POST':
        
        email = request.POST['email']
        user = existe_usuario(email)
        if user:

            key = Fernet.generate_key()
            f = Fernet(key)
            token = f.encrypt(str.encode(email))
            template = render_to_string('registration/email_template.html',{
                'email': email,
                'host': settings.ALLOWED_HOSTS[0],
                'email_byte':token.decode('utf-8'),
                'key': key.decode()
            })

            send_mail(
                "Reset Password",
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )
            return render(request, 'registration/reset_intermedio.html', {'se': sesion})
        else:
            return render(request, 'registration/send_mail.html', {'se': sesion, 'error': user})



@csrf_exempt
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

@csrf_exempt
def buscar(request):
    sesion = getSession(request)
    if request.method == 'POST':
        if(request.POST['search'] == ""):
            p = Peliculas
        else:
            p = buscar_pelicula(request.POST['search'])

        request.session['search'] = request.POST['search']
        page = request.GET.get('page',1)
        try:
            paginator = Paginator(p, 12)
            pelis = paginator.page(page)
        except:
            raise Http404

        return render(request, 'busquedad.html', { 'pelis': pelis, 'se': sesion })
    elif request.method == 'GET':

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

@csrf_exempt
def home(request):

    sesion = getSession(request)
    datos = []
    for p in range(0,12):
        datos.append(Peliculas[p])

    return render(request, 'home.html',  { 'pelis': datos, 'se': sesion }) 
    
@csrf_exempt
def perfil(request):
    sesion = getSession(request)
    if sesion == "no":
        return redirect('signin')
    else:
        user = buscar_usuario(sesion)
        return render(request, 'login/perfil.html', {'data': user, 'len':len(user['pelis']) } )

@csrf_exempt
def lista_peliculas(request):

    pelis = Peliculas
    page = request.GET.get('page',1)
    sesion = getSession(request)
    try:
        paginator = Paginator(Peliculas, 12)
        pelis = paginator.page(page)
    except:
        raise Http404

    return render(request, 'pelis.html', { 'pelis': pelis, 'se': sesion })



@csrf_exempt
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


@csrf_exempt
def edit_perfil(request):
    sesion = getSession(request)
    if sesion != "no":
        if request.method == "GET":
            name = request.GET['name']
            email = request.GET['email']
            pelis = json.loads(request.GET['pelis'])
            update_perfil(name,email,pelis)
            user = buscar_usuario(sesion)
            return render(request, 'login/perfil.html', {'data': user, 'len':len(user['pelis']) } )


@csrf_exempt
def raking_user(request):

    if request.method == "GET":
        sesion = getSession(request)
        title = request.GET['title']
        rating = request.GET['rating']
        peliculas_user(sesion,title,int(rating))

@csrf_exempt
def algoritmo_ia(request):
    sesion = getSession(request)
    if sesion != "no":
        userInput = buscar_usuario(sesion)['pelis']
        pel = []
        if len(userInput) == 0:
            nuevas_pelis = sorted(Peliculas, key=lambda t: t['vote_average'])
            for p in range(0,24):
                pel.append(nuevas_pelis[p])

            page = request.GET.get('page',1)
            try:
                paginator = Paginator(pel, 12)
                pel = paginator.page(page)
            except:
                raise Http404

            return render(request, 'recomendaciones.html', { 'pelis': pel})
        else:
            pelis = recomendacion(Peliculas,userInput, Genres)
            for i in pelis:
                for p in Peliculas:
                    if p['imdb_id'] == i:
                        pel.append(p)

            page = request.GET.get('page',1)
            try:
                paginator = Paginator(pel, 12)
                pel = paginator.page(page)
            except:
                raise Http404

            return render(request, 'recomendaciones.html', { 'pelis': pel})
    else:
        return redirect('signin')
    
