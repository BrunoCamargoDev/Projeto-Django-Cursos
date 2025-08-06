"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from unicodedata import name
from django.contrib import admin
from django.urls import path
from cursos.views import IndexView, CursoDetailView, InscreverCursoView
from usuarios.views import usuario_view, login_view, logout_view

urlpatterns = [
    path('',IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('users/', usuario_view, name='usuario'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('curso/<int:pk>/',CursoDetailView.as_view(), name='curso_detail'),
    path('curso/int:curso_id>/inscrever/',InscreverCursoView.as_view(), name='inscrever_curso'),
]