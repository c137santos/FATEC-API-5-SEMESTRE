| **Capacidade estimada da Equipe por Sprint:** | 16 Story Points |
|-----------------------------------------------|-----------------|
| **Meta da Sprint:**                           | User Stories de rank 1, rank 2, rank 3, rank 4 (total de *13 Story Points*) |
| **Previsão da Sprint (extras, sem compromisso de entrega):** | User Story de rank 5 (*5 Story Points*) |

# Backlog da Sprint 1
| Rank | Prioridade | User Story | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Alta | Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação. |3 | 1 |
| 2 | Alta | Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma. |2 | 1 |
| 3 | Alta | Como gestor, quero que o dashboard de issues exiba informações úteis ao contexto de issues do projeto. | 8| 1 |
| 4 | Alta| Como gestor, quero visualizar no dashboard a quantidade de membros ativos e as horas trabalhadas por cada um. |3 | 1 |
| 5 | Alta | Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues. | 5| 1 |

> User Story: Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação.

#### Critérios de Aceitação:

* [ ] O sistema deve exibir uma tela de listagem de issues após a seleção de um projeto.

* [ ] A tela de listagem deve exibir as issues em uma tabela ou lista.

* [ ] Para cada issue, os seguintes campos devem ser exibidos: ID da Issue, Autor e Data de Criação.

* [ ] A exibição deve ser clara e organizada.

#### Casos de Teste:

#### Cenário de Sucesso:

Dado: Um projeto com 10 issues válidas e com campos autor, ID e data de criação preenchidos.

Quando: O usuário seleciona o projeto.

Então: A tela de listagem deve ser exibida, mostrando as 10 issues com seus respectivos dados corretos.

#### Cenário de Falha:

Dado: Uma falha no banco com os dados.

Quando: O usuário seleciona o projeto.

Então: O sistema deve exibir uma mensagem de erro amigável ao usuário e registrar o erro no log.

#### Cenário de Dados Incompletos:

Dado: Um projeto com uma issue sem o campo autor ou data de criação.

Quando: O usuário seleciona o projeto.

Então: A lista de issues é exibida corretamente, e os campos ausentes na issue são mostrados com um valor padrão (não informado).

> User Story: Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma.

#### Critérios de Aceitação:

* [ ] O sistema deve adicionar um popup com informações adicionais sobre a issue, Tempo Total Gasto e Data de Início na tela de listagem de issues.

* [ ] O campo Tempo Total Gasto deve ser exibido em um formato legível.

* [ ] O campo Data de Início deve ser exibido no formato de data e hora.

#### Casos de Teste:

#### Cenário de Sucesso:

Dado: Um projeto com issues com tempo total gasto e data de início preenchidos.

Quando: O usuário seleciona o projeto.

Então: pode clicar na issue listada e ver o popup com as informações adicionais da issue.

#### Cenário de edge case (Issue sem tempo):

Dado: Um projeto com uma issue que ainda não tem tempo registrado.

Quando: O usuário seleciona o projeto.

Então: O popup é exibido com a informação padrão: não informado.

#### Cenário de edge case (Issue sem data de início):

Dado: Um projeto com uma issue que ainda não tem data de início.

Quando: O usuário seleciona o projeto.

Então: O popup é exibido com a informação padrão: não informado.

> User Story: Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues.

#### Critérios de Aceitação:

* [ ] O dashboard de issues deve ter um filtro para Intervalo de datas de criação (Data Início e Data Fim).

* [ ] O dashboard de issues deve ter um filtro para Membro da Equipe, listando todos os membros do projeto.

* [ ] Ao aplicar os filtros, o dashboard deve recarregar e exibir apenas as issues que correspondem aos critérios selecionados.

#### Casos de Teste:

#### Cenário de Filtragem por Data:

Dado: Existem issues criadas em diferentes datas.

Quando: O usuário aplica o filtro de Data de Criação para o intervalo de 01/09/2025 a 07/09/2025.

Então: O dashboard exibe apenas as issues criadas dentro desse período.

#### Cenário de Filtragem por Membro:

Dado: Existem issues atribuídas a diferentes membros da equipe.

Quando: O usuário aplica o filtro por um membro específico.

Então: O dashboard exibe apenas as issues criadas ou atribuídas àquele membro.

#### Cenário de Filtros Combinados:

Dado: Existem issues criadas em diferentes datas e por diferentes membros.

Quando: O usuário aplica o filtro de data e o filtro de membro ao mesmo tempo.

Então: O dashboard exibe apenas as issues que correspondem a ambos os critérios.

> User Story: Como gestor, quero que o dashboard de issues exiba informações úteis ao contexto de issues do projeto..

#### Critérios de Aceitação:

* [ ] O dashboard deve exibir um gráfico ou tabela mostrando o total de issues resolvidas por cada membro da equipe.

* [ ] O dashboard deve exibir uma métrica de destaque com o Total de Issues Resolvidas de todo o time no período selecionado.

* [ ] As informações exibidas devem ser precisas e baseadas nos dados que foram coletados da API do Jira.

#### Casos de Teste:

#### Cenário de Sucesso:

Dado: A equipe tem 5 membros e um total de 20 issues resolvidas.

Quando: O usuário acessa o dashboard de issues.

Então: O dashboard deve exibir o total de issues resolvidas (20) e um detalhamento por membro, como "João: 5, Maria: 8, Pedro: 7", com os dados corretos.

#### Cenário de Nenhum Resultado:

Dado: Nenhum membro resolveu issues no período filtrado.

Quando: O usuário acessa o dashboard.

Então: O dashboard deve exibir "0" como total de issues resolvidas, e o detalhamento por membro deve mostrar 0 para todos.
