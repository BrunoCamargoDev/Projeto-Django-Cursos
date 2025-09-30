from django.contrib import admin
from .models import Categoria, Curso, Instrutor, Modulo, Inscricao, TransacaoImportada

admin.site.register(Categoria)
admin.site.register(Curso)
admin.site.register(Instrutor)
admin.site.register(Modulo)
admin.site.register(TransacaoImportada)


@admin.action(description="Marcar pagamento e liberar por 30 dias")
def marcar_pagamento_30(modeladmin, request, queryset):
    for insc in queryset:
        insc.ativar_por_30_dias()
    modeladmin.message_user(request, f"{queryset.count()} inscrição(ões) ativada(s) por 30 dias.")

@admin.action(description="Desativar acesso (bloquear)")
def desativar_acesso(modeladmin, request, queryset):
    queryset.update(ativo=False)

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'curso', 'ativo', 'expira_em', 'pago_em', 'dias_restantes_display')
    list_filter  = ('ativo', 'curso')
    search_fields = ('usuario__username', 'curso__titulo')
    actions = [marcar_pagamento_30, desativar_acesso]

    def dias_restantes_display(self, obj):
        return obj.dias_restantes
    dias_restantes_display.short_description = "Dias restantes"