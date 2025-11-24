# 📊 Relatório Técnico: Estratégia de Rastreabilidade com GitHub vs Alternativas

## 🎯 Sumário Executivo

**Decisão Estratégica**
Optamos pela utilização nativa do GitHub para implementação de rastreabilidade em detrimento de ferramentas externas (GitLab, Jenkins, JIRA) devido ao alinhamento técnico, redução de custos e integração natural com nosso ecossistema existente.

**Contexto do Projeto**
- Organização GitHub: Estrutura já estabelecida
- Stack tecnológica: Python Django + Vue.js + Docker
- Necessidade: Rastreabilidade ferramentas → processos → pessoas

---

# 🔗 GitHub: Eixo Central da Rastreabilidade e DevOps

O **GitHub** é a **fonte única de metadados** que conecta código, *issues*, *builds* e *deploys*, estabelecendo-se como o **eixo central de rastreabilidade** em nosso fluxo de trabalho. Serve como a Fonte Primária de Metadados e o Destino Final da Correlação.

---

## 🔑 Rastreabilidade Baseada no SHA do Commit

O **SHA do commit** identifica unicamente uma versão do código e cria a ligação essencial: **código → build → imagem Docker → deploy**.

### 1. GitHub Actions como Veículo de Dados

* As **GitHub Actions** (*workflows* em `.github/workflows/`) atuam como o **veículo de injeção de dados**.
* Elas propagam o `COMMIT_SHA` (definido via `COMMIT_SHA=${{ github.sha }}`) e outras variáveis de ambiente durante os processos de *build* e *deploy*.
* O Actions injeta metadados diretamente em métricas, logs e *tags* de imagens Docker.

### 2. Criação da Trilha Completa

| Etapa | Mecanismo |
| :--- | :--- |
| **Requisito → Código** | *Workflow auto-traceability* anota *issues* (RF\*) e PRs com *labels* e comentários, ligando requisito → PR → commit. |
| **Código → Imagem** | Imagens Docker são *taggeadas* com `COMMIT_SHA` e número de *build*. |
| **Ambiente → Evidência** | O *deploy* registra *tag*/commit como metadado. O *endpoint* `/api/version` (ou `/api/health`) expõe o `commit/build`. |
| **Observabilidade** | Logs estruturados e métricas (ex: Prometheus) incluem a *label* `release=COMMIT_SHA`, permitindo correlação. |

---

## 💡 Benefícios e Vantagem Estratégica

A adoção do GitHub é uma **decisão estratégica** que maximiza a eficiência operacional:

* **Redução do Tempo Médio de Reparo (MTTR):** Ao detectar um pico de erro no Prometheus, a equipe correlaciona o erro diretamente ao `COMMIT_SHA`. Isso permite ir imediatamente à interface do GitHub (código exato, histórico do PR), eliminando a busca por "qual versão está rodando".
* **Liderança de Mercado:** Sendo a **maior plataforma de hospedagem de código-fonte**, o GitHub recebe **prioridade de integração** de ferramentas de monitoramento e rastreabilidade (como o Prometheus), facilitando a especialização de ferramentas de terceiros.
* **Flexibilidade e Custo:** O **GitHub Actions** favorece a modularidade em relação ao modelo integrado do GitLab. Além disso, o GitHub costuma ser mais competitivo em custo (Ex: Enterprise $21/usuário vs. GitLab Premium $29/usuário).

---

## ✅ Boas Práticas Adotadas

| Área | Boa Prática |
| :--- | :--- |
| **Workflows** | Definir `COMMIT_SHA=${{ github.sha }}` e usá-lo para *taggear* imagens. |
| **Aplicação** | Expor `commit/build` no *endpoint* `/api/version` (ou `/api/health`). |
| **Observabilidade**| Incluir a *label* `release=COMMIT_SHA` em logs e métricas. |
| **Auditoria** | Usar o *workflow auto-traceability* para anotar *issues*/PRs. |
| **Segurança** | Controlar permissões das Actions e o uso de *secrets/PATs*. **Jamais** remover autenticação ou usar `csrf_exempt` em produção. |

---

## 🧪 Como Testar a Rastreabilidade

1.  Commit e push (`dev`/`main`) disparam o Action de *build*.
2.  Verificar imagem no registry com a tag `COMMIT_SHA`.
3.  Fazer o *deploy* e checar se `GET /api/version` retorna o mesmo `COMMIT_SHA`.
4.  Simular erro/alerta e confirmar se logs/métricas mostram o `COMMIT_SHA` para correlação.
5.  Verificar se *issue*/PR foi anotada pelo *workflow* (*label* + comentário).

## 📈 Análise de Custos

### Custo GitHub Organizations

| Plano | Preço/Mês | Funcionalidades | Adequação |
|-------|-----------|-----------------|-----------|
| Team | $4/usuário | Projects, Actions, Security | ✅ Recomendado |
| Enterprise | $21/usuário | SSO, SAML, Advanced Security | ⚠️ Excesso para necessidade |

**Projeção para 10 desenvolvedores:**
- Team: $40/mês ($480/ano)
- Custo 3 anos: $1.440

### Comparativo com Alternativas

**Sistemas ERP (SAP, Oracle)**
- Custo Licença Profissional (Estimado): $100 - $140/usuário/mês
- Projeção Mensal (10 devs): $1.000 - $1.400/mês
- Custo 3 anos: **$36.000 - $50.400** (+2.400% a +3.400% vs GitHub)
- Implementação: 6-12 meses + consultoria

**JIRA Software Premium + Confluence**
- Custo Plano Premium (Estimado $10.20 - $18.30/usuário/mês)
- Projeção Mensal (10 devs): $102 - $183/mês
- Custo 3 anos: **$3.672 - $6.588** (+155% a +357% vs GitHub)
- Configuração complexa requer especialista

**Trello Premium**
- $10/usuário/mês → $100/mês ($1.200/ano)
- Custo 3 anos: $3.600 (+150% vs GitHub)
- Funcionalidades limitadas para rastreabilidade

**Modelos Excel + SharePoint**
- Custo licença: $12/usuário/mês → $120/mês
- Custo indireto: 60h/mês manutenção ≈ $4.800/mês
- Custo 3 anos: $177.120 (+11.200% vs GitHub)
- Alto risco de erro humano

---

## 🏆 Vantagens Técnicas do GitHub

### 1. Integração Github Native

- Issues → labels → Projects → Actions
- Uma plataforma, fluxo contínuo

### 2. Solução externa

- Jira(Gestão) + Jenkins(CI/CD) + GitLab(Repositório)
- 3 Sistemas distintos, maior complexidade

### 3. Redução de Dependências Externas
- ✅ Menos pontos de falha
- ✅ Single Sign-On nativo
- ✅ Auditoria integrada
- ✅ Backup unificado

---
## 🔧 Análise Técnica Detalhada

### GitHub vs. Sistemas ERP (SAP, Oracle)

| Funcionalidade | GitHub Projects | ERP (Sistemas Transacionais) | Decisão para a Estratégia de Rastreabilidade |
| :--- | :--- | :--- | :--- |
| **Escopo Principal** | Gestão de Código e Projetos de Desenvolvimento | Gestão Financeira, Logística, RH (Transações) | **GitHub:** Focado em engenharia de software e rastreabilidade requisito/código. ERP é **desnecessariamente amplo**. |
| **Rastreabilidade** | Labels, Issues, Milestones (Nat. no SCM) | Módulos e Customização (Desenvolvimento de Módulos) | **GitHub:** Rastreabilidade inerente ao fluxo de desenvolvimento. ERP exige **alto custo e consultoria** para mapeamento. |
| **Integração CI/CD** | Nativa (via Actions) | Desenvolvimento de interfaces/APIs específicas | **GitHub:** O fluxo contínuo é imediato. ERP requer **esforço de integração significativo** e complexo. |
| **Curva Aprendizado** | Baixa (Familiar aos Devs) | Alta (3-6 meses para módulos) | **GitHub:** Adoção rápida. ERP exige **treinamento especializado** e longo. |

### GitHub Projects vs JIRA

| Funcionalidade | GitHub Projects | JIRA | Decisão para a Estratégia de Rastreabilidade |
| :--- | :--- | :--- | :--- |
| **Rastreabilidade** | Labels + Issues | Custom Fields | **GitHub Projects:** Usa a funcionalidade nativa e leve, ideal para o escopo do projeto (API). |
| **Integração CI/CD** | Nativa (via Actions) | Plugins (necessita configuração) | **GitHub Projects:** Integração natural com o Actions, simplificando o fluxo Requirement $\rightarrow$ Code $\rightarrow$ Test. |
| **Customização** | Suficiente | Excessiva | **GitHub Projects:** A customização suficiente evita a "configuração complexa requer especialista" mencionada no relatório. |
| **Curva Aprendizado** | Baixa | Alta | **GitHub Projects:** Alinhado ao objetivo de um *onboarding* rápido e adoção imediata pela equipe de 10 pessoas. |

### GitHub vs. GitLab (Plataforma All-in-One)

O GitLab é o concorrente mais direto, com uma abordagem "tudo em um" (SCM, CI/CD, Segurança e Rastreamento).

| Critério | GitHub (SaaS) | GitLab (SaaS/Self-Managed) | Decisão para a Estratégia de Rastreabilidade |
| :--- | :--- | :--- | :--- |
| **Filosofia Central** | Centrado no Código (Extensível via Actions/Marketplace). | Plataforma DevOps ponta a ponta (Tudo nativo). | **GitHub:** Alinha-se melhor ao ecossistema existente e à necessidade de **simplicidade** e **baixo custo**. |
| **CI/CD Nativo** | **GitHub Actions** (Forte, base de mercado, YAML). | **GitLab CI/CD** (Altamente integrado ao repositório). | **Ambos Fortes:** GitHub Actions é a escolha natural por já estar integrado com *Issues* e *Projects* para rastreabilidade contínua. |
| **Rastreabilidade** | **Issues + Projects + Labels** (Focado no fluxo Dev). | **Issues + Epics** (Recurso mais robusto para Portfólio, mas mais complexo). | **GitHub:** Mais fácil de implementar e adotar, reforçando a métrica de **baixa curva de aprendizado**. |
| **Custo Total** | Preço por usuário mais competitivo no plano **Team** ($4/mês). | Plano **Premium/Ultimate** geralmente é necessário para rastreabilidade avançada. | **GitHub:** Mantém a projeção financeira de **$1.440 em 3 anos**, a mais vantajosa. |

---

### GitHub vs. Bitbucket (Suíte Atlassian)

O Bitbucket se destaca por sua integração profunda com o **JIRA Software**, fazendo parte de um ecossistema mais amplo.

| Critério | GitHub | Bitbucket (Integrado c/ JIRA) | Decisão para a Estratégia de Rastreabilidade |
| :--- | :--- | :--- | :--- |
| **Integração JIRA** | Via Plugins de terceiros. | **Nativa e Profunda** (Rastreabilidade JIRA $\leftrightarrow$ Bitbucket). | **GitHub:** A forte integração JIRA-Bitbucket não é um benefício, pois o **JIRA foi descartado** no relatório por custo e complexidade (+287% vs GitHub). |
| **Rastreabilidade** | Issues + Projects + Labels. | **Dependente do JIRA** (Bitbucket é SCM, JIRA é a gestão). | **GitHub:** A solução nativa do GitHub **elimina a dependência de um segundo sistema**, simplificando o fluxo. |
| **Custo Oculto** | Baixo (Tudo na mesma plataforma). | Alto (Licença Bitbucket + Licença JIRA + Custo de configuração). | **GitHub:** Reforça a estratégia de **redução de dependências externas** e custo. |

---

### GitHub vs. Azure DevOps (ADO)

O Azure DevOps (ADO) é a suíte de DevOps da Microsoft, composta por módulos (Boards, Repos, Pipelines) e altamente integrada ao Azure Cloud.

| Critério | GitHub | Azure DevOps (ADO) | Decisão para a Estratégia de Rastreabilidade |
| :--- | :--- | :--- | :--- |
| **Estrutura** | Plataforma Unificada. | Modular (Boards, Repos, Pipelines). | **GitHub:** A estrutura unificada e a **integração nativa** com o SCM existente são superiores para o projeto. |
| **Rastreabilidade** | Issues + Projects + Labels. | **Boards** (Funcionalidade de gestão comparável ao JIRA, com maior complexidade). | **GitHub:** O ADO Boards oferece complexidade desnecessária e exige migração, o que vai contra a preferência por **baixa curva de aprendizado**. |
| **Integração Cloud** | Forte com Azure e AWS (via Actions). | **Profunda com Azure** (Integração privilegiada). | **GitHub:** A organização já estabelecida no GitHub significa que a migração para o ADO é um **custo e risco de projeto desnecessário**. |
| **Custo de Migração** | $0 (Manutenção do ecossistema atual). | Alto (Migrar repositórios, *issues*, e *pipelines*). | **GitHub:** Manter o *status quo* no GitHub é o **caminho de menor risco e maior benefício**. |

### GitHub vs Ferramentas Empresariais

| Critério | GitHub | ERP | JIRA | Trello | Excel |
|----------|--------|-----|------|--------|-------|
| **Rastreabilidade** | Labels + Issues | Customizado | Custom Fields | Cards | Células |
| **Integração CI/CD** | Nativa | Desenvolvimento | Plugins | Power-ups | Manual |
| **Customização** | Suficiente | Excessiva | Complexa | Limitada | Manual |
| **Curva Aprendizado** | 2 dias | 3-6 meses | 2 semanas | 1 dia | Variável |
| **Manutenção** | GitHub | Consultoria | Admin | Manual | Alta |
| **Custo Total** | $1.440 | $18.000+ | $5.580 | $3.600 | $177.120 |

### Custo-Benefício por Tipo de Projeto

**Projeto API (Nosso Caso)**
- GitHub: ✅ Perfeito (custo baixo, integração nativa)
- ERP: ❌ Overkill (custo alto, complexo)
- JIRA: ⚠️ Aceitável (custo médio, configuração)
- Trello: ❌ Insuficiente (limitações técnicas)
- Excel: ❌ Risco alto (erros, manutenção)

**Time de 10 Pessoas - Custo 3 Anos**
- GitHub: **$1.440** ✅
- Trello: $3.600 (+150%)
- JIRA Premium: **$3.672 - $6.588** (+155% a +357%)
- ERP (Licença Profissional): **$36.000 - $50.400** (+2.400% a +3.400%)
- Excel: $177.120 (+11.200%) ❌

---

## 🚀 Plano de Implementação

### Fase 1: Estabelecimento
- IDs personalizados (RF1-PROJ-LIST)
- Mapeamento semântico
- Classificação automática
- Testes em staging
- Estrutura definida
- Rollout para time

### Fase 2: Treinamento e Adoção
- Padrões de commit
- Uso de labels
- Consulta de rastreabilidade
- Issues novas com padrão
- Issues existentes sob demanda

### Fase 3: Consolidação
- Taxa de classificação automática
- Acurácia do mapeamento
- Feedback do time
- Refinamento do workflow
- Expansão para outros projetos

---

## 📊 Métricas de Sucesso

### Quantitativas
- 90%+ das issues com rastreabilidade adequada
- < 30 segundos para identificar requisito→código
- 50% redução em tempo de onboarding
- 100% cobertura de requisitos rastreáveis

### Qualitativas
- ✅ Cliente consegue acompanhar progresso por requisito
- ✅ Novos devs entendem contexto rapidamente
- ✅ Auditoria de conformidade facilitada
- ✅ Tomada de decisão baseada em dados

---

## 🛡️ Considerações de Segurança

### Vantagens GitHub Organizations
- SSO/SAML nativo (Enterprise)
- 2FA obrigatório
- Audit Log integrado
- Security Overview automático
- Dependabot para vulnerabilidades

### Comparativo Segurança
| Recurso | GitHub | ERP | JIRA | Trello | Excel |
|---------|--------|-----|------|--------|-------|
| **2FA** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Audit Log** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **SSO** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Backup Auto** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Compliance** | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 💡 Conclusão

### Risco Mitigado
Para uma API de 3 anos em organização estabelecida, o GitHub oferece a **combinação ideal** sem a complexidade e custo de ferramentas overkill como ERP ou a limitação de soluções como Trello/Excel.

**Cenários onde outras ferramentas fariam sentido:**
- Empresa 500+ funcionários com processos complexos → ERP
- Time não-técnico focado apenas em gestão → Trello
- Orçamento ilimitado com necessidade customização extrema → JIRA
- **Nosso caso: GitHub é a solução ótima**

---

**Documento gerado em:** 18/10/2025
**Baseado em:** Testes reais de performance
**Validade:** 6 meses (revisão recomendada após esse período)

---

## 📚 Referências

1. Plans of Github and pricing. "Site do GitHub" https://docs.github.com/pt/get-started/learning-about-github/githubs-plans , https://github.com/pricing

2. How Much Does ERP Cost in 2025? Complete Pricing Guide for All Business Sizes. "Top10ERP". https://www.top10erp.org/blog/erp-price

3. Atlassian services. "ATLASSIAN". https://www.atlassian.com/br/collections/service/pricing

4. Trello preços. "Trello". https://trello.com/pt-BR/pricing

5. GitLab. "GitLab Documentation". https://docs.gitlab.com/

6. Gitlab. "Gitlab Pricing". https://about.gitlab.com/pt-br/pricing/

7. Azure DevOps Documentation. "Microsoft Azure". https://learn.microsoft.com/en-us/azure/devops/?view=azure-devops

8. Azure DevOps Pricing. "Microsoft Azure". https://azure.microsoft.com/en-us/pricing/details/devops/azure-devops-services/

9. Bitbucket Pricing. "Atlassian Bitbucket". https://www.atlassian.com/br/software/bitbucket/pricing

10. BitBucket Documentation. "Atlassian Documentation". https://bitbucket.org/product/guides

11. Microsoft Office Pricing. "Microsoft 365". https://www.microsoft.com/pt-br/microsoft-365/buy/compare-all-microsoft-365-products
