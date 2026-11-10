from django.db.models import Q
from .models import AcessoTerritorial, Comunidade

def is_global(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Administrador').exists())

def allowed_communities(user):
    qs = Comunidade.objects.all()
    if is_global(user): return qs
    grants = AcessoTerritorial.objects.filter(usuario=user)
    mids = grants.filter(municipio__isnull=False).values_list('municipio_id',flat=True)
    pids = grants.filter(polo__isnull=False).values_list('polo_id',flat=True)
    cids = grants.filter(comunidade__isnull=False).values_list('comunidade_id',flat=True)
    return qs.filter(Q(municipio_id__in=mids)|Q(polo_id__in=pids)|Q(id__in=cids)).distinct()

def scope(qs, model, user):
    if is_global(user): return qs
    ids = allowed_communities(user).values_list('id',flat=True)
    if model.__name__ == 'Familia': return qs.filter(territorio_id__in=ids)
    if model.__name__ in ('VisitaDomiciliar','AcompanhamentoSocial'): return qs.filter(familia__territorio_id__in=ids)
    if model.__name__ == 'Beneficiario': return qs.filter(territorio_id__in=ids)
    if model.__name__ in ('ProjetoSocial','AgenteComunitario'): return qs.filter(territorios__id__in=ids).distinct()
    if model.__name__ == 'Comunidade': return qs.filter(id__in=ids)
    if model.__name__ == 'Polo': return qs.filter(comunidades__id__in=ids).distinct()
    if model.__name__ == 'Municipio': return qs.filter(comunidades__id__in=ids).distinct()
    return qs.none()
