| **Capacidade estimada da Equipe por Sprint:** | 16 Story Points |
|-----------------------------------------------|-----------------|
| **Meta da Sprint:** | User Stories de rank 9, rank 10, rank 11 (total de *16 Story Points*) |
| **Previsão da Sprint (extras, sem compromisso de entrega):** | User Story de rank 12 e 13 (*3 e 5 Story Points*) |

### Requisitos

[Requisitos Relacionados](../../../README.md#requisitos)

# Backlog da Sprint 3

| Rank | Prioridade | User Story | Requisitos Relacionados | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 9 | Alta | Como administrador, quero um formulário para cadastrar novos usuários. | <a href="../../../README.md#5">[5]</a> | 8 | 3 |
| 10 | Alta | Como usuário, quero que ao logar no sistema, apresente minhas permissões as quais condizem com meu cargo (gerente, líder ou membro de equipe). | <a href="../../../README.md#5">[5]</a>, <a href="../../../README.md#6">[6]</a> | 3 | 3 |
| 11 | Média | Como gestor, quero visualizar um dashboard de um projeto específico que mostra a taxa de conclusão de issues e o tempo médio de resolução do projeto. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#2">[2]</a>, <a href="../../../README.md#8">[8]</a> | 5 | 3 |
| 12 | Média | Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#3">[3]</a>, <a href="../../../README.md#7">[7]</a> | 3 | 3 |
| 13 | Baixa | Como gestor, quero visualizar no dashboard de projeto específico a quantidade de membros ativos e as horas trabalhadas por cada um. | <a href="../../../README.md#1">[1]</a>, <a href="../../../README.md#2">[2]</a>, <a href="../../../README.md#8">[8]</a> | 5 | 3 |

### 🔗 Referências
Todos os requisitos detalhados estão aqui: [Requisitos Detalhados](../requisitos.md)

---

## User Story 9 (Rank 9 - 8 SP)
**Como administrador, quero um formulário para cadastrar novos usuários.**

### Critérios de Aceitação:

**CA9.1 - Acesso ao Formulário**
- DADO que sou um Administrador logado
- QUANDO navego para a seção de Administração
- ENTÃO devo ver a opção "Cadastrar Novo Usuário"
- E ao clicar, devo ser direcionado para o formulário.

**CA9.2 - Campos do Formulário**
- DADO que estou no formulário de cadastro de usuário
- QUANDO visualizo os campos
- ENTÃO devo ver campos para:
    - Nome Completo
    - Email (deve ser único e com validação de formato)
    - Senha (com validação de complexidade, ex: mínimo 8 caracteres)
    - Nível de Acesso (dropdown com opções: Gerente, Líder de Equipe, Membro de Equipe)
    - Valor da Hora (campo numérico opcional com 2 casas decimais)

**CA9.3 - Submissão do Formulário**
- DADO que preenchi todos os campos obrigatórios corretamente
- QUANDO clico em "Salvar Usuário"
- ENTÃO deve ser feita uma requisição `POST` para o endpoint de cadastro de usuário
- E o usuário deve ser criado no banco de dados com as permissões corretas.
- E devo ser redirecionado para a tela de listagem de usuários com uma mensagem de sucesso.

**CA9.4 - Tratamento de Erro de Duplicidade**
- DADO que tentei cadastrar um usuário com um Email já existente
- QUANDO submeto o formulário
- ENTÃO o sistema deve retornar um erro de validação
- E devo ver a mensagem: "Este e-mail já está em uso."

---

## User Story 10 (Rank 10 - 3 SP)
**Como usuário, quero que ao logar no sistema, apresente minhas permissões as quais condizem com meu cargo (gerente, líder ou membro de equipe).**

### Critérios de Aceitação:

**CA10.1 - Redirecionamento Pós-Login**
- DADO que me loguei com sucesso
- QUANDO o login é validado
- ENTÃO o sistema deve carregar as informações do meu nível de acesso (`cargo`)
- E devo ser redirecionado para a página inicial (dashboard) compatível com meu cargo.

**CA10.2 - Visibilidade da Navegação**
- DADO que estou logado
- QUANDO visualizo o menu de navegação
- ENTÃO as opções disponíveis devem refletir meu nível de acesso:
    - Administrador: Vê todas as opções (inclusive cadastro de usuário).
    - Gerente: Vê dashboards de projetos e custos.
    - Membro/Líder: Vê apenas os dashboards e issues dos projetos a que pertence.

**CA10.3 - Endpoint de Perfil**
- DADO que o sistema está carregando o perfil
- QUANDO faz a requisição de informações do usuário
- ENTÃO o endpoint de perfil deve retornar o campo `cargo` (ou `nivel_acesso`)
- E o valor deve ser um dos definidos: "gerente", "lider", "membro".

**CA10.4 - Tratamento de Nível Indefinido**
- DADO que um usuário possui nível de acesso nulo/indefinido no banco de dados
- QUANDO ele tenta logar
- ENTÃO ele deve ser classificado como "Membro de Equipe" por padrão
- E um alerta deve ser enviado ao Administrador para revisar seu cadastro.

---

## User Story 11 (Rank 11 - 5 SP)
**Como gestor, quero visualizar um dashboard de um projeto específico que mostra a taxa de conclusão de issues e o tempo médio de resolução do projeto.**

### Critérios de Aceitação:

**CA11.1 - Taxa de Conclusão (Gráfico)**
- DADO que estou no dashboard de um projeto
- QUANDO visualizo a seção de métricas
- ENTÃO deve haver um gráfico ou indicador (ex: Donut Chart) mostrando:
    - Quantidade total de issues.
    - Quantidade de issues concluídas (Status 'Done').
    - Quantidade de issues pendentes.
    - A Taxa de Conclusão em porcentagem (Issues Concluídas / Total de Issues * 100).

**CA11.2 - Cálculo do Tempo Médio de Resolução (TMR)**
- DADO que o projeto tem issues concluídas
- QUANDO o TMR é exibido
- ENTÃO deve ser calculado como: Soma do Tempo Gasto em Issues Concluídas / Quantidade de Issues Concluídas
- E deve ser exibido em um card de métrica de destaque.

**CA11.3 - Formato do TMR**
- DADO que o TMR foi calculado
- QUANDO é exibido no dashboard
- ENTÃO deve ser apresentado no formato de horas (ex: "8.5h", "120.3h").

**CA11.4 - TMR para Projetos Sem Conclusão**
- DADO que o projeto não possui issues concluídas
- QUANDO o dashboard é carregado
- ENTÃO deve ser exibido "TMR: N/A" ou "TMR: 0h".

**CA11.5 - Atualização com Filtros**
- DADO que filtros de data ou membro foram aplicados no dashboard
- QUANDO as métricas são recarregadas
- ENTÃO o TMR e a Taxa de Conclusão devem ser recalculados apenas com base nas issues que atendem aos filtros.

---

## User Story 12 (Rank 12 - 5 SP)
**Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues.**

### Critérios de Aceitação

**CA12.1 - Exibição dos Filtros**
- DADO que sou um Líder de Equipe logado
- QUANDO acesso o dashboard de issues
- ENTÃO devo visualizar os filtros disponíveis para:
    - Intervalo de Datas de Criação (com campos “Data Inicial” e “Data Final”)
    - Membro Responsável (dropdown com a lista de membros da equipe)

**CA12.2 - Aplicação de Filtro por Intervalo de Datas**
- DADO que estou no dashboard de issues
- QUANDO seleciono um intervalo de datas de criação válido
- ENTÃO o dashboard deve exibir apenas as issues criadas dentro desse intervalo e deve atualizar automaticamente os gráficos e listas correspondentes.

**CA12.3 - Aplicação de Filtro por Membro**
- DADO que estou no dashboard de issues
- QUANDO seleciono um membro específico no filtro de “Membro Responsável”
- ENTÃO o dashboard deve exibir apenas as issues atribuídas a esse membro e atualizar as métricas e gráficos relacionados.

**CA12.4 - Combinação de Filtros**
- DADO que selecionei tanto um intervalo de datas quanto um membro
- QUANDO aplico os filtros
- ENTÃO o dashboard deve exibir apenas as issues que atendam a ambos os critérios simultaneamente.

**CA12.5 - Limpeza dos Filtros**
- DADO que há filtros aplicados
- QUANDO clico em “Limpar Filtros”
- ENTÃO todos os campos de filtro devem ser resetados e o dashboard deve voltar a exibir todas as issues sem filtragem.

**CA12.6 - Validação de Intervalo Inválido**
- DADO que inseri uma “Data Inicial” posterior à “Data Final”
- QUANDO tento aplicar o filtro
- ENTÃO o sistema deve exibir uma mensagem de erro:
    - “O intervalo de datas é inválido. Verifique os valores informados.” E os filtros não devem ser aplicados até correção.

---

## User Story 13 (Rank 13 - 5 SP - Extra)
**Como gestor, quero visualizar no dashboard de projeto específico a quantidade de membros ativos e as horas trabalhadas por cada um.**

### Critérios de Aceitação:

**CA12.1 - Card de Membros Ativos**
- DADO que estou no dashboard do projeto
- QUANDO visualizo a seção de métricas
- ENTÃO deve haver um card de destaque mostrando: "X Membros Ativos"
- E "Membros Ativos" são definidos como usuários que registraram worklogs no projeto.

**CA12.2 - Tabela de Detalhes dos Membros**
- DADO que estou no dashboard
- QUANDO visualizo a seção de detalhes
- ENTÃO deve haver uma tabela "Horas Trabalhadas por Membro"
- E esta tabela deve conter as colunas: Nome do Membro, Horas Totais Trabalhadas, e Valor da Hora (por membro, conforme cadastro).

**CA12.3 - Ordenação da Tabela**
- DADO que a tabela de membros é carregada
- QUANDO os dados são exibidos
- ENTÃO a lista deve ser ordenada por "Horas Totais Trabalhadas" de forma decrescente.

**CA12.4 - Consumo do Endpoint**
- DADO que a tela do dashboard é carregada
- QUANDO as informações de membros são exibidas
- ENTÃO deve consumir o endpoint `GET /api/core/projects/<id>/desenvolvedores`
- E este endpoint deve retornar o nome do membro e o total de horas registradas no projeto.

**CA12.5 - Formato das Horas**
- DADO que as horas trabalhadas são exibidas
- QUANDO visualizo o valor
- ENTÃO deve estar no formato "XXX.Xh" (máximo 1 casa decimal).
