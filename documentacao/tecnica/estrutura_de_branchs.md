# Estrutura de branchs

## 📋 Visão Geral
Este documento descreve a estratégia de branches utilizando Git Flow adaptado para integração com GitHub Projects.

## 🌿 Estrutura de Branches

### main:
Essa branch sempre refletirá o estado pronto para produção do código. Todos os commits dessa branch devem ser estáveis.

### dev:
Essa branch serve como uma branch de integração de todas novas features. Ela contém o histórico completo do projeto, assim como features que não foram lançadas ainda. 

### feature branches:
Essas branchs são criadas a partir da branch dev para o desenvolvimento de novas funcionalidades. Uma vez que a feature é completa, testada e aceita, ela é mergeada novamente na branch dev. 

> nomenclatura de feature branchs

Para a criação de novas branchs seguiremos o padrão criado pelo github projects que consiste em:

[id-issue]-[título-da-issue]
