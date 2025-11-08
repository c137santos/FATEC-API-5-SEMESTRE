| **Capacidade estimada da Equipe por Sprint:** | 16 Story Points |
|-----------------------------------------------|-----------------|
| **Meta da Sprint:**                           | User Stories de rank 1, rank 2, rank 3 (total de *14 Story Points*) |
| **Previsão da Sprint (extras, sem compromisso de entrega):** | User Story de rank 4 (*3 Story Points*) |

### Requisitos

[Requisitos Relacionados](../../../README.md#requisitos)

# Backlog da Sprint 1

| Rank | Prioridade | User Story | Requisitos Relacionados | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Alta | Como gestor, quero visualizar uma lista dos projetos disponíveis na API do Jira, mostrando para cada um o nome, data de início e fim. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#7">[7]</a> | 3 | 1 |
| 2 | Alta | Como gestor, quero visualizar para cada projeto a quantidade de issues e o total de horas registradas. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#8">[8]</a> | 3 | 1 |
| 3 | Alta | Como gestor, quero um dashboard inicial que mostre a quantidade de issues e horas trabalhadas para um projeto. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#2">[2]</a>, <a href="../../../README.md#7">[7]</a>, <a href="../../../README.md#8">[8]</a>, <a href="../../../README.md#9">[9]</a> | 8 | 1 |
| 4 | Alta | Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#2">[2]</a>, <a href="../../../README.md#7">[7]</a> | 3 | 2 |

### 🔗 Referências
Todos os requisitos detalhados estão aqui: [Requisitos Detalhados](../requisitos.md)

---

## User Story 1 (Rank 1 - 3 SP)
**Como gestor, quero visualizar uma lista dos projetos disponíveis na API do Jira, mostrando para cada um o nome, data de início e fim.**

### Critérios de Aceitação:

**CA1.1 - Lista de Projetos**
- DADO que a API retorna os projetos e eles já foram tratados
- QUANDO visualizo a lista
- ENTÃO devo ver pelo menos os 2 projetos confirmados:
  - "SM2 - SOS MNT 2025"
  - "SE - SOS Edital"
- E cada projeto deve exibir o nome completo

**CA1.2 - Data de Início**
- DADO que cada projeto tem um campo `created`
- QUANDO visualizo um projeto
- ENTÃO devo ver a data de criação formatada como "Data de início: DD/MM/AAAA"
- E a data deve estar no fuso horário "America/Sao_Paulo"

**CA1.4 - Tratamento de Erros**
- DADO que os DADOS podem estar indisponível
- QUANDO há falha no retorno dos dados
- ENTÃO devo ver mensagem "Erro ao conectar com Jira. Tente novamente."
- E um botão "Tentar novamente"

---

## User Story 2 (Rank 2 - 3 SP)
**Como gestor, quero visualizar para cada projeto a quantidade de issues e o total de horas registradas.**

### Critérios de Aceitação:

**CA2.1 - Quantidade de Issues**
- DADO que o projeto SM2 tem 82 issues
- QUANDO visualizo o projeto SM2
- ENTÃO devo ver "82 issues"
- E o número deve ser obtido via JQL `project = SM2`

**CA2.2 - Total de Horas por Projeto**
- DADO que as issues possuem worklogs
- QUANDO visualizo um projeto
- ENTÃO devo ver o total de horas no formato "150.5h"
- E as horas devem ser calculadas somando `timeSpentSeconds/3600` de todas as issues

**CA2.3 - Dados Específicos dos Projetos da Necto**
- DADO os projetos
- QUANDO visualizo a lista
- ENTÃO devo ver:
  - SM2: aproximadamente 82 issues com horas registradas
  - SE: aproximadamente 76 issues com horas registradas

**CA2.4 - Atualização de Dados**
- DADO que os dados podem mudar no Jira
- QUANDO acesso a tela
- ENTÃO os números devem refletir o estado atual da API
- E deve haver timestamp "Última atualização: HH:MM"

**CA2.5 - Projetos Sem Issues**
- DADO que um projeto pode não ter issues
- QUANDO visualizo tal projeto
- ENTÃO devo ver "0 issues" e "0h"
- E não deve haver erro na interface

**CA2.6 - Formatação de Horas**
- DADO que as horas podem ter decimais
- QUANDO visualizo o total
- ENTÃO deve ser formatado como "123.5h" (máximo 1 casa decimal)
- E valores menores que 1h devem aparecer como "0.5h"

---

## User Story 3 (Rank 3 - 8 SP)
**Como gestor, quero um dashboard inicial que mostre a quantidade de issues e horas trabalhadas para um projeto.**

### Critérios de Aceitação:

**CA3.1 - Seleção de Projeto**
- DADO que tenho múltiplos projetos
- QUANDO acesso o dashboard
- ENTÃO devo ver um dropdown com "SM2 - SOS MNT 2025" e "SE - SOS Edital"
- E ao selecionar um projeto, o dashboard deve atualizar automaticamente

**CA3.2 - Cards de Métricas Principais**
- DADO que selecionei um projeto
- QUANDO visualizo o dashboard
- ENTÃO devo ver 4 cards principais:
  - "Total de Issues: X"
  - "Horas Trabalhadas: Xh"
  - "Issues Ativas: X" (não concluídas)
  - "Issues Concluídas: X"

**CA3.3 - Breakdown por Status**
- DADO que o projeto tem issues com diferentes status
- QUANDO visualizo o dashboard
- ENTÃO devo ver a distribuição:
  - "Tarefas pendentes: X issues"
  - "Em andamento: X issues"
  - "MR: X issues"
  - "Concluído: X issues"
- E deve usar os status reais da Necto confirmados nos testes

**CA3.4 - Gráfico de Status**
- DADO que tenho breakdown por status
- QUANDO visualizo o dashboard
- ENTÃO devo ver um gráfico de pizza ou barras
- E cada status deve ter cor distinta
- E deve mostrar percentuais

**CA3.5 - Dados do Projeto SM2 (Validação)**
- DADO que selecionei o projeto SM2
- QUANDO carrego o dashboard
- ENTÃO devo ver dados consistentes com os testes:
  - Total próximo de 82 issues
  - Issues com status "Tarefas pendentes", "Em andamento", etc.
  - Horas reais registradas nos worklogs

**CA3.6 - Responsividade**
- DADO que acesso de diferentes dispositivos
- QUANDO visualizo o dashboard
- ENTÃO deve funcionar em mobile, tablet e desktop
- E os cards devem se reorganizar adequadamente

**CA3.8 - Estado Vazio**
- DADO que um projeto não tem issues
- QUANDO visualizo seu dashboard
- ENTÃO devo ver cards com "0" e mensagem "Nenhuma issue encontrada"
- E não deve haver erro ou tela quebrada

---

## User Story 4 (Rank 4 - 3 SP - Extra/Sem Compromisso)
**Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação.**

### Critérios de Aceitação:

**CA4.1 - Navegação para Lista**
- DADO que estou no dashboard de um projeto
- QUANDO clico em "Ver todas as issues" ou similar
- ENTÃO devo ir para uma tela de lista detalhada
- E o projeto selecionado deve ser mantido

**CA4.2 - Colunas da Lista**
- DADO que estou na lista de issues
- QUANDO visualizo a tabela
- ENTÃO devo ver as colunas:
  - "ID" (ex: SM2-82)
  - "Título" (summary da issue)
  - "Autor" (reporter ou assignee)
  - "Data Criação" (formatada DD/MM/AAAA)

**CA4.3 - Dados das Issues**
- DADO que selecionei o projeto SM2
- QUANDO visualizo a lista
- ENTÃO devo ver issues como:
  - "SM2-82: Editar a Descrição Categoria - Gestão"
  - Autor: conforme dados do Jira
  - Datas de setembro/agosto de 2025

**CA4.4 - Paginação**
- DADO que o SM2 tem 82 issues
- QUANDO visualizo a lista
- ENTÃO deve haver paginação com 20 issues por página
- E controles "Anterior/Próximo" funcionais


**Critérios de Pronto da Sprint:**
- Todas as user stories de rank 1-3 atendem seus critérios de aceitação
- Testes manuais validam com dados reais da API da Necto
- Interface responsiva em mobile e desktop
- Performance adequada (carregamento < 5s)
- Tratamento de erros implementado
- Código revisado e sem bugs críticos
