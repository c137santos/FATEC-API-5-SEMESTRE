# Modelo Estrela Detalhado — Issues / Projetos / Horas

## 1. Visão geral

* **Fatos**

  * `fact_horas`  — lançamentos de horas (granularidade: apontamento de horas)
  * `fact_issue`  — uma linha por issue (granularidade: issue)
  * `fact_projeto` — uma linha por projeto (granularidade: projeto)

* **Dimensões** 

  * `dim_dev` (quem)
  * `dim_projeto` (onde / projeto / cliente)
  * `dim_issue` (descrição / id lógico da issue)
  * `dim_tempo` (quando: dia / mês / trimestre / ano)
  * `dim_status` (status das issues)
  * `dim_tipo_issue` (bug / story / task)
  * `dim_equipe` ou `dim_cliente` (opcional, contexto organizacional)

---

## 2. Diagrama simplificado (ASCII)

```
                    dim_dev     dim_status
                       |            |
                       |            |
              dim_tipo  |            |
                \      |            |
                 \     |            |
                  \    |            |
                   \   |            |
                    \  |            |
                     \ |            |
                       \|            |
                         fact_issue <--- dim_tempo
                          /  |  \
                         /   |   \
            dim_projeto /    |    \  dim_issue
                      /      |     \
                     /       |      \
                fact_horas   |     fact_projeto
                     |        
                     dim_tempo

```

---

## 3. Definições detalhadas das Dimensões

### dim\_tempo

* **PK:** tempo\_sk (surrogate key)
* **Atributos:** data, dia, semana, mês, trimestre, ano, dia\_da\_semana, mês\_ano (ex: 2025-09), is\_fim\_de\_semana, fiscal\_month, fiscal\_year
* **Comentários:** Usada por todas as facts — sempre criar até granularidade diária.

### dim\_dev

* **PK:** dev\_sk
* **Atributos:** dev\_id\_origem, nome, email, senioridade, cargo, custo\_hora\_calculado (opcional), ativo, equipe\_sk
* **SCD:** tipo 2 recomendado se você quiser histórico de mudanças de cargo/custo.

### dim\_projeto

* **PK:** projeto\_sk
* **Atributos:** projeto\_id\_origem, nome\_projeto, cliente, area, manager\_dev\_sk (owner), status\_projeto, data\_inicio, data\_previsao\_fim, data\_fim\_real, categoria, prioridade, etiqueta
* **SCD:** tipo 2 recomendado para manter mudanças de manager/cliente/estados.

### dim\_issue

* **PK:** issue\_sk
* **Atributos:** issue\_id\_origem, key (e.g. ABC-123), titulo, descricao\_resumida, reporter\_dev\_sk, assignee\_dev\_sk, prioridade, componente, criado\_data\_sk, tipo\_issue\_sk
* **Observação:** manter campos textuais curtos, long text no sistema operacional (OLTP) se necessário.

### dim\_status

* **PK:** status\_sk
* **Atributos:** status\_nome (Pendente, Em andamento, MR, Concluída), is\_final

### dim\_tipo\_issue

* **PK:** tipo\_issue\_sk
* **Atributos:** tipo\_nome (bug, task, story), descricao

### dim\_equipe (opcional)

* **PK:** equipe\_sk
* **Atributos:** nome\_equipe, area, gerente

---

## 4. Definições detalhadas das Tabelas Fato

### 4.1 `fact_horas`

* **Granularidade:** 1 linha por *lançamento de hora* (apontamento) — a menor unidade detalhada.
* **PK:** hora\_sk (surrogate key)
* **FKs / Colunas de ligação:** dev\_sk, projeto\_sk, issue\_sk (nullable se for hora geral de projeto), tempo\_sk
* **Medidas:**

  * `horas_trabalhadas` (DECIMAL(8,2)) — quantidade de horas no apontamento
  * `valor_hora` (DECIMAL(12,2)) — valor aplicado àquele apontamento (pode vir da dim\_dev ou do contrato)
  * `custo` (DECIMAL(14,2)) — `horas_trabalhadas * valor_hora` (pode ser calculado na ETL ou armazenado)
  * `is_billable` (BOOLEAN) — opcional
  * `atividade_tipo` (varchar) — desenvolvimento, revisão, reunião (dimensionar se necessário)
* **Campos auxiliares:** origem\_apontamento\_id, nota, criado\_em\_timestamp
* **Por que granularidade assim?** Permite agregar por projeto, por dev, por mês, por issue, por cliente, por sprint.

### 4.2 `fact_issue`

* **Granularidade:** 1 linha por **issue** (estado atual ou snapshot por issue se quiser histórico de status)
* **PK:** issue\_sk (pode ser igual ao dim\_issue.issue\_sk se não usar SCD)
* **FKs:** issue\_sk (ou issue\_id), projeto\_sk, tipo\_issue\_sk, status\_sk, assignee\_dev\_sk, tempo\_criacao\_sk, tempo\_fechamento\_sk
* **Medidas:**

  * `qtde_issues` (typedef = 1 por linha; útil para contagem sum(qtde\_issues))
  * `tempo_resolucao_minutos` (INTEGER) — data\_fechamento - data\_criacao em minutos/hours/days
  * `tempo_estimado_horas` (DECIMAL)
  * `tempo_gasto_horas` (DECIMAL) — soma a partir de fact\_horas (pode ser redundante como snapshot)
  * `qtde_reaberturas` (INTEGER)
  * `qtde_comments` (INTEGER)
* **Observação sobre histórico:**

  * Se quiser histórico completo de mudanças (status ao longo do tempo), crie um `fact_issue_status_history` com granularidade *issue × mudança de status × data*.

### 4.3 `fact_projeto`

* **Granularidade:** 1 linha por **projeto** (snapshot ou versão por data se precisar histórico)
* **PK:** projeto\_sk
* **FKs:** projeto\_sk, owner\_dev\_sk, tempo\_inicio\_sk, tempo\_fim\_sk
* **Medidas:**

  * `qtde_issues_total` (INTEGER)
  * `qtde_issues_concluidas` (INTEGER)
  * `horas_totais` (DECIMAL) — agregação de fact\_horas
  * `custo_total` (DECIMAL) — soma de custos de fact\_horas
  * `tempo_duracao_dias` (INTEGER) — data\_fim - data\_inicio
  * `projecao_termino` (DATE) — pode ser campo calculado em ETL/ML
* **Observação:** manter snapshots por mês/semana se quiser analisar evolução do projeto.

---

## 5. Exemplos de queries (resolvendo suas perguntas)

1. **Quantas issues tem em cada projeto?**

```sql
SELECT p.projeto_id_origem, p.nome_projeto, COUNT(i.issue_sk) AS qtde_issues
FROM fact_issue i
JOIN dim_projeto p ON i.projeto_sk = p.projeto_sk
GROUP BY p.projeto_id_origem, p.nome_projeto;
```

2. **Tempo médio de finalização das issues:**

```sql
SELECT AVG(i.tempo_resolucao_minutos)/60.0 AS tempo_medio_horas
FROM fact_issue i
WHERE i.tempo_resolucao_minutos IS NOT NULL;
```

3. **Projeção de término de um projeto:**

* Uma abordagem simples: usar `data_previsao_fim` em `dim_projeto` ou `fact_projeto.projecao_termino`.
* Outra: calcular ritmo atual com `horas_consumidas / horas_estimadas` e extrapolar.

4. **Taxa de conclusão das issues:**

```sql
SELECT p.nome_projeto, s.status_nome, COUNT(*) AS qtde
FROM fact_issue i
JOIN dim_status s ON i.status_sk = s.status_sk
JOIN dim_projeto p ON i.projeto_sk = p.projeto_sk
GROUP BY p.nome_projeto, s.status_nome;
```

5. **Quantas horas cada dev trabalhou no projeto:**

```sql
SELECT p.nome_projeto, d.nome AS dev_nome, SUM(h.horas_trabalhadas) AS horas_totais
FROM fact_horas h
JOIN dim_dev d ON h.dev_sk = d.dev_sk
JOIN dim_projeto p ON h.projeto_sk = p.projeto_sk
GROUP BY p.nome_projeto, d.nome;
```

6. **Quantas horas foram trabalhadas em cada projeto por mês:**

```sql
SELECT p.nome_projeto, t.mes_ano, SUM(h.horas_trabalhadas) AS horas_mes
FROM fact_horas h
JOIN dim_tempo t ON h.tempo_sk = t.tempo_sk
JOIN dim_projeto p ON h.projeto_sk = p.projeto_sk
GROUP BY p.nome_projeto, t.mes_ano
ORDER BY p.nome_projeto, t.mes_ano;
```

7. **A partir do total de horas gastas, quanto está custando o projeto?**

```sql
SELECT p.nome_projeto, SUM(h.horas_trabalhadas * h.valor_hora) AS custo_total
FROM fact_horas h
JOIN dim_projeto p ON h.projeto_sk = p.projeto_sk
GROUP BY p.nome_projeto;
```

8. **Custo médio por hora do projeto:**

```sql
SELECT p.nome_projeto,
       SUM(h.horas_trabalhadas * h.valor_hora) / NULLIF(SUM(h.horas_trabalhadas),0) AS custo_hora_medio
FROM fact_horas h
JOIN dim_projeto p ON h.projeto_sk = p.projeto_sk
GROUP BY p.nome_projeto;
```

---

## 6. Boas práticas / recomendações ETL e modelagem

* **Surrogate keys:** use `*_sk` como surrogate keys em todas as dims e facts.
* **SCD:** Dimensões como `dim_dev`, `dim_projeto` devem suportar SCD type 2 (histórico de manager/custo).
* **Granularidade:** prefira granularidade baixa (apontamento de horas) para manter flexibilidade.
* **Pre-aggregate snapshots:** crie tabelas agregadas (ex: `agg_projeto_mensal`) para relatórios pesados.
* **Indexação:** indexar FKs nas facts (`projeto_sk`, `dev_sk`, `tempo_sk`), e colunas de filtro frequente (status\_sk, tipo\_issue\_sk).
* **Qualidade de dados:** garantir consistência entre OLTP (sistema de origem) e DW — ex: mapping de status/tipo.
* **ETL por lote incremental:** carregar apenas novos apontamentos/alterações (CDC) para facts; para dims usar upsert com SCD.
* **Cálculos:** definir se cálculos (ex: `custo`) serão feitos na ETL (recomendado) ou dinamicamente em queries.

---

## 7. Índices & Performance

* **Fact\_horas:** índices compostos (projeto\_sk, tempo\_sk), (dev\_sk, tempo\_sk)
* **Fact\_issue:** índices (projeto\_sk, status\_sk), (tipo\_issue\_sk, tempo\_criacao\_sk)
* **Dimensões:** índices sobre chaves de origem (issue\_id\_origem, projeto\_id\_origem) para facilitar joins de ingestão.

---

## 8. Observações / escolhas de projeto

* Definições como `valor_hora` podem vir da `dim_dev` (custo por dev) ou do contrato do projeto.
* Escolha entre armazenar `tempo_gasto_horas` em `fact_issue` como *snapshot* (redundância) para acelerar consultas ou deixar apenas em `fact_horas` e sempre agregar.
* Se você precisa de histórico de status por issue, crie `fact_issue_status_history` com granularidade por mudança.
