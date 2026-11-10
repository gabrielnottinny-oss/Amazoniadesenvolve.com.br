# Preparação para publicação — 10/11/2026

Código Django v5 recuperado do pacote preparado e painel demonstrativo substituído por navegação para os cadastros persistentes. Incluída a migração inicial de core e a criação dos grupos no preDeployCommand.

Validação local: 8 testes aprovados (login obrigatório, isolamento territorial, bloqueio de POST para outro território, cadastro permitido, perfil leitura, ausência de concessões, CSRF e logout). Testes executados em SQLite temporário; PostgreSQL remoto, backup e instalação real ainda precisam ser verificados.

O render.yaml prevê serviços pagos e não foi aplicado. Confirmar os planos e custos no Render antes da criação. Configurar ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS com o endereço real atribuído. SECRET_KEY é gerada pelo provedor e DATABASE_URL vem do banco.

Após conectar o Render: revisar Blueprint, criar serviço e banco, acompanhar build e migrações, criar administrador pelo comando interativo `python manage.py createsuperuser`, testar login e persistência no PostgreSQL. Não há senha padrão nem contas de demonstração na implantação. O domínio próprio depende de configuração DNS posterior.

A publicação não foi executada nesta preparação. Não há URL de acesso confirmada.
