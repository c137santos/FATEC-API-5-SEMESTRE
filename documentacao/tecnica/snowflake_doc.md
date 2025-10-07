## Descrição do Modelo Dimensional de Projetos
Este modelo utiliza o esquema Star (Estrela), otimizado para análises de desempenho e custos, com foco na imutabilidade dos registros de transação (Fato_issue) e na captura do estado do projeto ao longo do tempo (Fato_snapshot_projeto). O soft delete (active) permite a desativação de entidades sem perda de histórico.

1. Tabelas Fato

- **Fato_issue**:	Registro de tempo gasto por Issue (Transacional) com id, IssueID, typeId, StatusId, projetoID, tempoID, userId. Armazena cada transação de tempo registrada. Deve ser imutável (sem updates). A chave primária é o campo id.

- **Fato_snapshot_projeto**:	Visão do Projeto em um Ponto no Tempo (Snapshot Diário)	id, projetoID, tempoID. Armazena métricas acumuladas e projetadas (dias restantes, custo total, etc.) capturadas diariamente. A chave primária ideal é (projetoID, tempoID).



2. Tabelas de Dimensão
As tabelas de dimensão do modelo são responsáveis por armazenar os principais atributos descritivos das entidades do sistema, facilitando a análise e a navegação dos dados. A seguir, estão descritas as principais dimensões:

- **dim_projeto**: Esta tabela armazena informações sobre os projetos, incluindo o identificador único (`projetoID`), nome, data de início, data de término e o campo `active`, utilizado para soft delete. O campo `active` permite desativar projetos sem perder o histórico dos dados.

- **dim_dev**: Responsável por descrever os desenvolvedores, possui como chave primária o `devId` e armazena atributos como o valor da hora trabalhada e o campo `active` para soft delete, permitindo manter o histórico mesmo após a desativação de um desenvolvedor.

- **dim_tempo**: Representa a dimensão temporal do modelo, sendo uma dimensão conformada compartilhada por todas as tabelas fato. Possui como chave primária o campo `id` e inclui atributos como tipo de tempo (`type_tempo`), minutos, mês, dias, datas de criação, início, término e o total de tempo.

- **dim_type**: Esta dimensão descreve os tipos de issues existentes no sistema, como Task, Bug ou Story. Utiliza o campo `idType` como chave primária e possui os atributos nome e `active`, que permite o soft delete dos tipos de issues.

- **dim_status**: Responsável por armazenar os diferentes status das issues, como Pendente ou Concluída. Tem como chave primária o campo `id` e inclui os atributos nome e `active`, também utilizado para soft delete dos status.



1. Quantas horas foram trabalhadas em cada projeto?
Esta query soma o tempo gasto em todas as issues ativas, agrupado por projeto.

```
SQL
SELECT
    DP.nome AS NomeProjeto,
    SUM(FI.horas_gastas) AS HorasTotais
FROM
    Fato_issue AS FI
JOIN
    dim_projeto AS DP ON FI.projetoID = DP.projetoID 
WHERE
    DP.active = TRUE 
GROUP BY
    DP.nome,
    FI.projetoID
ORDER BY
    HorasTotais DESC;
```

2. Quantas issues tem em cada projeto?
Esta query utiliza a Fato_snapshot_projeto e a função de janela ROW_NUMBER() para retornar a contagem de issues do snapshot mais recente de cada projeto.

```
SQL

WITH UltimoSnapshot AS (
    SELECT
        FSP.projetoID,
        FSP.quantidade_de_issue,
        ROW_NUMBER() OVER (
            PARTITION BY FSP.projetoID
            ORDER BY FSP.tempoID DESC
        ) AS rn
    FROM
        Fato_snapshot_projeto AS FSP
)
SELECT
    DP.nome AS NomeProjeto,
    US.quantidade_de_issue
FROM
    UltimoSnapshot AS US
JOIN
    dim_projeto AS DP ON US.projetoID = DP.projetoID
WHERE
    US.rn = 1; 
```

3. Qual o tempo médio de finalização das issues?
Retorna o tempo médio de término das issues do último snapshot disponível.

```
SQL

SELECT
    FSP.tempo_médio_de_termino_issue
FROM
    Fato_snapshot_projeto AS FSP
ORDER BY
    FSP.tempoID DESC 
LIMIT 1;
```

4. Qual a projeção de finalização do projeto?
Retorna a projeção de término do projeto do último snapshot disponível.

```
SQL

SELECT
    FSP.qual_a_projecao_de_termino
FROM
    Fato_snapshot_projeto AS FSP
ORDER BY
    FSP.tempoID DESC
LIMIT 1;
```

5. Quantas issues são task, bug, story... ?
Conta o total de issues ativas por tipo (dim_type).
```
SQL

SELECT
    DT.nome AS TipoIssue,
    COUNT(FI.id) AS Quantidade
FROM
    Fato_issue AS FI
JOIN
    dim_type AS DT ON FI.typeId = DT.idType 
WHERE
    DT.active = TRUE 
GROUP BY
    DT.nome
ORDER BY
    Quantidade DESC;
```

6. Qual a taxa de conclusão das issues? (pendentes, em andamento, MR e concluídas?)
Conta o total de issues por status (dim_status).

```
SQL

SELECT
    DS.nome AS StatusIssue,
    COUNT(FI.id) AS Quantidade
FROM
    Fato_issue AS FI
JOIN
    dim_status AS DS ON FI.StatusId = DS.id 
WHERE
    DS.active = TRUE 
GROUP BY
    DS.nome
ORDER BY
    CASE DS.nome -- Ordenação lógica do ciclo de vida
        WHEN 'Concluída' THEN 1
        WHEN 'Em Revisão' THEN 2
        WHEN 'Em Andamento' THEN 3
        WHEN 'Pendente' THEN 4
        ELSE 5
    END;
```

7. A partir do total de horas gastas, quanto está custando o projeto?
Retorna o custo acumulado do projeto do último snapshot disponível.

```
SQL

SELECT
    FSP.custo_do_projeto_atual_R$
FROM
    Fato_snapshot_projeto AS FSP
ORDER BY
    FSP.tempoID DESC
LIMIT 1;
```

8. Quanto custa a hora gasta do projeto?
Retorna o custo da hora média do projeto do último snapshot disponível.

```
SQL

SELECT
    FSP.custo_da_hora_média_do_projeto
FROM
    Fato_snapshot_projeto AS FSP
ORDER BY
    FSP.tempoID DESC
LIMIT 1;
```

9. Quantas horas cada dev trabalhou no projeto?
Utiliza a função de janela ROW_NUMBER() para somar apenas a entrada de horas mais recente de cada issue por Dev.

```
SQL

WITH UltimoRegistro AS (
    SELECT
        FI.userId,
        FI.horas_gastas,
        ROW_NUMBER() OVER (
            PARTITION BY FI.userId, FI.IssueId
            ORDER BY FI.tempoId DESC
        ) AS rn
    FROM
        Fato_issue AS FI
)
SELECT
    DD.devId AS DevId,
    DD.valor_da_Hora, 
    SUM(UR.horas_gastas) AS HorasTotaisMaisRecentes
FROM
    UltimoRegistro AS UR
JOIN
    dim_dev AS DD ON UR.userId = DD.devId
WHERE
    UR.rn = 1 AND DD.active = TRUE
GROUP BY
    DD.devId,
    DD.valor_da_Hora
ORDER BY
    HorasTotaisMaisRecentes DESC;
```