# Documentação de Testes Backend

## Visão Geral

Este projeto utiliza **pytest** como framework principal para testes automatizados do backend Django. Os testes garantem que as APIs, autenticação, permissões e integrações funcionem conforme esperado, facilitando a manutenção e evolução do sistema.

## Bibliotecas Utilizadas

- **pytest**: Framework de testes que simplifica a escrita e execução dos testes.
- **pytest-django**: Integração do pytest com Django, permitindo uso de fixtures específicas do Django (como `db`).
- **unittest.mock**: Utilizado para criar mocks e validar chamadas, como o uso de `ANY` para valores dinâmicos.
- **Django Test Client**: Simula requisições HTTP para testar endpoints da API.

## Estrutura dos Testes

- Os testes ficam em arquivos dentro dos diretórios `tests/` de cada app.
- Fixtures são definidas em arquivos `conftest.py` para reaproveitamento de dados e configuração de ambiente.
- Cada teste deve ser independente e garantir o estado limpo do banco de dados usando a fixture `db`.

## Práticas Esperadas

1. **Cobertura de Casos Relevantes**: Testar cenários de sucesso e falha, incluindo autenticação, permissões e respostas da API.
2. **Uso de Fixtures**: Criar dados de teste reutilizáveis em `conftest.py` para evitar duplicação.
3. **Isolamento**: Cada teste deve ser independente, sem depender do resultado de outros testes.
4. **Assertivas Claras**: Validar status HTTP, estrutura e conteúdo das respostas JSON.
5. **Mocks para Dados Dinâmicos**: Utilizar `ANY` do `unittest.mock` para campos que mudam dinamicamente (ex: IDs, hashes). Utilizar com cautela, nem tudo pode ser ANY!
6. **Marcação de Testes com Banco**: Usar `@pytest.mark.django_db` quando o teste interage com o banco de dados.
7. **Nomenclatura Descritiva**: Nomear funções de teste de forma clara, indicando o comportamento esperado.

## Exemplos

### Teste de Status da API

```python
def test_obter_status(client, db):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    assert resp.json() == {
        "status": "ok",
        "db": "ok",
        "git_hash": ANY,
    }
```

### Tipos de Testes Essenciais que devem ser implementados a cada features do backend

Teste de Unidade (Unit Testing): Foca em testar a menor parte testável do código, como uma função ou método. Garante que cada "unidade" funcione isoladamente, conforme o esperado.

Teste de Integração (Integration Testing): Verifica se diferentes módulos ou componentes do sistema funcionam bem juntos. É fundamental para garantir que as interações entre a nova feature e as partes existentes não causem falhas.

Teste de Aceitação do Usuário (UAT - User Acceptance Testing): É a etapa final, onde o cliente ou o usuário final valida se a nova feature atende aos requisitos e expectativas de negócio, garantindo que o produto é funcional e relevante. | Geralmente ocorre nos CRs |

#### Cenários de Teste que Você Deve Considerar

Ao testar uma nova funcionalidade, você deve ir além do "caminho feliz" (o cenário ideal) e considerar uma variedade de situações para cobrir todas as possibilidades.

1. Cenários de Sucesso (Caminho Feliz):

* Valores Válidos/Certos: Teste com dados esperados e corretos, garantindo que a funcionalidade se comporta exatamente como planejado. Exemplo: Se um campo aceita números de 1 a 100, teste com valores como 50.

2. Cenários de Insucesso (Caminho Alternativo):

* Valores Inválidos: Teste a nova feature com dados que não deveriam ser aceitos. Isso valida o tratamento de erros do sistema. Exemplo: Em um campo que aceita apenas números, tente inserir letras ou caracteres especiais.

* Casos de Borda (Boundary Values): Teste os valores extremos. Isso é crucial, pois muitos bugs acontecem nos limites do que é permitido. Exemplo: Para um campo que aceita de 1 a 100, teste com os valores 0, 1, 100 e 101.

* Casos Negativos: Simule situações em que uma ação deveria falhar ou ser rejeitada. Exemplo: Um usuário tenta acessar uma funcionalidade sem ter a permissão necessária.


#### Coverage

O uso do **coverage** é fundamental para garantir que os testes realmente exercitam o código relevante do backend. Recomenda-se:

- Execute os testes sempre utilizando o comando `coverage run -m pytest` para medir a cobertura de código.
- Após a execução, utilize `coverage report` para visualizar no terminal quais arquivos e linhas foram cobertos pelos testes.
- Gere relatórios HTML com `coverage html` para uma visualização detalhada e interativa das áreas cobertas e não cobertas.
- Para gerar o `coverage xml` para aferir a percentagem de cobertura do código rodando comando no terminal `coverage run -m pytest && coverage xml && coverage report --fail-under=80`
- Busque manter uma cobertura alta, especialmente nos módulos críticos, mas priorize qualidade dos testes sobre quantidade.
- É exigido pelo menos mais de 80% de cobertura de testes
- Analise linhas não cobertas e avalie se são casos relevantes a serem testados ou código morto/passível de remoção.
- Inclua a análise de cobertura no pipeline de CI/CD para garantir que novas features mantenham ou aumentem a cobertura existente.
