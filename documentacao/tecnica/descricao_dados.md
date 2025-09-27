# Dicionário de Dados do Sistema 


## 1. Tabela: `issue` (Modelo `Issue`)

| Coluna | Tipo (Django) | Nulável? | Chave | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `AutoField` | Não | **PK** | Identificador único da Issue (Gerado Automaticamente) |
| **description** | `CharField(512)` | Não | | Título ou descrição curta |
| **details** | `TextField` | Sim (Blank) | | Descrição longa ou detalhes adicionais |
| **created\_at** | `DateTimeField` | Não | | Data e hora de criação (Preenchido automaticamente) |
| **start\_date** | `DateTimeField` | Sim | | Data de início planejada ou real |
| **end\_date** | `DateTimeField` | Sim | | Data de término planejada ou real |
| **time\_estimate\_seconds** | `IntegerField` | Sim | | Estimativa de tempo para conclusão, em segundos |
| **id\_user\_id** | `ForeignKey` | Sim | **FK** | O usuário responsável (Conecta a `settings.AUTH_USER_MODEL`) |
| **project\_id** | `ForeignKey` | Sim | **FK** | O projeto ao qual a issue pertence (Conecta a `projeto`) |
| **type\_issue\_id** | `ForeignKey` | Sim | **FK** | O tipo da issue (ex: História, Tarefa, Bug) (Conecta a `type_issue`) |
| **jira\_id** | `IntegerField` | Sim | | Identificador único da issue no Jira |

---

## 2. Tabela: `type_issue` (Modelo `IssueType`)

| Coluna | Tipo (Django) | Nulável? | Chave | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `AutoField` | Não | **PK** | |
| **name** | `CharField(255)` | Não | | Nome do tipo de issue (ex: História, Tarefa, Bug) |
| **description** | `TextField` | Não | | Descrição detalhada do tipo |
| **subtask** | `BooleanField` | Não | | Indica se este tipo é uma subtarefa |
| **jira\_id** | `IntegerField` | Não | **UNIQUE** | Identificador único do tipo de issue no Jira |

---

## 3. Tabela: `projeto` (Modelo `Project`)

| Coluna | Tipo (Django) | Nulável? | Chave | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `AutoField` | Não | **PK** | |
| **key** | `CharField(50)` | Não | **UNIQUE** | A sigla identificadora |
| **name** | `CharField(255)` | Não | | Nome do projeto |
| **description** | `TextField` | Não | | Descrição detalhada do projeto |
| **start\_date\_project** | `DateField` | Sim | | Data de início do projeto |
| **end\_date\_project** | `DateField` | Sim | | Data limite de conclusão |
| **uuid** | `TextField` | Não | **UNIQUE** | Identificador único do Jira |
| **jira\_id** | `IntegerField` | Não | **UNIQUE** | Identificador numérico do Jira |
| **projectTypeKey** | `CharField(100)` | Não | | Tipo do projeto no Jira |

---

## 4. Tabela: `log_tempo` (Modelo `TimeLog`)

| Coluna | Tipo (Django) | Nulável? | Chave | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `AutoField` | Não | **PK** | |
| **id\_issue\_id** | `ForeignKey` | Não | **FK** | Referência para a Issue à qual este log de tempo pertence (Conecta a `issue`) |
| **id\_user\_id** | `ForeignKey` | Sim | **FK** | Usuário que registrou o tempo (Conecta a `settings.AUTH_USER_MODEL`) |
| **seconds** | `IntegerField` | Não | | Quantidade de tempo registrada, em segundos |
| **log\_date** | `DateTimeField` | Não | | Data e hora em que o tempo foi registrado (Preenchido automaticamente) |
| **description\_log** | `TextField` | Não | | Descrição ou comentário sobre o trabalho realizado |
| **jira\_id** | `IntegerField` | Não | **UNIQUE** | Identificador único do log de tempo no Jira |

---

## 5. Tabela: `type_status` (Modelo `StatusType`)

| Coluna | Tipo (Django) | Nulável? | Chave | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `AutoField` | Não | **PK** | |
| **key** | `CharField(255)` | Não | | Chave para categoria |
| **name** | `TextField` | Não | | Nome do status |
| **jira\_id** | `IntegerField` | Não | **UNIQUE** | Identificador único do Jira |

---

## 6. Tabela: `status_log` (Modelo `StatusLog`)

| Coluna | Tipo (Django) | Nulável? | Chave | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `AutoField` | Não | **PK** | |
| **id\_issue\_id** | `ForeignKey` | Não | **FK** | Id conexão tabela Issue (Conecta a `issue`) |
| **created\_at** | `DateTimeField` | Não | | Data de criação do log (Preenchido automaticamente) |
| **old\_status\_id** | `ForeignKey` | Sim | **FK** | Id conexão com Status que represente o anterior (Conecta a `type_status`) |
| **new\_status\_id** | `ForeignKey` | Sim | **FK** | Id conexão com Status que represente o atual (Conecta a `type_status`) |
