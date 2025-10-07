from unicodedata import name
from django.contrib import admin
from django.urls import path
from cursos.views import BaixarMaterialCursoView, CertificadoCursoPDFView, CursoDetailView, InscreverCursoView, IndexView, AcessarCursoView ,TodosCursosView, ProjetosView, CancelarCursoView, ConcluirCursoView
from usuarios.views import usuario_view, login_view, logout_view
from django.conf.urls.static import static
from django.conf import settings
from cursos import views
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
    path('curso/<int:curso_id>/cancelar/', CancelarCursoView.as_view(), name='cancelar_curso'),
    path('curso/<int:pk>/acessar', AcessarCursoView.as_view(), name='acessar_curso'),
    path('curso/<int:pk>/certificado', CertificadoCursoPDFView.as_view(), name='certificado_curso'),
    path('curso/<int:pk>/concluir', ConcluirCursoView.as_view(), name='concluir_curso'),
    path("projetos/", ProjetosView.as_view(), name="projetos"),
    # path('api/devices/register/', registrar_dispositivo, name='registrar_dispositivo'),
    path("curso/<int:pk>/material/download/", BaixarMaterialCursoView.as_view(), name="baixar_material_curso"),
    path('cursos/busca-posts/', views.busca_posts, name='busca_posts'),
    path('api/proxy/posts/<int:post_id>/', views.proxy_post, name='proxy_post')
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
