# 🚀 Guia de Deploy - Sistema Jiboia

**Data:** Novembro de 2025
**Versão:** 1.0

---

## 📋 Requisitos do Servidor

### Hardware Mínimo
- **RAM:** 1 GB
- **CPU:** 1 vCPU
- **Storage:** 40 GB SSD
- **Rede:** IP público + portas 22, 80, 443 abertas

### Software Necessário
```bash
# Instalar Docker e dependências
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
# Fazer logout/login após este comando
```

---

## 🔧 Configuração Inicial do Servidor

### 1. Preparar Estrutura

```bash
# Criar diretório e clonar repositório
cd /home/$USER
git clone https://github.com/SEU_USUARIO/FATEC-API-5-SEMESTRE.git
cd FATEC-API-5-SEMESTRE
```

### 2. Configurar Variáveis de Ambiente

Criar arquivo `.env`:
```bash
nano .env
```

### 3. Configurar SSH para GitHub Actions

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "deploy@jiboia" -f ~/.ssh/jiboia_deploy

# Adicionar chave pública ao authorized_keys
cat ~/.ssh/jiboia_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Copiar chave PRIVADA (para GitHub Secrets)
cat ~/.ssh/jiboia_deploy
```

### 4. Configurar GitHub Secrets

No repositório: **Settings → Secrets and variables → Actions**

Criar 3 secrets:

| Nome | Valor |
|------|-------|
| `SERVER_HOST` | IP público ou domínio do servidor |
| `SERVER_USER` | Usuário SSH (ex: `ubuntu`) |
| `SSH_PRIVATE_KEY` | Conteúdo completo de `~/.ssh/jiboia_deploy` |

### 5. Fazer Login no GitHub Container Registry

```bash
# Gerar token: GitHub → Settings → Developer settings → Personal access tokens
# Permissões: read:packages

docker login ghcr.io -u SEU_USUARIO_GITHUB
# Password: colar o token
```

---

## 🤖 Como Funciona o Deploy Automatizado

O sistema usa **GitHub Actions** que executa automaticamente a cada push:

### Fluxo de Deploy

```
1. Push no repositório
        ↓
2. GitHub Actions builda imagens Docker
        ↓
3. Publica imagens no GitHub Container Registry (ghcr.io)
        ↓
4. Conecta via SSH no servidor
        ↓
5. Atualiza código (git pull)
        ↓
6. Baixa novas imagens Docker
        ↓
7. Reinicia containers (docker-compose)
        ↓
8. Executa health check
```

### Comandos Executados no Servidor

O GitHub Actions executa via SSH:

```bash
# 1. Atualizar código
cd /home/ubuntu/FATEC-API-5-SEMESTRE
git fetch origin
git reset --hard origin/BRANCH_NAME

# 2. Baixar imagens do GitHub Container Registry
docker-compose -f docker-compose.prod.yml pull

# 3. Parar containers antigos
docker-compose -f docker-compose.prod.yml down

# 4. Subir novos containers
docker-compose -f docker-compose.prod.yml up -d

# 5. Aguardar inicialização
sleep 30

# 6. Limpar imagens antigas
docker system prune -f
```

### Arquivo de Workflow

Localização: `.github/workflows/deploy.yml`

**Para adaptar para seu servidor, altere:**

```yaml
# Linha ~39: Caminho do projeto
cd /home/ubuntu/FATEC-API-5-SEMESTRE
# Mudar para: /home/SEU_USUARIO/FATEC-API-5-SEMESTRE

# Linha ~104: URL do health check
https://jiboia.app/
# Mudar para: http://SEU_IP/ ou https://seu-dominio.com/
```

---

## 🌐 Configuração de Domínio

### DNS (Name.com)

No painel do Name.com, configurar:

```
Tipo A | Host: @   | Valor: SEU_IP_PUBLICO | TTL: 300
Tipo A | Host: www | Valor: SEU_IP_PUBLICO | TTL: 300
```

### Nginx + SSL

```bash
# Instalar
sudo apt install -y nginx certbot python3-certbot-nginx

# Criar configuração
sudo nano /etc/nginx/sites-available/jiboia
```

```nginx
server {
    listen 80;
    server_name jiboia.app www.jiboia.app;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/jiboia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obter certificado SSL (gratuito)
sudo certbot --nginx -d jiboia.app -d www.jiboia.app
```

**⚠️ Renovação:**
- **Domínio (jiboia.app):** Renovar em Name.com até Novembro 2026
- **SSL (Let's Encrypt):** Renova automaticamente a cada 60 dias (grátis)

---

## 🔍 Verificação e Troubleshooting

### Verificar Deploy

```bash
# Ver containers rodando
docker ps

# Ver logs
docker logs CONTAINER_NAME

# Testar localmente
curl http://localhost:3000
curl http://localhost:8000/api/
```

## ✅ Checklist de Deploy

### No Servidor
- [ ] Docker e Docker Compose instalados
- [ ] Repositório clonado em `/home/USER/FATEC-API-5-SEMESTRE`
- [ ] Arquivo `.env` configurado
- [ ] Chave SSH criada e adicionada ao `authorized_keys`
- [ ] Login no GitHub Container Registry feito
- [ ] Firewall liberando portas 22, 80, 443

### No GitHub
- [ ] Secrets configurados (SERVER_HOST, SERVER_USER, SSH_PRIVATE_KEY)
- [ ] Workflow adaptado (caminho do projeto, URL health check)
- [ ] Push de teste realizado

### Domínio (Opcional)
- [ ] DNS configurado (registros A)
- [ ] Nginx instalado e configurado
- [ ] Certificado SSL obtido
- [ ] Lembrete de renovação criado (Nov/2026)

---

**Após configuração inicial, todo deploy é automático via git push!** 🚀
