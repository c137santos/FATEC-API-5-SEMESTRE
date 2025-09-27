# Cron Jobs no Sistema Jiboia

Este documento descreve a implementação e gerenciamento de cron jobs no sistema Jiboia, com foco inicial no healthcheck da API do Jira.

## Visão Geral

O sistema utiliza cron jobs para executar tarefas agendadas automaticamente. Atualmente, implementamos:

1. **Healthcheck da API do Jira** - Executa diariamente à meia-noite para verificar se a API do Jira está acessível, garantindo que a integração continua funcionando corretamente.

Novos cron jobs podem ser adicionados seguindo a mesma estrutura e padrões descritos neste documento.

## Arquitetura

A implementação utiliza o pacote `django-crontab`, que integra os cron jobs do sistema operacional com o Django. A arquitetura é composta por:

1. **Serviços** - Classes que encapsulam a lógica de negócios e chamadas externas, localizados em `jiboia/core/service/`.
2. **Funções de Cron** - Funções que são executadas pelo agendador, localizadas em `jiboia/core/cron.py`.
3. **Configuração** - Definição dos agendamentos no `settings.py` do Django'.

## Configuração

### Variáveis de Ambiente

Para os cron jobs existentes, as seguintes variáveis de ambiente são necessárias no arquivo `.env`:

```
# Configurações do Jira (para o healthcheck)
JIRA_API_URL=https://necto.atlassian.net
JIRA_API_EMAIL=seu-email@exemplo.com
JIRA_API_TOKEN=seu-token-api
```

Novos cron jobs podem requerer suas próprias variáveis de ambiente, que devem ser documentadas conforme implementadas.

### Configuração do Django

Os cron jobs são configurados no `settings.py` seguindo este formato:

```python
CRONJOBS = [
    # Formato: ('minuto hora dia_do_mês mês dia_da_semana', 'caminho.para.função', '>> /caminho/para/log 2>&1')
    
    # Healthcheck diário do Jira (meia-noite)
    ('0 0 * * *', 'jiboia.core.cron.jira_healthcheck', '>> /tmp/jira_healthcheck.log 2>&1'),
    
    # Exemplo de formato para novos cron jobs
    # ('* * * * *', 'jiboia.core.cron.nova_funcao', '>> /tmp/nova_funcao.log 2>&1'),
]
```

## Gestão dos Cron Jobs

### Comandos Disponíveis

Os seguintes comandos estão disponíveis para gerenciar todos os cron jobs:

```bash
# Adicionar os cron jobs ao sistema
python manage.py crontab add

# Mostrar os cron jobs configurados
python manage.py crontab show

# Remover os cron jobs do sistema
python manage.py crontab remove

# Executar um cron job específico manualmente (para testes)
python manage.py crontab run <hash>
```

O `<hash>` é um identificador único gerado para cada cron job. Para obter o hash correto, execute `python manage.py crontab show` e note o identificador entre parênteses.

Exemplo para o healthcheck do Jira:
```bash
python manage.py crontab run 2dfdc8fe48583985868ea44dc3c84b58
```

### Logs

Cada cron job possui seu próprio arquivo de log, definido na configuração CRONJOBS. Por exemplo:
- Healthcheck do Jira: `/tmp/jira_healthcheck.log`

Além disso, os logs também aparecem nos logs padrão do Django.

## Funcionamento no Docker

### Inicialização Automática

No ambiente Docker, os cron jobs são configurados automaticamente na inicialização do container através do comando definido no `docker-compose.yml`:

```bash
service cron start && python manage.py crontab remove && python manage.py crontab add
```

Esta sequência:
1. Inicia o serviço cron no container
2. Remove quaisquer configurações antigas
3. Registra todos os cron jobs definidos em settings.py

### Desenvolvimento e Manutenção

Ao implementar novos cron jobs ou modificar existentes:

1. Adicione a função no arquivo `jiboia/core/cron.py`
2. Registre o agendamento em `settings.py` na lista CRONJOBS
3. Reinicie o container ou execute manualmente:
   ```bash
   python manage.py crontab remove
   python manage.py crontab add
   ```

## Implementações Atuais

### Healthcheck da API do Jira

- **Função**: `jiboia.core.cron.jira_healthcheck`
- **Agendamento**: Diariamente à meia-noite (`0 0 * * *`)
- **Log**: `/tmp/jira_healthcheck.log`
- **Descrição**: Verifica se o endpoint de projetos da API do Jira está acessível
- **Hash atual**: `2dfdc8fe48583985868ea44dc3c84b58`

## Solução de Problemas

Se os cron jobs não estiverem funcionando como esperado, verifique:

1. Se o serviço cron está em execução no container:
   ```bash
   service cron status
   ```

2. Se os cron jobs estão registrados corretamente:
   ```bash
   python manage.py crontab show
   ```

3. Se as variáveis de ambiente necessárias estão configuradas corretamente.

4. Se há permissões de escrita nos diretórios de logs.

5. Verifique os logs específicos de cada cron job.

6. Para problemas com um cron job específico, teste-o manualmente usando o comando `run` com o hash apropriado.

**Nota importante**: O hash de cada job é gerado pelo django-crontab com base na sua definição no settings.py. Se você modificar a definição, o hash mudará e precisará ser atualizado para testes manuais. O hash correto pode ser sempre identificado executando `python manage.py crontab show`.

## Expandindo o Sistema de Cron Jobs

Para adicionar novos cron jobs ao sistema:

1. Implemente a lógica de negócios em um serviço apropriado em `jiboia/core/service/`
2. Crie uma função de cron em `jiboia/core/cron.py` que utilize o serviço
3. Adicione o agendamento na lista CRONJOBS no settings.py
4. Defina as variáveis de ambiente necessárias
5. Atualize esta documentação com os detalhes do novo cron job