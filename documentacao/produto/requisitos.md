# 📝 Documento de Requisitos

## Requisitos Funcionais (O Que o Sistema Deve Fazer)

### 1. Gestão e Visualização de Projetos

O usuário (Gerente/Líder) deve ter a capacidade de listar e inspecionar os projetos cadastrados, visualizando os seguintes detalhes por projeto:

* **Informações Básicas:**
    * Nome do Projeto
    * Data de Início e Data Final do projeto
    * Timezone associado ao projeto (para consistência de datas)
* **Métricas de Trabalho:**
    * Quantidade total de *Issues*
    * Quantidade total de Horas Registradas
* **Métricas Financeiras (Custo):**
    * Valor da Hora (unitário) do projeto
    * Valor Total de Horas Gastas (cálculo: horas x valor\_hora)
* **Navegação:**
    * Ao selecionar um projeto, o usuário deve ser capaz de visualizar todas as *Issues* que o compõem.

### 2. Visualização de Detalhes de Issues

Para cada *Issue* listada em um projeto, o usuário deve conseguir visualizar as seguintes informações detalhadas:

* Autor da *Issue*
* ID da *Issue* (ex: JIRA-123)
* Data de Criação
* Data de Início/Trabalho na *Issue*
* Tempo Total Gasto na *Issue*

### 3. Gestão de Níveis de Acesso e Usuários

O sistema deve permitir o gerenciamento de usuários, definindo seus privilégios de acesso em três níveis claros de autorização:

1.  Gerente de Projetos
2.  Líder de Equipe
3.  Membro de Equipe

### 4. Dashboard de Projetos (Nível Agregado)

O sistema deve fornecer um *Dashboard* no nível de projetos com as seguintes métricas consolidadas:

* **Métricas Primárias:**
    * Quantidade de *Issues* por projeto.
    * Total de Horas Trabalhadas por projeto.
    * Quantidade de Membros Ativos trabalhando em cada projeto.
* **Filtros Necessários:**
    * Filtro por Projeto.
    * Filtro por Range de Datas de Início e Final do Projeto.

### 5. Dashboard de Issues (Nível Detalhado)

O sistema deve fornecer um *Dashboard* no nível de *Issues* focado em produtividade e resolução, exibindo:

* **Métricas de Desempenho:**
    * Taxa de Conclusão de *Issues* (em porcentagem).
    * Tempo Médio de Resolução de *Issues* (TMR).
* **Métricas por Membro:**
    * *Issues* resolvidas por Membro da Equipe, e totais do time.
    * Horas trabalhadas por Membro da Equipe, e totais do time.
* **Filtros Necessários:**
    * Filtro por Range de Data de Criação da *Issue*.
    * Filtro por Range de Data de Início da *Issue*.
    * Filtro por Membro da Equipe.

---

## 🧩 Requisitos Não Funcionais (Qualidade e Restrições)

### 🚀 Desempenho

* **O sistema deve apresentar as informações de projetos e *Issues* em tempo hábil.**
    * O tempo de resposta para a visualização inicial de qualquer tela **não deve exceder 2 segundos** sob condições normais de uso.
* **O carregamento dos *Dashboards* deve ser otimizado, mesmo com grande volume de dados.**
    * O carregamento completo de um *dashboard* com até 10.000 *issues* ou 50 projetos ativos deve ocorrer em **menos de 5 segundos**. Técnicas como *lazy loading* ou paginação devem ser implementadas.
* **Operações de filtro e busca devem ser processadas de forma eficiente (sem lentidão perceptível).**
    * A aplicação de filtros em listas de até 1.000 itens deve resultar na atualização da tela em **menos de 1 segundo**.
* **A aplicação deve ser escalável, suportando o aumento no número de usuários e dados sem degradação do desempenho.**
    *  A arquitetura deve suportar um crescimento de **50% na base de usuários** e **100% no volume de dados** do Jira durante o primeiro ano, mantendo os tempos de resposta especificados.

### 🔒 Segurança

* **O sistema deve possuir autenticação e autorização baseadas nos três níveis de acesso (Gerente, Líder, Membro).**
    *  A autenticação deve ser realizada via **JWT (JSON Web Tokens)** ou similar, e todas as requisições ao *backend* (APIs) devem ser validadas para garantir que o usuário possua a permissão necessária para a operação (Autorização baseada em Papéis - RBAC).
* **Os dados sensíveis (credenciais, informações de usuários) devem ser armazenados e transmitidos de forma criptografada (HTTPS, *hashing* de senhas).**
    * Todas as senhas devem ser armazenadas utilizando **algoritmos de *hashing* seguro** (ex.: Argon2 ou bcrypt). A comunicação entre o cliente (navegador) e o servidor deve ser **exclusivamente via HTTPS/TLS**.
* **Cada usuário deve ter acesso apenas às informações compatíveis com seu nível de permissão.**
    * O acesso a dados de custo (*valor\_hora\_dev*) deve ser **restrito apenas a Gerentes**. A visibilidade de projetos pode ser configurada por permissão.
* **O sistema deve garantir a integridade dos dados mesmo em casos de falha (ex.: *rollback* em transações incompletas).**
    * O banco de dados deve ser configurado para utilizar transações que garantam as propriedades **ACID**, especialmente em operações de cadastro de usuários e custos por hora.

### 🎨 Usabilidade (UX/UI)

* **A interface deve ser intuitiva e de fácil navegação (sem necessidade de treinamento extenso).**
    * A navegação principal deve ter uma **curva de aprendizado de no máximo 15 minutos** para um novo usuário. Deve haver um guia (*tooltip*) ou tutorial inicial para as funcionalidades mais complexas.
* **Os *Dashboards* devem apresentar informações de forma clara, com gráficos e indicadores visuais que facilitem a leitura.**
    * Devem ser utilizados **padrões de visualização de dados** (ex.: cores consistentes, legendas claras) para evitar a ambiguidade. Métricas críticas (ex.: taxa de conclusão) devem ser destacadas.
* **O *design* deve ser **responsivo**, permitindo o uso em *desktop* e dispositivos móveis.**
    * A aplicação deve ser **totalmente utilizável** em resoluções mínimas de **360px** (móvel) até **1920px** (desktop), sem a necessidade de *scroll* horizontal na maioria das telas.

### ⚙️ Manutenibilidade

* **O código deve seguir padrões de boas práticas (*Clean Code*, SOLID).**
    * Todas as funcionalidades críticas devem ser cobertas por **testes unitários e de integração** (cobertura mínima de 80%). O código deve ser revisado por pares (*code review*).
* **A arquitetura deve ser **modular** para facilitar atualizações e correções.**
    * O *backend* deve seguir uma arquitetura de **Microserviços** ou **Camadas bem definidas** (MVC/Clean Architecture), separando a lógica de negócios da camada de acesso a dados.
* **O sistema deve possuir *logs* e rastreamento de erros para facilitar o diagnóstico de falhas.**
    * *Logs* de nível de erro e aviso devem ser registrados com informações contextuais (usuário, *endpoint*, *stack trace*) e devem ser agregados em uma ferramenta de monitoramento centralizado.

### ⏰ Disponibilidade

* **O sistema deve estar disponível **24 horas por dia, 7 dias por semana** (tempo de indisponibilidade mínimo).**
    * O objetivo de tempo de atividade (*Uptime*) é de **99,9%** ao longo do mês (o que permite aproximadamente 43 minutos de indisponibilidade por mês).
* **Em caso de manutenção programada, os usuários devem ser notificados previamente.**
    * Notificações devem ser enviadas por e-mail e exibidas na interface do sistema com **pelo menos 48 horas de antecedência**.

### 🌐 Portabilidade e Compatibilidade

* **A aplicação deve poder ser executada em diferentes navegadores modernos (*Chrome*, *Firefox*, *Edge*, *Safari*).**
    * O *frontend* deve garantir compatibilidade com as **duas últimas versões estáveis** dos navegadores listados.
* **O *backend* deve ser compatível com contêineres **Docker**.**
    * Devem ser fornecidos **Dockerfiles** e um arquivo **docker-compose** para facilitar a implantação local e em ambientes de produção.
* **O sistema deve permitir integração futura com APIs externas além do Jira (ex.: GitLab, Trello).**
    * A lógica de integração com APIs de terceiros deve ser **abstraída e isolada** em um módulo específico, minimizando o impacto ao adicionar novas fontes de dados.
* **Os formatos de dados trocados (*JSON*, *REST*) devem seguir padrões abertos e documentados.**
    * Todas as APIs internas devem ser **documentadas utilizando o padrão OpenAPI/Swagger**.
