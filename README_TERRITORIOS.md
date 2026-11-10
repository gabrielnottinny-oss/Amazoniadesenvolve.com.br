# Amazônia Desenvolve v4 — territórios e controle regional

## Instalação
Instale as dependências em ambiente virtual, configure `DATABASE_URL` PostgreSQL, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e execute:

```bash
python manage.py makemigrations core
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
python manage.py runserver
```

O pacote não contém migrações geradas: `makemigrations` deve ser executado **antes** de `migrate`, revisado e versionado antes da implantação. Para bases existentes, execute backup e teste a migração em staging.

## Regras de segurança
- Usuário sem concessão territorial não visualiza nenhum registro regional.
- O grupo Administrador e superusuários têm acesso global.
- Concessões são cadastradas no Django Admin, exclusivamente por administradores centrais.
- Município, polo e comunidade são cadastrados somente por administradores centrais.
- Concessões por município, polo ou comunidade são expandidas às comunidades correspondentes.
- Registros legados com texto livre de município/comunidade ficam invisíveis para agentes regionais até associação ao novo campo `territorio`.
- Projetos e agentes exigem ao menos uma comunidade para usuários regionais.
- O Django Admin é reservado aos administradores centrais. As páginas de gestão respeitam escopo territorial.

## Atenção
A autorização regional precisa ser complementada com testes de integração, auditoria e política de privacidade antes de dados reais. Não houve teste de integração com PostgreSQL neste ambiente.
