# Amazônia Desenvolve — base de implantação

Sistema Django v5 com login, painel conectado aos cadastros, gestão territorial, famílias, visitas e acompanhamentos. Consulte DEPLOY_STATUS.md para o estado de implantação e os limites da validação.

## Implantação
1. Crie repositório **privado** no GitHub e envie esta pasta (não envie `.env`).
2. No Render, escolha New > Blueprint e conecte o repositório contendo `render.yaml`.
3. Revise preços, plano PostgreSQL e região antes de confirmar a criação. As opções de planos podem mudar.
4. Após a criação, configure `ALLOWED_HOSTS` com o hostname `.onrender.com` fornecido e seu domínio próprio, separados por vírgula, **sem** `https://`.
5. Configure `CSRF_TRUSTED_ORIGINS` com `https://seu-host.onrender.com,https://sistema.seudominio.com.br` (troque pelos endereços reais).
6. Faça deploy/redeploy. Confirme `/health/` e `/accounts/login/`.
7. No Render Shell ou em uma execução administrativa temporária e restrita, rode `python manage.py createsuperuser` para criar o administrador. Não coloque senha em arquivos, logs ou variáveis públicas.
8. Em Settings > Custom Domains, adicione o domínio escolhido. Crie os registros DNS **exatamente** como o Render indicar e aguarde validação e HTTPS.
9. Teste login/logout, admin, CSRF, HTTPS, restauração de backup, privilégios e alertas antes de cadastrar dados reais.

## Segurança e operação
- Exija MFA no provedor de hospedagem e no GitHub; habilite MFA no login da aplicação antes de produção com dados pessoais.
- Configure limitação de tentativas de login (por exemplo, django-axes ou proteção na borda), logs sem dados sensíveis, monitoramento e alertas.
- Escolha plano PostgreSQL com backups automáticos e teste restauração periodicamente; confirme retenção no painel do provedor.
- Documentos privados devem usar object storage com buckets privados, URLs assinadas e checagem de permissão; **não** use `STATIC_ROOT` ou diretório público para RG, CPF ou fotos.
- Restrinja acesso por papéis (administrador, financeiro, coordenador, agente, consulta) antes de implementar cadastros reais.
- Aplique política de retenção, consentimento/base legal, transparência, minimização e gestão de incidentes conforme LGPD.
- Migração do SQLite legado deve ser feita separadamente, com mapeamento, validação e testes de integridade.
- Não habilite `DEBUG=True` em produção.

## Desenvolvimento local
Instale PostgreSQL e Python 3.12. Configure variáveis do `.env.example` no ambiente (Django não carrega `.env` automaticamente). Depois:
```
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

A URL inicial é `http://localhost:8000/accounts/login/`.
