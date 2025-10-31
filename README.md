# API 5º Semestre Banco de dados

# Necto <-> Jibóia

<p align="center">
      <h2 align="center"> 🐍</h2>
      <h2 align="center"> Jibóia</h2>
</p>

<p align="center">
  | <a href ="#desafio"> Desafio</a>  |
  <a href ="#solucao"> Solução</a>  |
  <a href ="#requisitos"> Requisitos do Cliente</a>  |
  <a href ="#backlog"> Backlog do Produto</a>  |
  <a href ="#dor">DoR</a>  |
  <a href ="#dod">DoD</a>  |
  <a href ="#sprint"> Cronograma de Sprints</a>  |
  <a href ="#tecnologias">Tecnologias</a> |
  <a href ="#manual">Manual de Instalação</a>  |
  <a href ="#branchs">Manual de Branchs</a>  |
  <a href ="#pb">Product backlog -> DOR e DOD</a>  |
  <a href ="#manual_usuario">Manual do usuário</a>  |
  <a href ="#equipe"> Equipe</a> |
</p>

> Status do Projeto: Em progresso  🚧
>
>
> Pasta de Documentação: [Link](./documentacao) 📄
>
> Video do Projeto:  Em progresso  📽️

## 🏅 Desafio <a id="desafio"></a>

Esse desafio consiste em criar uma ferramenta analítica que consuma dados diretamente por meio da api do jira, consolide-os em um data warehouse e permita gerar indicadores, dashboard e boards sobre o andamento do projeto.
## 🏅 Solução <a id="solucao"></a>

Jiboia é um sistema de ETL de dados do Jira que transforma informações brutas em métricas úteis para acompanhamento de projetos.
O objetivo é dar visibilidade sobre o andamento, esforço e performance das equipes, oferecendo dashboards detalhados tanto em nível de projetos quanto de issues.

---

## 🧩 Requisitos do Cliente <a id="requisitos"></a>

Esta seção define os requisitos que são referenciados nas User Stories. Cada número entre colchetes (`[#]`) serve como âncora para rastreabilidade.

### 📝 Requisitos

* **<a id="1">[1]</a>** O sistema deve apresentar as informações de projetos e issues em tempo hábil.
* **<a id="2">[2]</a>** O carregamento dos dashboards (de projetos e de issues) deve ser otimizado, mesmo com grande volume de dados.
* **<a id="3">[3]</a>** Operações de filtro e busca devem ser processadas de forma eficiente, sem travamentos ou lentidão perceptível ao usuário.
* **<a id="4">[4]</a>** A visualização de informações do Jira deve ser realizada via integração API.
* **<a id="5">[5]</a>** O sistema deve prover um módulo seguro para cadastro e gestão de usuários e permissões.
* **<a id="6">[6]</a>** Os dados de custo e valor de hora/dev devem ser protegidos por controle de acesso baseado em cargo (Gerente).
* **<a id="7">[7]</a>** A interface do usuário deve ser intuitiva e responsiva em diferentes dispositivos.
* **<a id="8">[8]</a>** Todos os cálculos de tempo, custo e métricas devem ser precisos e auditáveis.
* **<a id="9">[9]</a>** O dashboard inicial deve ser o ponto de entrada para o usuário após o login.

### 🔗 Referências
Todos os requisitos detalhados estão aqui: [Requisitos Detalhados](./documentacao/produto/requisitos.md)

---

## 📋 Backlog do Produto <a id="backlog"></a>

| Rank | Prioridade | User Story | Requisitos Relacionados | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Alta | Como gestor, quero visualizar uma lista dos projetos disponíveis na API do Jira, mostrando para cada um o nome, data de início e fim. | <a href="#1">[1]</a>, <a href="#7">[7]</a> | 3 | 1 |
| 2 | Alta | Como gestor, quero visualizar para cada projeto a quantidade de issues e o total de horas registradas. | <a href="#1">[1]</a>, <a href="#8">[8]</a> | 3 | 1 |
| 3 | Alta | Como gestor, quero um dashboard inicial que mostre a quantidade de issues e horas trabalhadas para um projeto. | <a href="#1">[1]</a>, <a href="#2">[2]</a>, <a href="#7">[7]</a>, <a href="#8">[8]</a>, <a href="#9">[9]</a> | 8 | 1 |
| 4 | Alta | Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação. | <a href="#1">[1]</a>, <a href="#2">[2]</a>, <a href="#7">[7]</a> | 3 | 2 |
| 5 | Alta | Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma. | <a href="#1">[1]</a>, <a href="#7">[7]</a>, <a href="#8">[8]</a> | 5 | 2 |
| 6 | Alta | Como gerente, desejo poder cadastrar e analisar os custos do valor da hora trabalhado por dev em cada projeto. | <a href="#5">[5]</a>, <a href="#6">[6]</a>, <a href="#7">[7]</a> | 5 | 2 |
| 7 | Média | Como gestor, quero visualizar no dashboard a quantidade de membros ativos e as horas trabalhadas por cada um. | <a href="#1">[1]</a>, <a href="#2">[2]</a>, <a href="#8">[8]</a> | 3 | 3 |
| 8 | Média | Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues. | <a href="#1">[1]</a>, <a href="#3">[3]</a>, <a href="#7">[7]</a> | 3 | 3 |
| 9 | Alta | Como administrador, quero um formulário para cadastrar novos usuários. | <a href="#5">[5]</a> | 8 | 3 |
| 10 | Alta | Como usuário, quero que ao logar no sistema, apresente minhas permissões as quais condizem com meu cargo (gerente, líder ou membro de equipe). | <a href="#5">[5]</a>, <a href="#6">[6]</a> | 3 | 3 |
| 11 | Média | Como gestor, quero visualizar um dashboard de um projeto específico que mostra a taxa de conclusão de issues e o tempo médio de resolução do projeto. | <a href="#1">[1]</a>, <a href="#2">[2]</a>, <a href="#8">[8]</a> | 5 | 3 |
| 12 | Baixa | Como gestor, quero que o sistema calcule e exiba o valor total de horas gastas (horas x valor_hora) de um projeto. | <a href="#8">[8]</a> | 5 | 3 |

## 📅 Cronograma de Sprints <a id="sprint"></a>
| Sprint          |    Período    | Documentação                                     | Vídeo Entrega                                     |
| --------------- | :-----------: | ------------------------------------------------ | ------------------------------------------------ |
| 🔖 **SPRINT 1** | 08/09 - 28/09 | [Sprint 1 Docs](./documentacao/produto/backlog%20sprints/sprint1.md) | [Sprint 1 entrega](https://drive.google.com/file/d/1lTRNIouHLhvxYD-sD-3FFqk2J7dnPl_7/view?usp=sharing) |
| 🔖 **SPRINT 2** | 06/10 - 26/10 | [Sprint 2 Docs](./documentacao/produto/backlog%20sprints/sprint2.md) | [Sprint 2 entrega](https://drive.google.com/file/d/1ts-Tc75Hhq3WGDdZoDllG1HI9AAI6o32/view?usp=sharing) |
| 🔖 **SPRINT 3** | 03/11 - 28/11 | [Sprint 3 Docs](./documentacao/produto/backlog%20sprints/sprint3.md) |  |
| ⚡️ **feira de soluções** | 04/12 |  |  |

## 📅 Board de priorização  <a id="sprint"></a>
[Board no github equipe neurodivertidamente](https://github.com/users/c137santos/projects/10
)


## 💻 Tecnologias <a id="tecnologias"></a>

<h4 align="center">
 <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
 <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white"></a>
 <a href="https://vuejs.org/"><img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D"/></a>
 <a href="https://www.atlassian.com/software/jira"><img src="https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white"/></a>
 <a href="https://github.com/"><img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white"/></a>
 <a href="https://www.figma.com/"><img src="https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white"/></a>
 <a href="https://aws.amazon.com/"><img src="https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white"></a>
 <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white"></a>
 <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"></a>
 <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"></a>
 <a href="https://dbeaver.io/"><img src="https://img.shields.io/badge/DBeaver-372923?style=for-the-badge&logo=dbeaver&logoColor=white"></a>
</h4>

## 📖 Manual de Instalação e testagem <a id="manual"></a>
[manual de instalação](./documentacao/tecnica/manual_de_instalacao.md)

## 🪵 Estrutura de branchs  <a id="branchs"></a>
[Estrutura de branchs](./documentacao/tecnica/estrutura_de_branchs.md)

## 📦 Product Backlog -> DOR e DOD  <a id="pb"></a>
[Product backlog](./documentacao/tecnica/estrutura_de_branchs.md)

## 📖 Manual do usuário  <a id="manual_usuario"></a>
[Manual do usuário](./documentacao/produto/manual_do_usuario.md)

## 📦 Figma Projeto <a id="figma"></a>
[Figma](https://www.figma.com/design/YBuIsfRpONwxIMrR1xqMyv/API-5%C2%BA-SEM?node-id=0-1&t=ZWqGjJXrsCpHYu7s-1 ) - Atualizado o Figma conforme aprovação da equipe com os ajustes solicitados pelo cliente.

## 🎓 Equipe <a id="equipe"></a>

<div align="center">
  <table>
    <tr>
      <th>Membro</th>
      <th>Função</th>
      <th>Github</th>
      <th>Linkedin</th>
    </tr>
    <tr>
      <td>Jean Rodrigues</td>
      <td>Scrum Master</td>
      <td><a href="https://github.com/JeanRodrigues1"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/jean-rodrigues-0569a0251/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Paloma Soares</td>
      <td>Product Owner</td>
      <td><a href="https://github.com/PalomaSoaresR"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/paloma-soares-rocha/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Isaque de Souza</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/Isaque-BD"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/isaque-souza-6760b8270/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Marília Moraes</td>
      <td>Desenvolvedora</td>
      <td><a href="https://github.com/marilia-borgo"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/mariliaborgo/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Maria Clara Santos</td>
      <td>Desenvolvedora</td>
      <td><a href="https://github.com/c137santos"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/c137santos/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Ricardo Campos</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/r1cardvs"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/ricardo-campos-ba56091b5/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Vinícius Monteiro</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/viniciusvasmonteiro"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/viniciusvasm/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Yan Yamim</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/YanYamim"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/yan-yamim-185220278/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
  </table>
</div>
