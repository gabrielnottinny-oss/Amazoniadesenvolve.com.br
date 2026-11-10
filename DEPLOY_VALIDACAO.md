# Implantação inicial para validação

O arquivo `render-preview.yaml` cria um web service e um PostgreSQL gratuitos na mesma região. Não altera recursos existentes. O banco gratuito expira 30 dias após a criação e não oferece backups. Não cadastrar dados reais neste ambiente. A aplicação pode demorar para abrir após ficar ociosa.

O hostname é obtido de RENDER_EXTERNAL_HOSTNAME, sem permitir hosts arbitrários. As migrações versionadas e os grupos são aplicados no início, pois o plano gratuito não oferece preDeployCommand. /health/ verifica a conexão com o banco.

Primeiro acesso: usuário `administrador`. A senha inicial é gerada pelo Render na variável INITIAL_ADMIN_PASSWORD. Consulte-a apenas na página Environment do serviço, entre em /admin/ e altere a senha. O comando de inicialização nunca redefine a senha se já existe um superusuário. Após o primeiro acesso, a variável INITIAL_ADMIN_PASSWORD pode ser removida do Blueprint e do serviço.

Aprovar o plano de infraestrutura não significa que a implantação terminou. Confirmar status live, resposta do login, conexão ao PostgreSQL e criação/consulta de dados fictícios. Para uso operacional, migrar para infraestrutura persistente com backups e concluir os testes de recuperação e autorização.
