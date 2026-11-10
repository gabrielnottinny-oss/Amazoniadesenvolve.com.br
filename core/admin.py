from django.contrib import admin
from .models import Beneficiario,ProjetoSocial,AgenteComunitario
@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display=['nome','comunidade','municipio','ativo']; search_fields=['nome','comunidade']; list_filter=['ativo','municipio']
@admin.register(ProjetoSocial)
class ProjetoSocialAdmin(admin.ModelAdmin):
    list_display=['titulo','area','status','orcamento']; search_fields=['titulo','area']; list_filter=['status']
@admin.register(AgenteComunitario)
class AgenteAdmin(admin.ModelAdmin):
    list_display=['nome','municipio','vinculo','ativo']; search_fields=['nome','municipio']; list_filter=['vinculo','ativo']

from .models import Municipio, Polo, Comunidade, AcessoTerritorial
from .territory import is_global, scope
for model in (Municipio,Polo,Comunidade,AcessoTerritorial):
    admin.site.register(model)
# Restrict Django admin to central staff only. Regional users use scoped application views.
_original_has_permission = admin.site.has_permission
def central_admin_permission(request):
    return _original_has_permission(request) and is_global(request.user)
admin.site.has_permission = central_admin_permission

from .models import Familia, VisitaDomiciliar, AcompanhamentoSocial
admin.site.register(Familia)
admin.site.register(VisitaDomiciliar)
admin.site.register(AcompanhamentoSocial)
