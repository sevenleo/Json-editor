# JSON Database Editor

Um sistema de gerenciamento de arquivos JSON com interface gráfica, desenvolvido em Python com Tkinter. Permite editar, validar e manter arquivos JSON estruturados de acordo com um esquema definido.

## Descrição

Este sistema foi projetado para funcionar como um editor visual de banco de dados JSON, permitindo:

- Validar dados JSON contra um esquema definido em um arquivo modelo
- Visualizar e editar dados de forma amigável com widgets apropriados para cada tipo de dado
- Adicionar e remover registros seguindo o esquema definido
- Buscar informações, navegar e manipular registros facilmente
- Exportar e salvar os dados editados

## Requisitos

- Python 3.6 ou superior
- Tkinter (incluído na maioria das instalações padrão do Python)
- Para suporte completo de arrastar e soltar no Windows, o módulo pywin32 é recomendado:
  ```
  pip install pywin32
  ```

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Certifique-se de que Python 3.6+ está instalado
3. (Opcional) Instale pywin32 para suporte completo de arrastar e soltar no Windows

## Como Usar

Execute o arquivo principal:

```
python main.py
```

### Fluxo básico de uso:

1. Carregue um arquivo de modelo JSON (contendo a definição `__meta__`)
2. Carregue um arquivo de dados JSON ou crie um novo conjunto de dados
3. Edite, adicione ou remova registros conforme necessário
4. Salve as alterações no arquivo original ou em um novo arquivo

## Estrutura do Arquivo Modelo

O arquivo de modelo deve conter um objeto JSON com uma propriedade `__meta__` que define a estrutura esperada dos dados:

```json
{
  "__meta__": {
    "nome_do_campo": {
      "type": "tipo_de_dado",
      "required": true_ou_false
    },
    ...
  }
}
```

### Tipos de dados suportados:

- `str` - Strings
- `int` - Números inteiros
- `float` - Números de ponto flutuante
- `bool` - Valores booleanos (verdadeiro/falso)
- `list` - Listas genéricas
- `list[tipo]` - Listas tipadas (ex: `list[str]`). Isso também se aplica a `list[dict]`, permitindo a criação de listas de objetos com uma estrutura definida.
- `dict` ou `object` - Dicionários aninhados. Se o modelo especificar os campos do dicionário, a interface de edição exibirá campos estruturados. Caso contrário, será usada uma interface genérica de pares chave-valor.

### Exemplo:

```json
{
  "__meta__": {
    "name": { "type": "str", "required": true },
    "email": { "type": "str", "required": false },
    "age": { "type": "int", "required": false },
    "active": { "type": "bool", "required": true },
    "tags": { "type": "list[str]", "required": false },
    "address": {
      "type": "dict",
      "required": false,
      "fields": {
        "street": { "type": "str", "required": true },
        "city": { "type": "str", "required": true },
        "zipcode": { "type": "str", "required": false }
      }
    }
  }
}
```

## Funcionalidades

### Principais recursos:

- **Validação em tempo real**: Identifica campos obrigatórios ausentes e tipos de dados incorretos
- **Interface tipo planilha**: Visualização em grade com edição de célula individualizada
- **Edição apropriada por tipo**: Inputs de texto, checkboxes, campos numéricos, etc.
- **Pesquisa**: Busca por conteúdo em qualquer campo
- **Histórico de ações**: Suporte a operações de desfazer/refazer
- **Tema claro/escuro**: Alterna entre temas para melhor conforto visual
- **Arrastar e soltar**: Suporte para carregamento de arquivos via drag & drop
- **Exportação**: Salva dados no formato JSON

### Atalhos de teclado:

- `Ctrl+O` - Carregar arquivo de modelo
- `Ctrl+D` - Carregar arquivo de dados
- `Ctrl+S` - Salvar dados
- `Ctrl+N` - Adicionar nova entrada
- `Delete` - Excluir entrada selecionada
- `Ctrl+Z` - Desfazer
- `Ctrl+Y` - Refazer
- `Ctrl+F` - Focar no campo de pesquisa
- `F3` - Próximo resultado de pesquisa
- `Shift+F3` - Resultado anterior de pesquisa

## Exemplos

O sistema vem com arquivos de exemplo na pasta `examples/`:

- `example_model.json` - Um modelo de exemplo com vários tipos de campos
- `example_data.json` - Dados de exemplo compatíveis com o modelo.
- `complex_model.json` - Um modelo mais complexo, demonstrando dicionários e listas com estruturas aninhadas.
- `complex_data.json` - Dados correspondentes para o modelo complexo.

## Limitações Atuais

- Suporte limitado para estruturas profundamente aninhadas
- Não há suporte para validação de esquema via JSON Schema ou similar
- Sem suporte nativo para referências entre objetos

## Licença

Este projeto é distribuído sob a licença MIT.