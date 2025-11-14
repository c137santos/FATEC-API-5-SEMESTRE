# Documentação de Banco de Dados

## 1. Visão Geral do Banco de Dados
Este documento fornece uma visão geral do banco de dados utilizado no sistema, incluindo sua estrutura, tabelas principais, relacionamentos.

## Vantagens Técnicas do Flyway

### 1.Tabela de histórico confiável
Registra:
- versão
- checksum
- autor
- data
- status

📌 Impacto técnico: auditoria completa; detecção de alterações ilegais em scripts.

### 2. Multi-banco e independente da linguagem

Suporta PostgreSQL.
Suporte com a linguagem Django.

### 3. Ideal para CI/CD
Ele consegue integrar com o Github Actions, que é algo que é utilizado no projeto.

📌 Impacto técnico: automatiza migrações, elimina erros humanos e garante deploy previsível.

### 4. Fácil integração com Docker.
Flyway pode ser facilmente integrado em contêineres Docker, permitindo que as migrações de banco de dados sejam executadas automaticamente durante o processo de construção e implantação do contêiner.

📌 Impacto técnico: simplifica o gerenciamento de banco de dados em ambientes conteinerizados, garantindo consistência entre desenvolvimento, teste e produção.
