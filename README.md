# API 5º Semestre Banco de dados

# Necto <-> Jibóia

<p align="center">
      <h2 align="center"> 🐍</h2>
      <h2 align="center"> Jibóia</h2>
</p>

<p align="center">
  | <a href ="#desafio"> Desafio</a>  |
  <a href ="#solucao"> Solução</a>  |   
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

## 📋 Backlog do Produto <a id="backlog"></a>

| Rank | Prioridade | User Story | Estimativa (Story Points) | Sprint |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Alta | Como gestor, ao selecionar um projeto, quero ver uma lista das issues, exibindo o autor, ID da issue e a data de criação. |3 | 1 |
| 2 | Alta | Como gestor, ao visualizar as issues de um projeto, quero ver o tempo total gasto e a data de início de cada uma. |2 | 1 |
| 3 | Alta | Como gestor, quero que o dashboard de issues exiba informações úteis ao contexto de issues do projeto. | 8| 1 |
| 4 | Alta| Como gestor, quero visualizar no dashboard a quantidade de membros ativos e as horas trabalhadas por cada um. |3 | 1 |
| 5 | Alta | Como líder de equipe, quero aplicar filtros por intervalo de datas de criação e por membro no dashboard de issues. | 5| 1 |
| 6 | Média | Como gestor, quero visualizar uma lista dos projetos disponíveis na API do Jira, mostrando para cada um o nome, data de início e fim. | 3| 2 |
| 7 | Média | Como gestor, quero visualizar para cada projeto a quantidade de issues e o total de horas registradas. | 3| 2 |
| 8 | Média | Como gestor, quero um dashboard inicial que mostre a quantidade de issues e horas trabalhadas para um projeto. |8| 2 |
| 9 | Média | Como administrador, quero um formulário para cadastrar novos usuários e definir seu nível de acesso: gerente, líder ou membro de equipe. |5| 3 |
| 10 | Média | Como gestor, quero visualizar no dashboard de projetos a taxa de conclusão de issues e o tempo médio de resolução do projeto. | 3| 3 |
| 11 | Baixa | Como gestor, quero aplicar filtros por projeto e por intervalo de datas (início e fim) no dashboard. | 3| 3 |
| 12 | Baixa | Como gestor, quero que o sistema calcule e exiba o valor total de horas gastas (horas x valor_hora) de um projeto. | 5| 3 |

---

## 📅 Cronograma de Sprints <a id="sprint"></a>

| Sprint          |    Período    | Documentação                                     |
| --------------- | :-----------: | ------------------------------------------------ |
| 🔖 **SPRINT 1** | 08/09 - 28/09 | [Sprint 1 Docs](./documentacao/produto/backlog%20sprints/sprint1.md) |
| 🔖 **SPRINT 2** | 06/10 - 26/10 | [Sprint 2 Docs]() |
| 🔖 **SPRINT 3** | 03/11 - 28/11 | [Sprint 3 Docs]() |
| ⚡️ **feira de soluções** |04/12 | |


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
[Estrutura de branchs](./documentacao/tecnica/estrutura_de_branchs.md)

## 📖 Manual do usuário  <a id="manual_usuario"></a>
[Estrutura de branchs](./documentacao/produto/manual_do_usuario.md)

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
      <td>Marília Moraes</td>
      <td>Product Owner</td>
      <td><a href="https://github.com/marilia-borgo"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/mariliaborgo/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Maria Clara Santos</td>
      <td>Scrum Master</td>
      <td><a href="https://github.com/c137santos"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/c137santos/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Matheus Marciano</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/MarcyLeite"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/matheus-marciano-leite/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Yan Yamin</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/YanYamim"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/yan-yamim-185220278/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
    <tr>
      <td>Jean Rodrigues</td>
      <td>Desenvolvedor</td>
      <td><a href="https://github.com/JeanRodrigues1"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a></td>
      <td><a href="https://www.linkedin.com/in/jean-rodrigues-0569a0251/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a></td>
    </tr>
  </table>
</div>