from django.shortcuts import render
from .models import Curso
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

class CursosListView(ListView):
    model = Curso
    template_name = 'ListaCursos.html'
    context_object_name = 'Cursos'

    def get_queryset(self):
        cursos = super().get_queryset().order_by('titulo')
        titulo = self.request.GET.get('titulo')
# Create your views here.
