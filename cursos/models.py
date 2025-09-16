import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# Crie seus modelos aqui!

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Instrutor(models.Model):
    nome = models.CharField(max_length=100)
    bio = models.TextField()
    linkedin = models.URLField(blank=True, null=True)
    foto = models.ImageField(upload_to='fotos/', blank=True, null=True)

    def __str__(self):
        return self.nome
    
youtube_id_validator = RegexValidator(
    regex=r'^[A-Za-z0-9_-]{11}$',
    message='Informe apenas o ID do youtube (11 caracteres)' 
)

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_criacao = models.DateField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='cursos')
    instrutores = models.ManyToManyField(Instrutor, related_name='cursos')
    publico_alvo = models.TextField(blank=True)
    requisitos = models.TextField(blank=True)
    material_pdf = models.FileField(
        upload_to="materiais/",
        blank=True,
        null=True,
        help_text='PDF do material de apoio do curso'
    )
    video_id = models.CharField(
        max_length=11,
        blank=True, null=True,
        validators=[youtube_id_validator],
        help_text="Cole apenas o ID."
    )
    
    def __str__(self):
        return self.titulo

class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='modulos')
    titulo = models.CharField(max_length=200)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.titulo} - {self.curso.titulo}"

class Aula(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.PROTECT, related_name='aulas')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    video_url = models.URLField(blank=True, null=True)  
    material_extra = models.FileField(upload_to='docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} ({self.modulo.titulo})"

class Inscricao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    progresso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  
    concluido = models.BooleanField(default=False)
    data_conclusao = models.DateField(null=True,blank=True)
    codigo_certificado = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'curso'], name='inscricao_unica')
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo}"

