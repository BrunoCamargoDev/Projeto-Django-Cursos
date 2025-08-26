# notificacoes/email_utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

def enviar_email_confirmacao_inscricao(request, usuario, curso):
    subject = f'Inscrição confirmada: {curso.titulo}'
    url_acesso = request.build_absolute_uri(
        reverse('acessar_curso', kwargs={'pk': curso.pk})
    )

    html = render_to_string('confirm_inscricao.html', {
        'usuario': usuario,
        'curso': curso,
        'url_acesso': url_acesso,
    })
    text = render_to_string('confirm_inscricao.txt', {
        'usuario': usuario,
        'curso': curso,
        'url_acesso': url_acesso,
    })

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        to=[usuario.email],
    )
    msg.attach_alternative(html, 'text/html')
    msg.send(fail_silently=False)
