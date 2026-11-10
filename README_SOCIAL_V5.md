# Amazônia Desenvolve v5 — Famílias, visitas e acompanhamento

Amplia a versão v4 sem substituir os cadastros territoriais. Registros de famílias são vinculados a comunidades, visitas a famílias e agentes, acompanhamentos a famílias e opcionalmente projetos. Todos os módulos usam formulários Django e persistência no banco configurado.

## Instalação local / staging
1. Crie um ambiente virtual e instale `pip install -r requirements.txt`.
2. Configure `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
3. Faça backup antes de migrar banco existente.
4. Execute `python manage.py makemigrations core` e revise/versione a migração.
5. Execute `python manage.py migrate` e `python manage.py setup_roles`.
6. Crie administrador via `python manage.py createsuperuser`.
7. Teste acesso por região e cenários de edição, incluindo IDs manipulados e POST malicioso.

## Limitações antes de produção
- Não houve teste de integração PostgreSQL ou teste end-to-end neste ambiente.
- A autorização por comunidade é aplicada a listagem, edição e opções de formulário. Para uso real, revisar todas as rotas, filtros, permissões, relatórios e endpoints, inclusive o Django Admin.
- Dados de assistência social podem ser sensíveis. Implementar base legal, minimização, política de retenção, auditoria, registro de consentimento quando aplicável, backups, segurança operacional e avaliação LGPD antes de coletar dados reais.
- A criação de visitas exige agente previamente vinculado à comunidade; acompanhamentos com projeto exigem projeto vinculado à mesma comunidade.
- Não armazenar documentos ou informações médicas detalhadas nos campos de texto livre.
