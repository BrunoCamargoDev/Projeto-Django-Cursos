# Create your views here.
from django.shortcuts import render
from .models import Curso, Inscricao
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView


class IndexView(ListView):
    model = Curso
    template_name = 'index.html'
    context_object_name = 'cursos'
    def get_queryset(self):
        queryset = super().get_queryset().order_by('titulo')
        titulo = self.request.GET.get('titulo')

        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)

        return queryset

class CursoDetailView(DetailView):
    model = Curso
    template_name = 'curso_detail.html'
    context_object_name = 'curso'

@method_decorator(login_required(login_url='login'), name='dispatch')
class InscreverCursoView(ListView):
    def post(self, request, curso_id):
        curso = get_object_or_404(Curso, pk=curso_id)
        usuario = request.user

        # Verifica se já está inscrito

        if not Inscricao.objects.filter(usuario=usuario, curso=curso).exits():
            Inscricao.objects.create(usuario=usuario, curso=curso)

        return redirect('curso_detail', pk=curso_id)