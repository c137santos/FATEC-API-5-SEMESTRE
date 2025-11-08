| **Capacidade estimada da Equipe por Sprint:** | 16 Story Points |
|-----------------------------------------------|-----------------|
| **Meta da Sprint:**                           | User Stories de rank 4, rank 5, rank 6 (total de *13 Story Points*) |
| **Previsão da Sprint (extras, sem compromisso de entrega):** | User Stories de rank 7 e rank 8 (*6 Story Points*) |

### Requisitos

[Requisitos Relacionados](../../../README.md#requisitos)

# Backlog da Sprint 2

| Rank | Prioridade | User Story | Requisitos Relacionados | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4 | Alta | Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#2">[2]</a>, <a href="../../../README.md#7">[7]</a> | 3 | 2 |
| 5 | Alta | Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma. | <a href="#1">[1]</a>, <a href="#7">[7]</a>, <a href="#8">[8]</a> | 5 | 2 |
| 6 | Alta | Como gerente, desejo poder cadastrar e analisar os custos do valor da hora trabalhado por dev em cada projeto. | <a href="../../../README.md#5">[5]</a>, <a href="../../../README.md#6">[6]</a>, <a href="../../../README.md#7">[7]</a> | 5 | 2 |
| 7 | Média | Como gestor, quero visualizar no dashboard a quantidade de membros ativos e as horas trabalhadas por cada um. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#2">[2]</a>, <a href="../../../README.md#8">[8]</a> | 3 | 3 |
| 8 | Média | Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#3">[3]</a>, <a href="../../../README.md#7">[7]</a> | 3 | 3 |

### 🔗 Referências
Todos os requisitos detalhados estão aqui: [Requisitos Detalhados](../requisitos.md)

---

## User Story 4 (Rank 4 - 3 SP)
**Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação.**

### Critérios de Aceitação:

**CA4.1 - Navegação para Lista**
- DADO que estou no dashboard de um projeto
- QUANDO clico em "Ver todas as issues" ou botão similar
- ENTÃO devo ser direcionado para a rota `projects/{id}/issues`
- E o projeto selecionado deve ser mantido no contexto

**CA4.2 - Colunas da Lista**
- DADO que estou na lista de issues
- QUANDO visualizo a tabela
- ENTÃO devo ver as colunas:
  - "Issue ID" (ex: SM2-82)
  - "Issue Summary" (descrição da issue)
  - "Author" (nome do usuário relacionado)
  - "Time Created" (data de criação formatada DD/MM/AAAA)

**CA4.3 - Dados das Issues do Projeto SM2**
- DADO que selecionei o projeto SM2
- QUANDO visualizo a lista
- ENTÃO devo ver issues como:
  - "SM2-82: Editar a Descrição Categoria - Gestão"
  - Autor conforme dados do Jira
  - Datas formatadas corretamente no fuso "America/Sao_Paulo"

**CA4.4 - Paginação**
- DADO que o projeto tem múltiplas issues (ex: SM2 com 82 issues)
- QUANDO visualizo a lista
- ENTÃO deve haver paginação funcional
- E deve ser possível navegar entre páginas
- E os parâmetros de paginação (quantidade de items por página e página atual) devem ser enviados ao endpoint

**CA4.5 - Consumo do Endpoint**
- DADO que a tela foi acessada
- QUANDO a lista é carregada
- ENTÃO deve consumir o endpoint `GET /api/core/issues`
- E deve passar corretamente os parâmetros de paginação
- E deve receber: jira_id, descricao_issue, data_criacao, nome do usuário, tempo gasto

**CA4.6 - Tratamento de Erros**
- DADO que o endpoint pode falhar
- QUANDO há erro na requisição
- ENTÃO devo ver mensagem "Erro ao carregar issues. Tente novamente."
- E um botão "Tentar novamente"

---

## User Story 5 (Rank 5 - 5 SP)
**Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma.**

### Critérios de Aceitação:

**CA5.1 - Popup de Detalhes**
- DADO que estou visualizando a lista de issues
- QUANDO clico em uma issue da tabela
- ENTÃO deve abrir um popup/modal com informações adicionais
- E o popup deve ter botão de fechar

**CA5.2 - Informações no Popup**
- DADO que abri o popup de uma issue
- QUANDO visualizo o conteúdo
- ENTÃO devo ver:
  - Issue ID (ex: SM2-82)
  - Issue Summary (descrição completa)
  - Author (nome do usuário)
  - Time Created (data de criação formatada)
  - Tempo Total Gasto (em horas, formato "150.5h")

**CA5.3 - Formatação do Tempo Gasto**
- DADO que a issue possui worklog registrado
- QUANDO visualizo o tempo no popup
- ENTÃO deve aparecer no formato "XXX.Xh" (máximo 1 casa decimal)
- E deve somar todos os worklogs da issue
- E valores menores que 1h devem aparecer como "0.5h"

**CA5.4 - Issues Sem Worklog**
- DADO que uma issue não tem tempo registrado
- QUANDO abro seu popup
- ENTÃO deve mostrar "Tempo gasto: 0h"
- E não deve haver erro na interface

**CA5.5 - Dados Consistentes**
- DADO que o popup utiliza as mesmas informações do endpoint de listagem
- QUANDO abro o popup
- ENTÃO os dados devem ser idênticos aos da tabela
- E não deve haver necessidade de nova requisição

**CA5.6 - Responsividade do Popup**
- DADO que acesso de diferentes dispositivos
- QUANDO abro o popup
- ENTÃO deve funcionar em mobile, tablet e desktop
- E deve ter tamanho adequado para cada tela

---

## User Story 6 (Rank 6 - 5 SP)
**Como gerente, desejo poder cadastrar e analisar os custos do valor da hora trabalhado por dev em cada projeto.**

### Critérios de Aceitação:

**CA6.1 - Alteração no Banco de Dados**
- DADO que precisamos armazenar o valor da hora por desenvolvedor
- QUANDO implemento a solução
- ENTÃO deve ser adicionado o campo `valor_hora` na tabela `accounts_user`
- OU caso não seja possível alterar essa tabela (por regras do Django), deve ser proposta e aprovada solução alternativa
- E a implementação deve ser feita após aprovação do time

**CA6.2 - Endpoint de Edição**
- DADO que preciso atualizar o valor da hora de um desenvolvedor
- QUANDO faço requisição ao endpoint `PATCH /api/core/projects/desenvolvedores/valor`
- ENTÃO devo enviar: id do usuário e novo valor_hora
- E o sistema deve atualizar a tabela no banco
- E deve retornar confirmação de sucesso

**CA6.3 - Tabela de Desenvolvedores**
- DADO que estou na página de um projeto
- QUANDO visualizo a seção de desenvolvedores
- ENTÃO devo ver uma tabela com as colunas:
  - "Nome do Desenvolvedor"
  - "Horas Trabalhadas"
  - "Valor da Hora"
  - Botão "Editar"

**CA6.4 - Consumo do Endpoint de Listagem**
- DADO que a página do projeto foi carregada
- QUANDO a tabela de desenvolvedores é exibida
- ENTÃO deve consumir `GET /api/core/projects/desenvolvedores`
- E deve receber: nome do desenvolvedor, horas trabalhadas, valor da hora

**CA6.5 - Popup de Edição**
- DADO que estou visualizando a tabela de desenvolvedores
- QUANDO clico no botão "Editar" de um desenvolvedor
- ENTÃO deve abrir um popup/modal de edição
- E deve conter um input para o valor da hora
- E deve ter botões "Salvar" e "Cancelar"

**CA6.6 - Salvamento do Valor**
- DADO que editei o valor da hora no popup
- QUANDO clico em "Salvar"
- ENTÃO deve chamar o endpoint `PATCH /api/core/projects/desenvolvedores/valor`
- E deve enviar o id do usuário e o novo valor_hora
- E deve atualizar a tabela após sucesso
- E deve fechar o popup
- E deve mostrar mensagem de confirmação

**CA6.7 - Validação de Entrada**
- DADO que estou editando o valor da hora
- QUANDO insiro um valor
- ENTÃO deve aceitar apenas números positivos
- E deve aceitar casas decimais (ex: 150.50)
- E deve mostrar mensagem de erro para valores inválidos

**CA6.8 - Tratamento de Erros**
- DADO que o endpoint de edição pode falhar
- QUANDO há erro na requisição
- ENTÃO deve mostrar mensagem "Erro ao salvar. Tente novamente."
- E não deve fechar o popup
- E deve permitir nova tentativa

---

## User Story 7 (Rank 7 - 3 SP - Extra/Sem Compromisso)
**Como gestor, quero visualizar no dashboard a quantidade de membros ativos e as horas trabalhadas por cada um.**

### Critérios de Aceitação:

**CA7.1 - Seção de Membros no Dashboard**
- DADO que estou no dashboard de um projeto
- QUANDO visualizo a página
- ENTÃO devo ver uma seção "Membros da Equipe"
- E deve estar visível sem necessidade de scroll excessivo

**CA7.2 - Card de Total de Membros**
- DADO que o projeto tem membros ativos
- QUANDO visualizo o dashboard
- ENTÃO devo ver um card "Membros Ativos: X"
- E o número deve refletir a quantidade de desenvolvedores com horas registradas

**CA7.3 - Tabela de Membros e Horas**
- DADO que estou visualizando a seção de membros
- QUANDO carrego o dashboard
- ENTÃO devo ver uma tabela com:
  - "Nome do Desenvolvedor"
  - "Horas Trabalhadas"
  - "Valor da Hora"
- E deve consumir `GET /api/core/projects/desenvolvedores`

**CA7.4 - Ordenação por Horas**
- DADO que tenho múltiplos membros na tabela
- QUANDO visualizo a lista
- ENTÃO os membros devem estar ordenados por horas trabalhadas (decrescente)
- E deve ser possível identificar quem trabalhou mais no projeto

**CA7.5 - Formatação de Horas**
- DADO que cada membro tem horas registradas
- QUANDO visualizo a tabela
- ENTÃO as horas devem estar no formato "XXX.Xh"
- E deve mostrar máximo 1 casa decimal

**CA7.6 - Membros Sem Horas**
- DADO que um membro não tem horas registradas
- QUANDO visualizo a tabela
- ENTÃO deve aparecer "0h" para esse membro
- E ele ainda deve ser listado

---

## User Story 8 (Rank 8 - 3 SP - Extra/Sem Compromisso)
**Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues.**

### Critérios de Aceitação:

**CA8.1 - Campos de Filtro de Data**
- DADO que estou no dashboard do projeto
- QUANDO visualizo a seção de filtros
- ENTÃO devo ver dois campos de data:
  - "Data Inicial"
  - "Data Final"
- E ambos devem ser date pickers funcionais

**CA8.2 - Valores Pré-preenchidos**
- DADO que acessei o dashboard pela primeira vez
- QUANDO os campos de data são exibidos
- ENTÃO devem vir pré-preenchidos com:
  - Data Inicial: data de início do projeto
  - Data Final: data final do projeto (ou data atual se projeto ativo)

**CA8.3 - Descrição do Projeto**
- DADO que estou visualizando os filtros
- QUANDO carrego o dashboard
- ENTÃO devo ver a descrição do projeto acima dos campos de data
- E a descrição deve vir do endpoint atualizado

**CA8.4 - Aplicação dos Filtros**
- DADO que alterei as datas de filtro
- QUANDO clico em "Aplicar" ou similar
- ENTÃO o dashboard deve recarregar
- E deve mostrar apenas dados dentro do intervalo selecionado
- E os cards de métricas devem refletir os dados filtrados

**CA8.5 - Atualização do Endpoint**
- DADO que os filtros foram aplicados
- QUANDO faço requisição ao endpoint `projects/<int:project_id>`
- ENTÃO devo enviar os parâmetros de data (data_inicial e data_final)
- E o endpoint deve retornar dados filtrados
- E deve incluir a descrição do projeto na resposta

**CA8.6 - Validação de Intervalo**
- DADO que estou selecionando datas
- QUANDO insiro as datas
- ENTÃO a data final não pode ser anterior à data inicial
- E deve mostrar mensagem de erro caso o intervalo seja inválido

**CA8.7 - Reset de Filtros**
- DADO que apliquei filtros personalizados
- QUANDO clico em "Limpar filtros" ou similar
- ENTÃO os campos devem voltar aos valores padrão (datas do projeto)
- E o dashboard deve recarregar com todos os dados

**CA8.8 - Persistência Visual**
- DADO que apliquei filtros
- QUANDO visualizo o dashboard
- ENTÃO deve haver indicação visual de que filtros estão ativos
- E os valores dos campos devem permanecer visíveis

---

**Critérios de Pronto da Sprint 2:**
- Todas as user stories de rank 4-6 atendem seus critérios de aceitação
- Alteração no banco de dados implementada e documentada
- Testes manuais validam com dados reais da API da Necto
- Tratamento de erros implementado em todos os endpoints
- Código revisado e sem bugs críticos
