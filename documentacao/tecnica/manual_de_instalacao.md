# Manual de Instalação - Sistema Jibóia

Este documento fornece instruções passo a passo para instalar e executar o sistema Jibóia, tanto em ambiente de desenvolvimento quanto em produção.

## Pré-requisitos

- Docker e Docker Compose instalados
- Git instalado (para clonar o repositório)
- rodar o comando: ./setup_precommit.sh # Configurar o pré-commit

## Instalação Padrão com Docker

O método padrão de execução do sistema utiliza o Docker para configurar todos os componentes necessários.

### Passo 1: Clone o repositório

```bash
git clone https://github.com/c137santos/FATEC-API-5-SEMESTRE.git
cd FATEC-API-5-SEMESTRE
```

### Passo 2: Configure o arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Banco de Dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=jiboia
DATABASE_URL=postgres://postgres:postgres@postgres:5432/jiboia

# API do Jira
JIRA_API_URL=https://your-domain.atlassian.net
JIRA_API_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### Passo 3: Inicie os containers

```bash
docker-compose up -d
```

Este comando irá:
- Construir as imagens necessárias
- Iniciar o banco de dados PostgreSQL
- Configurar e iniciar o backend Django
- Iniciar o frontend Vue.js
- Configurar o servidor Nginx

### Passo 4: Acesse o sistema

Após iniciar todos os containers, o sistema estará disponível em:

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/

### Passo 5 : Crie um superusuário

Acesse a interface de comando do docker e rode o seguinte comando:

```bash
python3 manage.py createsuperuser
```

Ele irá criar um superusuário que permitirá o acesso em toda a plataforma.


## Ambiente de Desenvolvimento com API Mockada

Para desenvolvimento frontend sem necessidade do backend Django completo, você pode utilizar a API mockada.

```bash
docker-compose -f docker-compose.apimock.yml up -d --force-recreate --build
```

Este comando:
- Substitui o backend Django por um servidor mock
- Carrega dados de exemplo predefinidos
- Mantém a mesma estrutura de API

O frontend continuará acessível em http://localhost

## Cron Jobs

O sistema utiliza cron jobs para tarefas agendadas como sincronização de dados e healthchecks. Para mais detalhes sobre como configurar e gerenciar os cron jobs, consulte a [documentação específica sobre cron jobs](./cron_jobs.md).

### Comandos principais para gerenciamento de cron jobs

```bash
# Dentro do container do backend
docker exec -it back-jiboia bash

# Verificar cron jobs configurados
python manage.py crontab show

# Executar um cron job específico manualmente
python manage.py crontab run <hash>
```

## Solução de Problemas

### Logs do sistema

Para verificar os logs dos containers:

```bash
# Log do backend
docker logs back-jiboia

# Log do frontend
docker logs front-jiboia

# Log do banco de dados
docker logs postgres
```

### Reinício de containers

Se encontrar problemas, tente reiniciar os containers:

```bash
docker-compose restart backend
```

### Reconstrução completa

Para reconstruir completamente o ambiente:

```bash
docker-compose down -v
docker-compose up -d --build
```

## Configurações Avançadas

Para configurações avançadas ou deployment em produção, consulte a documentação técnica completa na pasta `documentacao/tecnica/`.
