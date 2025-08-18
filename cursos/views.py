# Create your views here.
import re
from django.shortcuts import render
from .models import Curso, Inscricao
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.views.generic import TemplateView

class IndexView(ListView):
    model = Curso
    template_name = 'index.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Curso.objects.filter(Inscricao__usuario=self.request.user)
        
        else:
            qs= Curso.objects.all()

        titulo = self.request.GET.get('titulo')
        if titulo:
            qs = qs.filter(titulo__icontains=titulo)

        return qs.order_by('titulo').select_related('categoria').prefetch_related('instrutores')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = (
            'Meus cursos' if self.request.user.is_authenticated else 'Cursos Disponíveis'
        )
        return ctx

class TodosCursosView(ListView):
    model = Curso
    template_name = 'index.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        qs = Curso.objects.all().order_by('titulo')
        titulo = self.request.GET.get('titulo')
        if titulo :
            qs = qs.filter(titulo__icontains=titulo)
        return qs
    
    def get_context_data(self, **kwargs):
        curso = super().get_context_data(**kwargs)
        curso['titulo_pagina'] = 'Todos os Cursos'
        return curso

class CursoDetailView(DetailView):
    model = Curso
    template_name = 'curso_detail.html'
    context_object_name = 'curso'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['ja_inscrito'] = {
            user.is_authenticated
            and Inscricao.objects.filter(usuario=user, curso=self.object).exists()
        }
        return ctx

@method_decorator(login_required(login_url='login'), name='dispatch')
class InscreverCursoView(ListView):
    def post(self, request, curso_id):
        curso = get_object_or_404(Curso, pk=curso_id)
        usuario = request.user

        # Verifica se já está inscrito

        if not Inscricao.objects.filter(usuario=usuario, curso=curso).exists():
            Inscricao.objects.create(usuario=usuario, curso=curso)
            messages.success(request, "Sua inscrição foi realizada com sucesso!")

        else:
            messages.warning(request, "Você já está inscrito nesse curso!")

        return redirect('curso_detail', pk=curso_id)
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class ProjetosView(TemplateView):
    template_name = "projetos.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projetos"] = [
            {"nome": "Projeto cursos",
                    "link": "https://github.com/BrunoCamargoDev/Projeto-Django-Cursos.git"}
        ]
        return ctx