from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
class Command(BaseCommand):
    help='Cria grupos de acesso sem criar contas ou senhas'
    def handle(self,*args,**kwargs):
        entities=['beneficiario','projetosocial','agentecomunitario','municipio','polo','comunidade','familia','visitadomiciliar','acompanhamentosocial']
        policies={
            'Administrador': ['view','add','change','delete'],
            'Coordenador': ['view','add','change'],
            'Agente comunitário': ['view','add','change'],
            'Financeiro': ['view'],
            'Leitura': ['view'],
        }
        for group_name,actions in policies.items():
            group,_=Group.objects.get_or_create(name=group_name)
            codes=[f'{action}_{entity}' for entity in entities for action in actions if entity not in ('municipio','polo','comunidade') or action=='view' or group_name=='Administrador']
            permissions=Permission.objects.filter(content_type__app_label='core',codename__in=codes)
            group.permissions.set(permissions)
            self.stdout.write(f'{group_name}: {permissions.count()} permissões')
        self.stdout.write(self.style.WARNING('Revise permissões por projeto e princípio de menor privilégio antes de dados reais.'))
