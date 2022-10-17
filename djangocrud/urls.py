"""djangocrud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from re import template
from django.contrib import admin
from django.urls import path
from tasks import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('pelis/', views.lista_peliculas, name='lista_pelis'),
    path('logout/', views.logout, name='logout'),
    path('forgot_password/', views.mail, name='enviarmail'),
    path('change_password/', views.change_password, name='change_password'),
    path('reset_complete/', views.complete_reset, name='reset_complete'),
    path('reset/<str:email>/', views.reset_passwd, name='reset'),
    path('perfil/', views.perfil, name='perfil'),
    path('search/', views.buscar, name='search'),
    path('recomendacion/', views.algoritmo_ia, name='recomendacion'),
    path('usuario/ranking/', views.raking_user, name='ranking_user'),
    path('usuario/perfil/edit', views.edit_perfil, name='edit_perfil'),

    
]
