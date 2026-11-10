from django import forms
from .models import Beneficiario, ProjetoSocial, AgenteComunitario, Municipio, Polo, Comunidade, Familia, VisitaDomiciliar, AcompanhamentoSocial
from .territory import allowed_communities, is_global
class DateInput(forms.DateInput): input_type='date'
class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model=Beneficiario
        fields=['nome','data_nascimento','telefone','territorio','comunidade','municipio','observacoes','ativo']
        widgets={'data_nascimento':DateInput()}
class ProjetoSocialForm(forms.ModelForm):
    class Meta:
        model=ProjetoSocial
        fields=['titulo','area','descricao','status','inicio','termino','orcamento','territorios','beneficiarios']
        widgets={'inicio':DateInput(),'termino':DateInput(),'beneficiarios':forms.SelectMultiple(attrs={'size':6})}
    def clean(self):
        data=super().clean()
        if data.get('inicio') and data.get('termino') and data['termino']<data['inicio']:
            self.add_error('termino','A data final deve ser posterior à inicial.')
        return data
class AgenteComunitarioForm(forms.ModelForm):
    class Meta:
        model=AgenteComunitario
        fields=['nome','email','telefone','municipio','vinculo','territorios','projetos','ativo']
        widgets={'projetos':forms.SelectMultiple(attrs={'size':6})}


class MunicipioForm(forms.ModelForm):
    class Meta: model=Municipio; fields=['nome','uf','ativo']
class PoloForm(forms.ModelForm):
    class Meta: model=Polo; fields=['nome','municipio','ativo']
class ComunidadeForm(forms.ModelForm):
    class Meta: model=Comunidade; fields=['nome','municipio','polo','ativo']
    def clean(self):
        data=super().clean()
        if data.get('polo') and data.get('municipio') and data['polo'].municipio_id!=data['municipio'].id:
            self.add_error('polo','O polo deve pertencer ao município escolhido.')
        return data

def restrict_form(form, model, user):
    allowed=allowed_communities(user)
    if 'territorio' in form.fields: form.fields['territorio'].queryset=allowed
    if 'territorios' in form.fields: form.fields['territorios'].queryset=allowed
    if 'membros' in form.fields:
        form.fields['membros'].queryset=Beneficiario.objects.filter(territorio__in=allowed)
    if 'familia' in form.fields:
        form.fields['familia'].queryset=Familia.objects.filter(territorio__in=allowed)
    if 'agente' in form.fields:
        form.fields['agente'].queryset=AgenteComunitario.objects.filter(territorios__in=allowed).distinct()
    if 'projeto' in form.fields:
        form.fields['projeto'].queryset=ProjetoSocial.objects.filter(territorios__in=allowed).distinct()
    if 'beneficiarios' in form.fields:
        form.fields['beneficiarios'].queryset=Beneficiario.objects.filter(territorio__in=allowed)
    if 'projetos' in form.fields:
        form.fields['projetos'].queryset=ProjetoSocial.objects.filter(territorios__in=allowed).distinct()
    if 'municipio' in form.fields and model in (Polo,Comunidade):
        form.fields['municipio'].queryset=Municipio.objects.all() if is_global(user) else Municipio.objects.filter(comunidades__in=allowed).distinct()
    if 'polo' in form.fields:
        form.fields['polo'].queryset=Polo.objects.all() if is_global(user) else Polo.objects.filter(comunidades__in=allowed).distinct()
    return form


class FamiliaForm(forms.ModelForm):
    class Meta:
        model=Familia
        fields=['codigo','referencia','territorio','endereco_referencia','telefone','membros','observacoes','ativo']
        widgets={'membros':forms.SelectMultiple(attrs={'size':6})}
    def clean(self):
        data=super().clean()
        territorio=data.get('territorio')
        if territorio and any(m.territorio_id != territorio.id for m in data.get('membros', [])):
            self.add_error('membros','Todos os membros devem pertencer à comunidade da família.')
        return data

class VisitaDomiciliarForm(forms.ModelForm):
    class Meta:
        model=VisitaDomiciliar
        fields=['familia','agente','data','situacao','finalidade','relato','proxima_visita']
        widgets={'data':DateInput(),'proxima_visita':DateInput()}
    def clean(self):
        data=super().clean()
        if data.get('familia') and data.get('agente') and not data['agente'].territorios.filter(pk=data['familia'].territorio_id).exists():
            self.add_error('agente','O agente deve atuar na comunidade da família.')
        return data

class AcompanhamentoSocialForm(forms.ModelForm):
    class Meta:
        model=AcompanhamentoSocial
        fields=['familia','projeto','titulo','descricao','encaminhamento','prazo','situacao']
        widgets={'prazo':DateInput()}
    def clean(self):
        data=super().clean()
        if data.get('familia') and data.get('projeto') and not data['projeto'].territorios.filter(pk=data['familia'].territorio_id).exists():
            self.add_error('projeto','O projeto deve atender à comunidade da família.')
        return data
