## Requisitos Funcionais (O Que o Sistema Deve Fazer)

### RF1 - Gestão de Projetos
**ID Base:** `RF1-PROJ`

#### `RF1-PROJ-LIST` - **Listagem de Projetos**
- Listar e inspecionar projetos cadastrados
- Visualizar informações básicas:
  - Nome do Projeto
  - Data de Início e Data Final
  - Timezone associado
- Métricas de trabalho:
  - Quantidade total de Issues
  - Quantidade total de Horas Registradas

#### `RF1-PROJ-DETAIL` - **Detalhes do Projeto**
- Visualizar métricas financeiras:
  - Valor da Hora (unitário) do projeto
  - Valor Total de Horas Gastas (horas × valor_hora)
- Navegação para visualizar todas as Issues do projeto

### RF2 - Visualização de Issues
**ID Base:** `RF2-ISSUE`

#### `RF2-ISSUE-LIST` - **Listagem de Issues**
- Listar Issues por projeto selecionado
- Visualização em tabela/grid

#### `RF2-ISSUE-DETAIL` - **Detalhes da Issue**
- Autor da Issue
- ID da Issue (ex: JIRA-123)
- Data de Criação
- Data de Início/Trabalho na Issue
- Tempo Total Gasto na Issue

### RF3 - Gestão de Usuários e Acessos
**ID Base:** `RF3-USER`

#### `RF3-USER-MANAGE` - **Gestão de Usuários**
- Gerenciamento de usuários do sistema
- Definição de privilégios em três níveis:
  - Gerente de Projetos
  - Líder de Equipe
  - Membro de Equipe

### RF4 - Dashboards
**ID Base:** `RF4-DASH`

#### `RF4-DASH-PROJ` - **Dashboard de Projetos**
- Métricas consolidadas:
  - Quantidade de Issues por projeto
  - Total de Horas Trabalhadas por projeto
  - Quantidade de Membros Ativos por projeto
- Filtros:
  - Por Projeto
  - Por Range de Datas de Início e Final

#### `RF4-DASH-ISSUE` - **Dashboard de Issues**
- Métricas de desempenho:
  - Taxa de Conclusão de Issues (%)
  - Tempo Médio de Resolução de Issues (TMR)
- Métricas por membro:
  - Issues resolvidas por Membro
  - Horas trabalhadas por Membro
- Filtros:
  - Range de Data de Criação
  - Range de Data de Início
  - Por Membro da Equipe

---

## 🧩 Requisitos Não Funcionais (Qualidade e Restrições)

### RNF1 - Desempenho
**ID Base:** `RNF1-PERF`

#### `RNF1-PERF-RESPONSE` - **Tempo de Resposta**
- Tempo de resposta para visualização inicial ≤ 2 segundos
- Carregamento de dashboard com 10k issues ou 50 projetos ≤ 5 segundos
- Aplicação de filtros em listas de 1k itens ≤ 1 segundo

#### `RNF1-PERF-SCALE` - **Escalabilidade**
- Suportar crescimento de 50% na base de usuários
- Suportar crescimento de 100% no volume de dados do Jira
- Manter performance durante primeiro ano de operação

### RNF2 - Segurança
**ID Base:** `RNF2-SEC`

#### `RNF2-SEC-AUTH` - **Autenticação**
- Autenticação via JWT (JSON Web Tokens)
- Autorização baseada em papéis (RBAC)
- Validação de permissões em todas as APIs
- Senhas com hashing seguro (Argon2 ou bcrypt)

#### `RNF2-SEC-ACCESS` - **Controle de Acesso**
- Dados sensíveis restritos a Gerentes
- Comunicação exclusivamente via HTTPS/TLS
- Transações ACID no banco de dados
- Integridade de dados em caso de falha

### RNF3 - Usabilidade
**ID Base:** `RNF3-UX`

#### `RNF3-UX-VISUAL` - **Visualização de Dados**
- Gráficos e indicadores visuais claros
- Cores consistentes e legendas claras
- Métricas críticas destacadas

#### `RNF3-UX-RESP` - **Design Responsivo**
- Funcional em resoluções de 360px (mobile) até 1920px (desktop)
- Sem necessidade de scroll horizontal na maioria das telas
- Navegação intuitiva (≤15 minutos para aprendizado)

### RNF4 - Manutenibilidade
**ID Base:** `RNF4-MAIN`

#### `RNF4-MAIN-CODE` - **Qualidade do Código**
- Padrões Clean Code e SOLID
- Testes unitários e de integração (≥80% cobertura)
- Code review por pares obrigatório

#### `RNF4-MAIN-ARCH` - **Arquitetura**
- Arquitetura modular (Microserviços ou Camadas)
- Separação entre lógica de negócio e acesso a dados

#### `RNF4-MAIN-LOGS` - **Monitoramento**
- Logs com informações contextuais (usuário, endpoint, stack trace)
- Agregação em ferramenta de monitoramento centralizado

### RNF5 - Disponibilidade
**ID Base:** `RNF5-AVAIL`

#### `RNF5-AVAIL-UPTIME` - **Tempo de Atividade**
- Disponibilidade 24/7
- Uptime de 99.9% (≈43 minutos de indisponibilidade mensal)

### RNF6 - Portabilidade
**ID Base:** `RNF6-PORT`

#### `RNF6-PORT-BROWSER` - **Compatibilidade Navegadores**
- Compatível com Chrome, Firefox, Edge, Safari
- Suporte às duas últimas versões estáveis

#### `RNF6-PORT-DOCKER` - **Containerização**
- Compatível com contêineres Docker
- Dockerfiles e docker-compose para implantação

#### `RNF6-PORT-API` - **Integração APIs**
- Módulo isolado para APIs de terceiros
- Documentação OpenAPI/Swagger para APIs internas
- Formatos de dados abertos (JSON, REST)
