from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Beneficiario, ProjetoSocial, AgenteComunitario, Municipio, Polo, Comunidade, Familia, VisitaDomiciliar, AcompanhamentoSocial
from .forms import BeneficiarioForm, ProjetoSocialForm, AgenteComunitarioForm, MunicipioForm, PoloForm, ComunidadeForm, FamiliaForm, VisitaDomiciliarForm, AcompanhamentoSocialForm, restrict_form
from .territory import scope, is_global

@login_required
def dashboard(request):
    return render(request,'dashboard.html',{'modules':[(key,title) for key,(model,form,title,perm) in MODULES.items() if request.user.has_perm('core.view_'+perm)],'totais':{'beneficiarios':scope(Beneficiario.objects.all(),Beneficiario,request.user).count(),'projetos':scope(ProjetoSocial.objects.all(),ProjetoSocial,request.user).count(),'agentes':scope(AgenteComunitario.objects.all(),AgenteComunitario,request.user).count()}})
def health(request): return HttpResponse('ok',content_type='text/plain')

MODULES={
 'municipios':(Municipio,MunicipioForm,'Municípios','municipio'),
 'polos':(Polo,PoloForm,'Polos','polo'),
 'comunidades':(Comunidade,ComunidadeForm,'Comunidades','comunidade'),
 'beneficiarios':(Beneficiario,BeneficiarioForm,'Beneficiários','beneficiario'),
 'projetos':(ProjetoSocial,ProjetoSocialForm,'Projetos sociais','projetosocial'),
 'familias':(Familia,FamiliaForm,'Famílias','familia'),
 'visitas':(VisitaDomiciliar,VisitaDomiciliarForm,'Visitas domiciliares','visitadomiciliar'),
 'acompanhamentos':(AcompanhamentoSocial,AcompanhamentoSocialForm,'Acompanhamentos sociais','acompanhamentosocial'),
 'agentes':(AgenteComunitario,AgenteComunitarioForm,'Agentes comunitários','agentecomunitario'),
}

def _module(module):
    from django.http import Http404
    if module not in MODULES: raise Http404
    return MODULES[module]

@login_required
def records(request,module):
    model,form,title,perm=_module(module)
    if not request.user.has_perm('core.view_'+perm):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    items=scope(model.objects.all(),model,request.user)[:200]
    return render(request,'records.html',{'items':items,'title':title,'module':module,'can_add':request.user.has_perm('core.add_'+perm),'can_edit':request.user.has_perm('core.change_'+perm)})

@login_required
@require_http_methods(['GET','POST'])
def record_form(request,module,pk=None):
    model,form,title,perm=_module(module)
    action='change_' if pk is not None else 'add_'
    if not request.user.has_perm('core.'+action+perm):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    instance=get_object_or_404(scope(model.objects.all(),model,request.user),pk=pk) if pk else None
    if model in (Municipio,Polo,Comunidade) and not is_global(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    objform=restrict_form(form(request.POST or None,instance=instance),model,request.user)
    if request.method=='POST' and objform.is_valid():
        if not is_global(request.user):
            if model is Familia and not objform.cleaned_data.get('territorio'):
                objform.add_error('territorio','Selecione uma comunidade autorizada.')
            if model is Beneficiario and not objform.cleaned_data.get('territorio'):
                objform.add_error('territorio','Selecione uma comunidade autorizada.')
            if model in (ProjetoSocial,AgenteComunitario) and not objform.cleaned_data.get('territorios'):
                objform.add_error('territorios','Selecione ao menos uma comunidade autorizada.')
    if request.method=='POST' and objform.is_valid() and not objform.errors:
        item=objform.save(commit=False)
        if not item.pk: item.criado_por=request.user
        item.save(); objform.save_m2m()
        # The agent must never attach records to territories outside their grants.
        if not is_global(request.user) and model in (ProjetoSocial,AgenteComunitario):
            if not item.territorios.exists():
                item.territorios.set([])
        return redirect('records',module=module)
    return render(request,'record_form.html',{'form':objform,'title':title,'module':module,'editing':bool(pk)})
