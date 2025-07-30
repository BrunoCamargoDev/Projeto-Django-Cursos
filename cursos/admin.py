from django.contrib import admin

from cursos.models import Categoria, Curso, Inscricao, Instrutor, Aula, Modulo

# Register your models here.

admin.site.register(Categoria)
admin.site.register(Curso)
admin.site.register(Inscricao)
admin.site.register(Instrutor)
admin.site.register(Modulo)
admin.site.register(Aula)
