from django.utils import timezone
from .models import Curso, Inscricao
from io import BytesIO
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.views import View
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from notificacoes.email_utils import enviar_email_confirmacao_inscricao
import os 
# from notificacoes.onesignal import notificar_usuario_onesignal

class IndexView(ListView):
    model = Curso
    template_name = 'index.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Curso.objects.filter(inscricao__usuario=self.
                                      request.user)
        else:
            qs = Curso.objects.all()

        titulo = self.request.GET.get('titulo') 
        if titulo:
            qs = qs.filter(titulo__icontains=titulo)

        return qs.order_by('titulo').select_related('categoria').prefetch_related('instrutores')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = (
            'Meus Cursos' if self.request.user.is_authenticated else 'Cursos Disponíveis'
        )
        return ctx

class TodosCursosView(ListView):
    model = Curso
    template_name = 'index.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        qs = Curso.objects.all().order_by('titulo')
        titulo = self.request.GET.get('titulo')
        if titulo:
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
        ctx['ja_inscrito'] = (
            user.is_authenticated
            and Inscricao.objects.filter(usuario=user, curso=self.object).exists()
        )
        return ctx

@method_decorator(login_required(login_url='login'), name='dispatch')
class InscreverCursoView(View):
    def post(self, request, curso_id):
        curso = get_object_or_404(Curso, pk=curso_id)
        usuario = request.user

        if Inscricao.objects.filter(usuario=usuario, curso=curso).exists():
            messages.warning(request, 'Você já está inscrito neste curso.')
        else:
            Inscricao.objects.create(usuario=usuario, curso=curso)
            messages.success(request, 'Inscrição realizada com sucesso!')
            
            try: 
                enviar_email_confirmacao_inscricao(request, usuario, curso)
            except Exception as e:
                messages.info(request, f'Não foi possível enviar o e-mail: {e}')

        return redirect('curso_detail', pk=curso_id)

    def get(self, request, curso_id):
        return redirect('curso_detail', pk=curso_id)

@method_decorator(login_required(login_url='login'), name='dispatch')
class ProjetosView(TemplateView):
    template_name = "projetos.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projetos"] = [
            {"nome": "Projeto cursos", 
                     "link": "https://github.com/BrunoCamargoDev/Projeto-Django-Cursos.git"},
        ]
        return ctx


@method_decorator(login_required(login_url='login'), name='dispatch')
class CancelarCursoView(View):
    def post(self, request, curso_id):
        curso = get_object_or_404(Curso, pk=curso_id)
        usuario = request.user

        inscricao = Inscricao.objects.filter(usuario=usuario, curso=curso).first()
        if inscricao:
            Inscricao.delete()
            messages.success(request, 'Inscrição cancelada com sucesso!')

        return redirect('curso_detail', pk=curso_id)


class BaixarMaterialCursoView(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request, pk):
        curso = get_object_or_404(Curso, pk=pk)

        inscrito = Inscricao.objects.filter(usuario=request.user, curso=curso).exists()

        if not inscrito:
            messages.warning(request, "Você precisa estar matrículado para baixar o material.")
            return redirect("curso_detail", pk=curso.pk)

        if not curso.material_pdf:
            raise Http404("Material não encontrado.")

        filename = os.path.basename(curso.material_pdf.name)
        return FileResponse(curso.material_pdf.open("rb"), as_attachment=True, filename = filename)

    
class CertificadoCursoPDFView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        curso = get_object_or_404(Curso, pk=pk)
        inscricao = get_object_or_404(Inscricao, usuario=request.user, curso=curso)

        if not inscricao.concluido:
            messages.warning(request, 'Você precisa concluir o curso para emitir o certificado.')
            return redirect('curso_detail', pk=curso.pk)

        aluno = (request.user.get_full_name() or request.user.username).strip()

        data = (inscricao.data_conclusao or timezone.now().date()).strftime('%d/%m/%Y')

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        w, h = landscape(A4)

        c.setTitle(f'Certificado - {curso.titulo}')
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(w/2, h - 3*cm, 'CERTIFICADO DE CONCLUSÃO')

        c.setFont('Helvetica', 15)
        c.drawCentredString(w/2, h - 5.2*cm, 'Certificamos que')
        c.setFont('Helvetica-Bold', 22)
        c.drawCentredString(w/2, h - 7.2*cm, aluno)
        c.setFont('Helvetica', 15)
        c.drawCentredString(w/2, h - 9.2*cm, 'concluiu o curso')
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(w/2, h - 11.2*cm, curso.titulo)

        c.setFont('Helvetica', 12)
        c.drawCentredString(w/2, 3*cm, f'Emitido em {data}')
        if inscricao.codigo_certificado:
            c.setFont('Helvetica', 9)
            c.drawRightString(w - 1.5*cm, 1.5*cm, f'Código: {inscricao.codigo_certificado}')

        c.showPage()
        c.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename=f'certificado_{curso.titulo}.pdf')
    
class AcessarCursoView(LoginRequiredMixin, DetailView):
    model = Curso
    template_name = 'acessar_curso.html'
    context_object_name = 'curso'
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not Inscricao.objects.filter(usuario=request.user, curso=self.object).exists():
            messages.warning(request, 'Você precisa estar matrículado para acessar este curso.')
            return redirect('curso_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inscricao'] = Inscricao.objects.filter(
            usuario=self.request.user, curso=self.object
        ).first()
        return ctx
    
class ConcluirCursoView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, pk):
        curso = get_object_or_404(Curso, pk=pk)
        insc  = get_object_or_404(Inscricao, usuario=request.user, curso=curso)

        marcado = request.POST.get('concluido') == 'on'
        insc.concluido = marcado
        if marcado:
            insc.data_conclusao = insc.data_conclusao or timezone.now().date()
            insc.progresso = 100
            msg = 'Curso marcado como concluído.'
        else:
            insc.data_conclusao = None
            msg = 'Conclusão removida.'

        insc.save()
        messages.success(request, msg)
        return redirect('acessar_curso', pk=curso.pk)