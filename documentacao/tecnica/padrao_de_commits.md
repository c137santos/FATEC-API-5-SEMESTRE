### Padrão de Commits

Para garantir um histórico de commits limpo, legível e padronizado, utilizamos uma convenção baseada no **Conventional Commits**, com uma adaptação para incluir o ID da *issue* a que o commit se refere.

---

#### Estrutura do Commit

A estrutura de cada commit deve seguir o seguinte padrão:

tipo (id_da_issue) : descrição

#### Partes da Mensagem de Commit

* **`<tipo>`**: Obrigatório, indica a natureza da alteração. Use uma das seguintes opções:
    * **`feat`**: Nova funcionalidade.
    * **`fix`**: Correção de bug.
    * **`docs`**: Mudanças na documentação.
    * **`style`**: Mudanças de formatação, sem alteração na lógica.
    * **`refactor`**: Refatoração de código sem adicionar funcionalidade ou corrigir bug.
    * **`test`**: Adição ou correção de testes.
    * **`chore`**: Mudanças de build, scripts ou ferramentas auxiliares.
    * **`ci`**: Mudanças nos arquivos de CI.
    * **`perf`**: Mudança que melhora a performance.
    * **`build`**: Mudanças no sistema de build ou dependências.
    * **`revert`**: Reverte um commit anterior.

* **`<id_da_issue>`**: O ID da *issue* ao qual o commit se refere, colocado entre parênteses `()`.

* **`<descrição>`**: Uma breve explicação da alteração, escrita de forma concisa e em caixa baixa (exceto nomes próprios), sendo eles escritos em inglês.

---

### Exemplos

* **Nova funcionalidade:**
    ```
    feat(#3): Add form to create a new user
    ```

* **Correção de bug:**
    ```
    fix(#5):Fix bug of alignment in the button of home
    ```

* **Refatoração:**
    ```
    refactor(#12): Otimize the query that search products
    ```

---

### Boas Práticas Adicionais

* Mantenha a descrição curta (máximo 50 caracteres) para facilitar a leitura.
* Se precisar de mais detalhes, adicione um corpo ao commit (uma linha em branco após a descrição).
* Use quebras de linha no corpo do commit com cerca de 72 caracteres.








