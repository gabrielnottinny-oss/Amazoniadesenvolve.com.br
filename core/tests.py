from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from .models import Municipio, Polo, Comunidade, Familia, AcessoTerritorial

@override_settings(SECURE_SSL_REDIRECT=False, STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_roles', verbosity=0)
        municipio=Municipio.objects.create(nome='Município teste')
        polo=Polo.objects.create(nome='Polo teste',municipio=municipio)
        cls.a=Comunidade.objects.create(nome='Comunidade A',municipio=municipio,polo=polo)
        cls.b=Comunidade.objects.create(nome='Comunidade B',municipio=municipio,polo=polo)
        cls.fa=Familia.objects.create(codigo='F-A',referencia='Família A',territorio=cls.a)
        cls.fb=Familia.objects.create(codigo='F-B',referencia='Família B',territorio=cls.b)
        cls.agent=User.objects.create_user('agente_teste')
        cls.agent.groups.add(Group.objects.get(name='Agente comunitário'))
        AcessoTerritorial.objects.create(usuario=cls.agent,comunidade=cls.a)
        cls.reader=User.objects.create_user('leitura_teste')
        cls.reader.groups.add(Group.objects.get(name='Leitura'))
        AcessoTerritorial.objects.create(usuario=cls.reader,comunidade=cls.a)
    def test_anonymous_requires_login(self):
        for path in ['/', '/gestao/familias/', '/gestao/familias/novo/']:
            self.assertEqual(self.client.get(path).status_code,302)
    def test_territory_list_and_direct_url(self):
        self.client.force_login(self.agent)
        response=self.client.get('/gestao/familias/')
        self.assertContains(response,'Família A')
        self.assertNotContains(response,'Família B')
        self.assertEqual(self.client.get(f'/gestao/familias/{self.fb.pk}/editar/').status_code,404)
    def test_forged_territory_rejected(self):
        self.client.force_login(self.agent)
        self.client.post('/gestao/familias/novo/',{'codigo':'FORGED','referencia':'Teste','territorio':self.b.pk})
        self.assertFalse(Familia.objects.filter(codigo='FORGED').exists())
    def test_permitted_creation_persists(self):
        self.client.force_login(self.agent)
        response=self.client.post('/gestao/familias/novo/',{'codigo':'VALID','referencia':'Teste permitido','territorio':self.a.pk})
        self.assertEqual(response.status_code,302)
        self.assertEqual(Familia.objects.get(codigo='VALID').criado_por,self.agent)
    def test_reader_cannot_write(self):
        self.client.force_login(self.reader)
        self.assertEqual(self.client.post('/gestao/familias/novo/',{}).status_code,403)
    def test_no_grants_no_records(self):
        AcessoTerritorial.objects.filter(usuario=self.agent).delete()
        self.client.force_login(self.agent)
        self.assertNotContains(self.client.get('/gestao/familias/'),'Família A')
    def test_csrf_enforced(self):
        client=Client(enforce_csrf_checks=True)
        client.force_login(self.agent)
        self.assertEqual(client.post('/gestao/familias/novo/',{}).status_code,403)
    def test_dashboard_and_logout(self):
        self.client.force_login(self.agent)
        self.assertContains(self.client.get('/'),'Cadastros e acompanhamento')
        self.assertEqual(self.client.post('/accounts/logout/').status_code,302)
        self.assertEqual(self.client.get('/').status_code,302)

class DeploymentTests(TestCase):
    def test_bootstrap_creates_admin_without_resetting_password(self):
        import os
        from unittest.mock import patch
        import secrets
        password = secrets.token_urlsafe(32)
        with patch.dict(os.environ, {'INITIAL_ADMIN_PASSWORD': password}):
            call_command('bootstrap_admin', verbosity=0)
        admin = User.objects.get(username='administrador')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password(password))
        replacement = secrets.token_urlsafe(32)
        admin.set_password(replacement)
        admin.save()
        with patch.dict(os.environ, {'INITIAL_ADMIN_PASSWORD': password}):
            call_command('bootstrap_admin', verbosity=0)
        admin.refresh_from_db()
        self.assertTrue(admin.check_password(replacement))
        self.assertEqual(User.objects.filter(is_superuser=True).count(),1)

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_health_reflects_database_failure_without_details(self):
        from unittest.mock import patch
        from django.db import DatabaseError
        self.assertEqual(self.client.get('/health/').status_code,200)
        with patch('django.db.connection.cursor',side_effect=DatabaseError('private details')):
            response=self.client.get('/health/')
        self.assertEqual(response.status_code,503)
        self.assertNotIn(b'private details',response.content)
