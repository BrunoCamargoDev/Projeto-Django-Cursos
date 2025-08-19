from django.contrib import admin
from django.urls import path
from cursos.views import CursoDetailView, InscreverCursoView, IndexView, TodosCursosView, ProjetosView
from usuarios.views import usuario_view, login_view, logout_view
# from notificacoes.views import registrar_dispositivo

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  
    path('cursos/', TodosCursosView .as_view(), name='todos_cursos'),  
    path('admin/', admin.site.urls),
    path('users/', usuario_view, name='usuario'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('curso/<int:pk>/', CursoDetailView.as_view(), name='curso_detail'),
    path('curso/<int:curso_id>/inscrever/', InscreverCursoView.as_view(), name='inscrever_curso'),
    path('curso/<int:pk>/acessar/', CursoDetailView.as_view(template_name='acessar_curso.html'), name='acessar_curso'),
    path("projetos/", ProjetosView.as_view(), name="projetos"),
    # path('api/devices/register/', registrar_dispositivo, name='registrar_dispositivo'),
]
