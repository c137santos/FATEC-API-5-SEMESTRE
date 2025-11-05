# 📋 Especificação de Requisitos de Infraestrutura
## Sistema Jiboia - Integração e Análise Jira
**Projeto:** Jiboia
**Equipe:** FATEC - 5º Semestre

---

## 📊 Sumário Executivo

Este documento especifica os requisitos mínimos e recomendados de infraestrutura para deployment do sistema **Jiboia** em ambiente de produção. As especificações são baseadas em testes de performance reais executados em ambiente Docker equivalente à produção e são agnósticas quanto ao provedor de cloud escolhido.

**Objetivo:** Fornecer informações técnicas objetivas para dimensionamento correto da infraestrutura, independente do provedor (AWS, Azure, GCP, DigitalOcean, etc).

---

## 🎯 Resultados dos Testes de Performance

### 1. Perfil de Consumo de Recursos

#### Memória RAM

| Métrica | Valor Medido | Observações |
|---------|--------------|-------------|
| **Aplicação em repouso** | 162.55 MB | Após sincronização inicial com Jira |
| **Aplicação sob carga** | 163.29 MB | 500 requisições simultâneas |
| **Variação sob carga** | +0.74 MB | Footprint de memória estável |
| **Overhead sincronização** | +7.79 MB | Durante execução do cron job |

**Conclusão Técnica:** A aplicação demonstra consumo de memória previsível e estável (~163 MB), mesmo sob carga intensa.

#### CPU

| Cenário | vCPU Utilizada | Observações |
|---------|----------------|-------------|
| **Operação normal** | 0.02 vCPU | Baseado em throughput × latência |
| **Sob carga (50 usuários)** | ~0.15 vCPU | Extrapolado dos testes |
| **Sincronização Jira** | 0.3-0.5 vCPU | Durante 2 minutos/dia |

**Conclusão Técnica:** Aplicação com baixo consumo de CPU. Processador com 0.5-1 vCPU é suficiente para operação normal.

### 2. Características de Performance

#### Latência por Endpoint

**Teste de Carga Mista (500 requisições):**
- **Latência média geral:** 43ms
- **Mediana (P50):** 5ms
- **P95:** 141ms
- **P99:** 147ms

**Breakdown por Endpoint:**

| Endpoint | Tipo | Latência Média (C=1) | Latência Média (C=50) | P95 (C=50) |
|----------|------|----------------------|-----------------------|------------|
| `/api/core/issues` | Lista | 4ms | 7ms | 10ms |
| `/api/core/projects/overview` | Agregação | 17ms | 192ms | 276ms |
| `/api/core/projects/{id}/desenvolvedores` | Lista | 3ms | 4ms | 6ms |

**Legenda:** C = Concorrência (usuários simultâneos)

**Conclusão Técnica:**
- Endpoints de listagem: < 10ms (excelente)
- Endpoint de agregação: < 200ms em alta concorrência (aceitável)
- SLA sugerido: P95 < 300ms

#### Throughput Máximo

| Concorrência | Requisições/segundo | Tempo médio/req | Taxa de erro |
|--------------|---------------------|-----------------|--------------|
| 10 | 900.66 req/s | 11.1ms | 0% |
| 50 | 810.13 req/s | 61.7ms | 0% |
| 100 | 1038.32 req/s | 96.3ms | 0% |

**Conclusão Técnica:** Throughput sustentável de **~810 req/s** sem degradação ou erros.

#### Transferência de Dados

| Endpoint | Payload médio | % do tráfego estimado |
|----------|---------------|----------------------|
| `/api/core/issues` | 2.6 KB | 50% |
| `/api/core/projects/overview` | 0.3 KB | 30% |
| `/api/core/projects/{id}/desenvolvedores` | 0.07 KB | 20% |

**Payload médio ponderado:** 1.4 KB/requisição

### 3. Perfil do Cron Job (Sincronização)

| Métrica | Valor |
|---------|-------|
| **Frequência** | 1x/dia (3:00 AM) |
| **Duração** | ~2 minutos |
| **Memória adicional** | +7.79 MB |
| **CPU durante execução** | 0.3-0.5 vCPU |
| **Operações** | Sincronização de 9 tipos, 8 status, ~90 issues |

---

## 📐 Requisitos de Infraestrutura

### Requisitos Mínimos

| Recurso | Especificação Mínima | Justificativa |
|---------|---------------------|---------------|
| **RAM** | 512 MB | Aplicação (163MB) + PostgreSQL (80MB) + SO (150MB) + Buffer (119MB) |
| **CPU** | 1 vCPU (compartilhada) | 10x acima do consumo medido (0.1 vCPU) |
| **Armazenamento** | 20 GB SSD | Banco de dados (5GB) + logs (2GB) + sistema (10GB) + margem (3GB) |
| **Banda/Transfer** | 5 GB/mês | Baseado em 1.94 GB calculado + margem 150% |
| **Arquitetura** | x86_64 ou ARM64 | Compatível com Python 3.11+ |

### Requisitos Recomendados

| Recurso | Especificação Recomendada | Justificativa |
|---------|---------------------------|---------------|
| **RAM** | 1-2 GB | Margem de 100-300% para picos e cache |
| **CPU** | 1-2 vCPU (dedicada) | Melhor performance e isolamento |
| **Armazenamento** | 40-60 GB SSD | Permite crescimento sem redimensionamento |
| **Banda/Transfer** | 50-100 GB/mês | Margem para crescimento de 10-20x |
| **Backup** | Snapshots diários | Retenção mínima de 7 dias |

---

## 🏗️ Arquitetura da Aplicação

### Stack Tecnológico

```
┌─────────────────────────────────────────┐
│         Frontend (Vue)           │
│         Port 3000 (HTTPS)         │
└────────────┬────────────────────────────┘
             │
┌─────────────────────────────────────────┐
│         Reverse Proxy (Nginx)           │
│         Port 443 (HTTPS)         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      WSGI Server (Gunicorn)             │
│           3 workers                     │
│         Port 8000 (interno)             │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│    Aplicação Django 5.0 + DRF           │
│         Python 3.11 / uv                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Banco de Dados PostgreSQL          │
│         Port 5432 (interno)             │
└─────────────────────────────────────────┘
```

## 📊 Dimensionamento para Demanda Esperada

### Perfil de Tráfego Estimado

#### Cenário Atual (Baseline)
| Métrica | Valor | Observações |
|---------|-------|-------------|
| **Usuários/dia** | 2.000 | Base de usuários ativa inicial |
| **Requisições/usuário** | 20 | Navegação média por sessão |
| **Requisições/dia** | 40.000 | 2.000 × 20 |
| **Requisições/mês** | 1.200.000 | 40k × 30 dias |
| **Throughput médio** | 0.46 req/s | Distribuído em 24h |
| **Throughput pico** | 1.4 req/s | 3x a média (concentração horário comercial) |

#### Projeção de Crescimento

| Período | Usuários/dia | Requisições/dia | Throughput médio | Throughput pico |
|---------|--------------|-----------------|------------------|-----------------|
| **Hoje** | 2.000 | 40.000 | 0.46 req/s | 1.4 req/s |
| **12 meses** | 4.000 | 80.000 | 0.93 req/s | 2.8 req/s |
| **18 meses** | 20.000 | 400.000 | 4.63 req/s | 13.9 req/s |

**Taxa de crescimento:**
- Ano 1: 100% (2.000 → 4.000 usuários)
- Mês 13-18: 400% (4.000 → 20.000 usuários)
- Crescimento total em 18 meses: **900%** (10x)

### Capacidade vs Demanda

#### Cenário Atual (Baseline)
| Aspecto | Demanda | Capacidade Medida | Margem |
|---------|---------|-------------------|--------|
| **Throughput** | 1.4 req/s (pico) | 810 req/s | 578x |
| **RAM** | 363 MB | 512 MB (mínimo) | 41% |
| **Latência** | < 500ms (SLA) | 43ms (média) | 11.6x melhor |
| **Transfer mensal** | 1.94 GB | N/A | Provedor-dependente |
| **Storage** | 5 GB (inicial) | 20 GB (mínimo) | 4x |

#### 12 Meses (4.000 usuários/dia)
| Aspecto | Demanda | Capacidade Mínima | Margem |
|---------|---------|-------------------|--------|
| **Throughput pico** | 2.8 req/s | 810 req/s | 289x |
| **RAM estimada** | 400-450 MB | 512 MB | 14-28% |
| **Transfer mensal** | 3.88 GB | N/A | Provedor-dependente |
| **Storage** | 8-10 GB | 20 GB | 2-2.5x |

**Status:** Infraestrutura mínima ainda adequada. Considerar upgrade para 1GB RAM para maior conforto operacional.

#### 18 Meses (20.000 usuários/dia)
| Aspecto | Demanda | Capacidade Recomendada | Observações |
|---------|---------|------------------------|-------------|
| **Throughput pico** | 13.9 req/s | 810 req/s | Margem ainda confortável (58x) |
| **RAM estimada** | 500-600 MB | **1-2 GB** | ⚠️ Upgrade recomendado |
| **Transfer mensal** | 19.4 GB | 50-100 GB | Verificar limites do provedor |
| **Storage** | 15-20 GB | **40-60 GB** | ⚠️ Upgrade recomendado |
| **CPU** | 0.2-0.3 vCPU | 1-2 vCPU | Ainda adequado |

**Status:** Upgrade necessário em RAM e storage. Considerar plano intermediário.

**Conclusão:**
- **0-12 meses:** Infraestrutura mínima (512MB) adequada com monitoramento
- **12-18 meses:** Upgrade recomendado para 1-2GB RAM e 40GB storage
- **Capacidade de throughput:** Suficiente mesmo para 20k usuários (margem de 58x)

---

## 🚀 Escalabilidade Futura

### Gatilhos para Upgrade

| Métrica | Threshold | Ação Recomendada |
|---------|-----------|------------------|
| RAM usage | > 75% constante | Upgrade para 2GB RAM |
| CPU usage | > 60% por 1h | Upgrade para 2 vCPU |
| Throughput | > 400 req/s | Adicionar worker / upgrade CPU |
| Storage | > 70% | Expandir disco (+20GB) |
| Latência P95 | > 300ms | Otimizar queries / cache / upgrade |

### Estratégias de Escalabilidade

#### Vertical (Escala para cima)
```
512 MB RAM → 1 GB → 2 GB → 4 GB
1 vCPU → 2 vCPU → 4 vCPU
```

#### Horizontal (Escala para fora)
```
1 instância → Load Balancer + 2 instâncias
PostgreSQL standalone → Managed Database (HA)
Cache em memória → Redis/Memcached externo
```
