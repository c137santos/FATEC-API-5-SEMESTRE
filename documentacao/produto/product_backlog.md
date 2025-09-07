# Product backlog

## Objetivos desse documento

Este documento tem como objetivo registrar e estruturar todas as User Stories que compõem o projeto, de forma clara, objetiva e alinhada às necessidades do cliente.
Ele serve como base para o desenvolvimento das funcionalidades priorizadas, facilitando o entendimento
compartilhado entre o Product Owner, equipe técnica e stakeholders.
Além disso, nesse documento estão mapeadas as definitions of ready (DOR) e a definitions of done (DOD).

## Backlog
| Rank | Prioridade | User Story | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Alta | Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação. | | 1 |
| 2 | Alta | Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma. | | 1 |
| 3 | Alta | Como gestor, quero visualizar uma lista dos projetos disponíveis na API do Jira, mostrando para cada um o nome, data de início e fim. | | 1 |
| 4 | Alta | Como gestor, quero visualizar para cada projeto a quantidade de issues e o total de horas registradas. | | 1 |
| 5 | Média | Como gestor, quero um dashboard inicial que mostre a quantidade de issues e horas trabalhadas para um projeto. | | 2 |
| 6 | Média | Como administrador, quero um formulário para cadastrar novos usuários e definir seu nível de acesso: gerente, líder ou membro de equipe. | | 2 |
| 7 | Média | Como gestor, quero visualizar no dashboard de projetos a taxa de conclusão de issues e o tempo médio de resolução do projeto. | | 2 |
| 8 | Média | Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues. | | 3 |
| 9 | Média | Como gestor, quero que o dashboard de issues exiba as issues resolvidas por membro e o total do time. | | 3 |
| 10 | Baixa | Como gestor, quero visualizar no dashboard a quantidade de membros ativos e as horas trabalhadas por cada um. | | 3 |
| 11 | Baixa | Como gestor, quero aplicar filtros por projeto e por intervalo de datas (início e fim) no dashboard. | | 3 |
| 12 | Baixa | Como gestor, quero que o sistema calcule e exiba o valor total de horas gastas (horas x valor_hora) de um projeto. | | 3 |

## Definition of Ready (DoR)
Para que uma User Story seja considerada pronta para a sprint, todos os critérios abaixo devem ser atendidos:

[ ]  Clara e Unificada: A User Story segue o formato padrão (Como <papel>, quero <funcionalidade>, para <objetivo>) e representa uma funcionalidade única.

[ ]  Priorizada: A User Story tem uma prioridade definida e foi ranqueada no Product Backlog.

[ ]  Estimável: A equipe de desenvolvimento discutiu e atribuiu uma estimativa em Story Points para a User Story.

[ ]  Detalhada: Os critérios de aceitação foram escritos de forma clara e objetiva, descrevendo exatamente o que deve ser feito para a história ser considerada completa.

## Definition of Done (DoD)
Para que uma User Story seja considerada concluída, os seguintes critérios devem ser satisfeitos:
### Desenvolvimento
[ ]  O código-fonte da funcionalidade foi desenvolvido e está completo.

[ ]  O código está limpo e bem comentado.

[ ]  Todos os critérios de aceitação da User Story foram implementados.

[ ]  Testes unitários foram criados para o código e todos foram aprovados.

[ ]  Testes de integração foram implementados para garantir que a funcionalidade se comunica corretamente com a API do Jira e outras partes do sistema.

[ ]  O código foi revisado por outro membro do time (Code Review) e as sugestões foram incorporadas.

### Qualidade e Testes
[ ]  Todos os testes de aceitação definidos na User Story foram executados com sucesso.

[ ]  O sistema lida corretamente com cenários de erro (por exemplo, falha na comunicação com a API do Jira, dados ausentes).

[ ]  Os logs de erros foram implementados e estão registrando corretamente as exceções.

[ ]  A funcionalidade foi testada e validada pelo Product Owner.

### Documentação
[ ]  A documentação técnica da API (se houver novos endpoints) foi atualizada.

[ ]  Qualquer nova configuração, comando de instalação ou dependência necessária foi documentada.

[ ]  A documentação de uso, como exemplos de retorno ou prints de tela para os dashboards, foi criada e está pronta.