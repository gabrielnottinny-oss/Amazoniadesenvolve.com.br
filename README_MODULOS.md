# Amazônia Desenvolve — módulos persistentes v3

Inclui Beneficiários, Projetos Sociais e Agentes Comunitários com modelos Django, formulários, administração, relações e permissões por grupo.

## Preparação
1. Crie PostgreSQL gerenciado e configure `DATABASE_URL` e `SECRET_KEY` como variáveis secretas; use `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` corretos.
2. `pip install -r requirements.txt`
3. `python manage.py makemigrations core` (obrigatório na primeira implantação: migração ainda não gerada)
4. `python manage.py migrate`
5. `python manage.py setup_roles`
6. `python manage.py createsuperuser` (somente em ambiente seguro)
7. `python manage.py collectstatic --noinput`
8. `gunicorn config.wsgi:application`

**Render:** conecte o repositório e use `render.yaml`; após o primeiro deploy, execute `python manage.py setup_roles` em shell seguro. Não execute `createsuperuser` em build público. Os usuários devem receber grupos no Django Admin.

## Segurança e limites
- Todos os endpoints de dados exigem login e permissões Django por modelo. As rotas desconhecidas retornam 404.
- Não existe ainda escopo de acesso por projeto/comunidade: os grupos autorizados veem todos os registros daquele módulo. Antes de armazenar dados reais sensíveis, implementar segregação por território, trilha de auditoria completa, consentimento/base legal, retenção, exportação, backups e armazenamento privado de anexos.
- `criado_por` e timestamps dão rastreabilidade básica, mas não histórico de alterações.
- Não existe importação automática do sistema HTML anterior nem dados fictícios no banco.
- Configure o PostgreSQL com backup e teste restauração antes de produção.
