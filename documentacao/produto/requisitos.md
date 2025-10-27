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

* O sistema deve apresentar as informações de projetos e *Issues* em tempo hábil.
* O carregamento dos *Dashboards* deve ser otimizado, mesmo com grande volume de dados.
* Operações de filtro e busca devem ser processadas de forma eficiente (sem lentidão perceptível).
* A aplicação deve ser escalável, suportando o aumento no número de usuários e dados sem degradação do desempenho.

### 🔒 Segurança

* O sistema deve possuir autenticação e autorização baseadas nos três níveis de acesso (Gerente, Líder, Membro).
* Os dados sensíveis (credenciais, informações de usuários) devem ser armazenados e transmitidos de forma criptografada (HTTPS, *hashing* de senhas).
* Cada usuário deve ter acesso apenas às informações compatíveis com seu nível de permissão.
* O sistema deve garantir a integridade dos dados mesmo em casos de falha (ex.: *rollback* em transações incompletas).

### 🎨 Usabilidade (UX/UI)

* A interface deve ser intuitiva e de fácil navegação (sem necessidade de treinamento extenso).
* Os *Dashboards* devem apresentar informações de forma clara, com gráficos e indicadores visuais que facilitem a leitura.
* O *design* deve ser **responsivo**, permitindo o uso em *desktop* e dispositivos móveis.

### ⚙️ Manutenibilidade

* O código deve seguir padrões de boas práticas (*Clean Code*, SOLID).
* A arquitetura deve ser **modular** para facilitar atualizações e correções.
* O sistema deve possuir *logs* e rastreamento de erros para facilitar o diagnóstico de falhas.

### ⏰ Disponibilidade

* O sistema deve estar disponível **24 horas por dia, 7 dias por semana** (tempo de indisponibilidade mínimo).
* Em caso de manutenção programada, os usuários devem ser notificados previamente.

### 🌐 Portabilidade e Compatibilidade

* A aplicação deve poder ser executada em diferentes navegadores modernos (*Chrome*, *Firefox*, *Edge*, *Safari*).
* O *backend* deve ser compatível com contêineres **Docker**.
* O sistema deve permitir integração futura com APIs externas além do Jira (ex.: GitLab, Trello).
* Os formatos de dados trocados (*JSON*, *REST*) devem seguir padrões abertos e documentados.
