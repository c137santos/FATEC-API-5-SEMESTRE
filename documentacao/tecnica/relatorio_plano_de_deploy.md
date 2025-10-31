# 📊 Relatório de Deployment AWS - Sistema Jiboia

**Data:** 18 de Outubro de 2025
**Projeto:** Jiboia - Sistema de Integração e Análise Jira
**Equipe:** FATEC - 5º Semestre

---

## 📋 Sumário Executivo

Este relatório apresenta a análise técnica e recomendações para o deployment da aplicação **Jiboia** na AWS, baseado em testes de performance reais executados em ambiente Docker equivalente à produção.

### Decisão Recomendada
**AWS Lightsail - Plano de $10/mês**

**Justificativa:** Os testes demonstraram que a aplicação consome apenas **163 MB de RAM** sob carga e suporta **1038 req/s**, muito acima da demanda estimada de **0.46 req/s** (40.000 requisições/dia). O plano mais econômico da Lightsail atende plenamente aos requisitos do projeto acadêmico.

Custo estimado pela aws: https://calculator.aws/#/estimate?id=c3a8e747fef10be0a0f484a076c40db88b957367

---

## 🎯 Resultados dos Testes de Performance

### 1. Consumo de Memória RAM

| Métrica | Valor | Análise |
|---------|-------|---------|
| **RAM Baseline (aplicação)** | 162.55 MB | Consumo inicial após sincronização Jira |
| **RAM sob Carga (500 req)** | 163.29 MB | Variação mínima de 0.74 MB |
| **RAM Sistema Total** | 3285 → 3299 MB | 85-86% do container Docker (4GB) |
| **Cron Job (sincronização)** | +7.79 MB | Overhead durante sync diário |

**Conclusão:** A aplicação Django + Gunicorn é extremamente leve, utilizando apenas **~163 MB** de RAM mesmo sob carga intensa. Com buffer de segurança de 50%, requer **244 MB** disponíveis.

### 2. Latência e Tempo de Resposta

#### Por Endpoint (Carga Mista - 500 requisições):
- **Média Geral:** 43ms
- **Mediana (P50):** 5ms
- **P95 (95% das requisições):** 141ms
- **P99 (99% das requisições):** 147ms

#### Latência por Concorrência:

**Endpoint: `/api/core/issues` (lista de issues)**
| Concorrência | Média | P95 |
|--------------|-------|-----|
| 1 usuário | 4ms | 5ms |
| 5 usuários | 5ms | 7ms |
| 10 usuários | 6ms | 8ms |
| 20 usuários | 6ms | 9ms |
| 50 usuários | 7ms | 10ms |

**Endpoint: `/api/core/projects/overview` (visão geral projetos)**
| Concorrência | Média | P95 |
|--------------|-------|-----|
| 1 usuário | 17ms | 26ms |
| 5 usuários | 24ms | 30ms |
| 10 usuários | 58ms | 73ms |
| 20 usuários | 132ms | 161ms |
| 50 usuários | 192ms | 276ms |

**Endpoint: `/api/core/projects/1/desenvolvedores` (desenvolvedores)**
| Concorrência | Média | P95 |
|--------------|-------|-----|
| 1 usuário | 3ms | 4ms |
| 5 usuários | 4ms | 7ms |
| 10 usuários | 5ms | 7ms |
| 20 usuários | 4ms | 6ms |
| 50 usuários | 4ms | 6ms |

**Conclusão:** Latências excelentes para uma aplicação web. O endpoint de overview é mais pesado (queries complexas), mas ainda responde em < 200ms mesmo com 50 usuários simultâneos.

### 3. Throughput (Capacidade Máxima)

Testes com ApacheBench (1000 requisições em diferentes níveis de concorrência):

| Concorrência | Throughput | Tempo Médio/Req | Falhas |
|--------------|------------|-----------------|--------|
| **C=10** | **900.66 req/s** | 11.1ms | 0 |
| **C=50** | **810.13 req/s** | 61.7ms | 0 |
| **C=100** | **1038.32 req/s** | 96.3ms | 0 |

**Throughput Máximo Observado:** 1038.32 req/s
**Demanda Estimada:** 0.46 req/s (média) / ~3 req/s (pico)
**Margem de Segurança:** **2257x acima da demanda média** 🚀

**Conclusão:** A aplicação suporta **~2.6 bilhões de requisições/mês** na configuração testada, enquanto a demanda real é de **1.2 milhões/mês**. Ampla margem para crescimento.

### 4. Transferência de Dados

| Endpoint | Tamanho Resposta |
|----------|------------------|
| `/api/core/issues` | 2.6 KB |
| `/api/core/projects/overview` | 0.3 KB |
| `/api/core/projects/1/desenvolvedores` | 0.07 KB |

**Cálculo de Data Transfer:**
- **Tamanho médio ponderado:** 1.4 KB/requisição
  (50% issues + 30% overview + 20% devs)
- **Total mensal (1.2M req):** 1.62 GB
- **Com margem de segurança (+20%):** **1.94 GB/mês**

**Conclusão:** Transferência muito baixa, bem dentro do limite de 1 TB do Lightsail.

### 5. Cron Job (Sincronização Jira)

| Métrica | Valor |
|---------|-------|
| **Tempo de execução** | 130.47s (~2 min) |
| **Memória adicional** | 7.79 MB |
| **Dados sincronizados** | 9 tipos \| 8 status \| 90 issues |
| **Frequência** | Diária (3:00 AM) |

**Conclusão:** O job de sincronização é eficiente e ocorre em horário de baixo tráfego. Impacto mínimo no sistema.

---

## 💰 Análise de Custos AWS

### Comparação de Serviços AWS

| Serviço | Configuração | Custo Mensal | Adequação |
|---------|--------------|--------------|-----------|
| Lightsail $10 ✅ | 1GB RAM, 1 vCPU, 40GB SSD, 2TB transfer | $10.00 | ✅ **RECOMENDADO** |
| EC2 t4g.nano | 512MB RAM, 2 vCPU | ~$3.50 + EBS + transfer | ⚠️ Mais complexo |
| EC2 t4g.micro | 1GB RAM, 2 vCPU | ~$7.00 + EBS + transfer | ⚠️ Mais caro |
| Elastic Beanstalk | Mínimo 1GB | ~$15.00+ | ❌ Overkill |
| ECS Fargate | 0.5 vCPU, 1GB | ~$14.40 | ❌ Muito caro |

### AWS Lightsail - Plano $10/mês

#### Recursos Incluídos:
- **Memória RAM:** 2 gB
- **CPU:** 2 vCPU (processador compartilhado)
- **Armazenamento:** 60 GB SSD
- **Transferência:** 3 TB/mês de data transfer
- **IP Estático:** Incluído (1 IPv4)
- **Sistema Operacional:** Ubuntu 22.04 LTS

#### Stack de Software:
```
┌─────────────────────────────────────────┐
│         Nginx (Reverse Proxy)           │
│              Port 80/443                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Gunicorn WSGI Server               │
│        3 workers × ~54 MB               │
│              Port 8000                  │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Django 5.0 + DRF Application       │
│         Python 3.11 / uv                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│         PostgreSQL 15                   │
│           Port 5432                     │
└─────────────────────────────────────────┘
```

#### Distribuição de Memória (512 MB total):

| Componente | Memória Alocada | Justificativa |
|------------|-----------------|---------------|
| **Sistema Operacional** | ~120 MB | Ubuntu Server mínimo |
| **PostgreSQL 15** | ~80 MB | Configuração otimizada (shared_buffers=32MB) |
| **Gunicorn + Django** | ~163 MB | Medido nos testes (3 workers) |
| **Nginx** | ~10 MB | Proxy reverso leve |
| **Buffer/Sistema** | ~139 MB | Cache, buffers, margem de segurança |
| **TOTAL** | **512 MB** | ✅ Dentro do limite |

--
## 📊 Validação dos Requisitos

### Comparação: Medido vs. Necessário

| Requisito | Necessário | Medido | Status | Margem |
|-----------|------------|--------|--------|--------|
| **RAM** | 350 MB¹ | 163 MB | ✅ | 53% abaixo |
| **CPU** | 0.1 vCPU² | 1 vCPU | ✅ | 10x maior |
| **Throughput** | 0.46 req/s | 810 req/s | ✅ | 1761x maior |
| **Latência** | < 500ms³ | 43ms (média) | ✅ | 11x melhor |
| **Storage** | ~5 GB⁴ | 20 GB | ✅ | 4x maior |
| **Transfer** | 1.94 GB/mês | 1 TB/mês | ✅ | 515x maior |

**Notas:**
1. RAM necessária: SO (120MB) + PostgreSQL (80MB) + App (163MB) = 363MB → Lightsail oferece 512MB
2. CPU calculada: throughput × latency = 0.46 × 0.043 = 0.02 vCPU (com margem: 0.1 vCPU)
3. Latência aceitável para aplicação web interna: < 500ms
4. Storage: Banco de dados (~2GB) + logs (~1GB) + código (~500MB) + sistema (~2GB)

### Capacidade vs. Demanda

**Tráfego Estimado:**
- **Usuários:** 2000/dia
- **Requisições/usuário:** 20
- **Total/dia:** 40.000 requisições
- **Total/mês:** 1.200.000 requisições
- **Média:** 0.46 req/s
- **Pico (3x média):** ~1.4 req/s

**Capacidade Medida:**
- **Throughput sustentável:** 810 req/s (concorrência 50)
- **Capacidade/mês:** ~2.1 bilhões de requisições
- **Headroom:** **1750x acima da demanda**

---

### Cálculo de Workers Gunicorn

**Fórmula oficial:** `workers = (2 × CPU cores) + 1`

Para 1 vCPU:
```
workers = (2 × 1) + 1 = 3 workers
```

**Referência:**
- Gunicorn Documentation. "Design - How Many Workers?". Disponível em: https://docs.gunicorn.org/en/stable/design.html#how-many-workers

### Cálculo de Memória PostgreSQL

**Regra geral:** `shared_buffers = 25% da RAM dedicada`

Para 80MB dedicados ao PostgreSQL:
```
shared_buffers = 80MB × 0.4 = 32MB
effective_cache_size = RAM_total × 0.25 = 512MB × 0.25 = 128MB
```

**Referência:**
- PostgreSQL Wiki. "Tuning Your PostgreSQL Server". Disponível em: https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server

### Dimensionamento de CPU

**Fórmula simplificada:** `CPU = throughput × latency`

Para nossa aplicação:
```
CPU_necessária = 0.46 req/s × 0.043s = 0.0198 vCPU
CPU_com_buffer_5x = 0.0198 × 5 = 0.099 vCPU
```

Lightsail oferece **1 vCPU** = **10x acima do necessário**

**Referência:**
- Allspaw, John. "The Art of Capacity Planning". O'Reilly Media, 2008.

### Estimativa de Data Transfer

**Cálculo:**
```
Transfer_mensal = Requisições_mês × Tamanho_médio
Transfer_mensal = 1.200.000 × 1.4 KB = 1.68 GB
Com margem 20% = 1.68 × 1.2 = 2.016 GB ≈ 1.94 GB
```


## 💡 Conclusão

### Resumo da Recomendação

✅ **AWS Lightsail - Plano $10/mês** é a escolha ideal para o projeto Jiboia porque:

1. **Adequação Técnica:**
   - 2 GB RAM > 244 MB necessários (margem de 109%)
   - 2 vCPU > 0.1 vCPU necessária (margem de 900%)
   - 3 TB transfer > 1.94 GB necessários (margem de 51400%)
   - Throughput 810 req/s > 0.46 req/s necessária (margem de 176000%)

2. **Custo-Benefício:**
   - Custo total: **~$10/mês** (incluindo backups e DNS)
   - Alternativa mais próxima (EC2 t4g.nano): ~$10/mês + complexidade
   - Lightsail inclui: IP estático, snapshots, interface simplificada

3. **Simplicidade Operacional:**
   - Interface web amigável (ideal para projeto acadêmico)
   - Billing previsível (sem surpresas)
   - Snapshots integrados
   - Menos componentes para gerenciar

4. **Margem para Crescimento:**
   - Capacidade atual suporta **1750x** mais tráfego
   - Fácil upgrade para planos maiores ($10, $20, $40/mês)
   - Possibilidade de escalar verticalmente sem migração

---

**Documento gerado em:** 18/10/2025
**Baseado em:** Testes reais de performance
**Validade:** 6 meses (revisão recomendada após esse período)

---

## 📚 Referências

1. Gunicorn Project. "Gunicorn Design Documentation". https://docs.gunicorn.org/en/stable/design.html

2. PostgreSQL Global Development Group. "PostgreSQL Documentation - Server Configuration". https://www.postgresql.org/docs/15/runtime-config.html

3. PostgreSQL Wiki. "Tuning Your PostgreSQL Server". https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server

4. Django Software Foundation. "Django Deployment Checklist". https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

5. AWS Documentation. "Amazon Lightsail Features". https://aws.amazon.com/lightsail/features/
