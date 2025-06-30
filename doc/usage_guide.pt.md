# Guia de Uso do Editor de Banco de Dados JSON

Este guia fornece instruções detalhadas sobre como utilizar o Editor de Banco de Dados JSON, um sistema que permite gerenciar arquivos JSON estruturados com validação de esquema.

## Sumário

1. [Introdução](#introdução)
2. [Conceitos Básicos](#conceitos-básicos)
3. [Primeiros Passos](#primeiros-passos)
4. [Interface de Usuário](#interface-de-usuário)
5. [Operações com Arquivos](#operações-com-arquivos)
6. [Edição de Dados](#edição-de-dados)
7. [Busca e Navegação](#busca-e-navegação)
8. [Configurações](#configurações)
9. [Recursos Avançados](#recursos-avançados)
10. [Solução de Problemas](#solução-de-problemas)

## Introdução

O Editor de Banco de Dados JSON é uma aplicação gráfica que permite editar, validar e gerenciar arquivos JSON com base em um esquema predefinido. O sistema trabalha com dois tipos de arquivos:

1. **Arquivo de Modelo**: Contém a definição do esquema na seção `__meta__`, que especifica os campos, tipos de dados e requisitos.
2. **Arquivo de Dados**: Contém os dados propriamente ditos, que devem seguir a estrutura definida no modelo.

## Conceitos Básicos

### Modelo de Dados (`__meta__`)

O modelo define a estrutura esperada dos dados através de um objeto `__meta__` com o seguinte formato:

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

### Tipos de Dados Suportados

- `str`: Strings (textos)
- `int`: Números inteiros
- `float`: Números de ponto flutuante (decimais)
- `bool`: Valores booleanos (verdadeiro/falso)
- `list`: Listas genéricas
- `list[tipo]`: Listas tipadas (ex: `list[str]` para lista de strings)
- `dict` ou `object`: Dicionários aninhados. Se o modelo especificar os campos do dicionário, a interface de edição exibirá campos estruturados. Caso contrário, será usada uma interface genérica de pares chave-valor.

### Arquivo de Dados

Os dados são armazenados como uma lista de objetos JSON que seguem a estrutura definida no modelo:

```json
[
  {
    "nome": "João Silva",
    "email": "joao@exemplo.com",
    "idade": 30,
    "ativo": true
  },
  {
    "nome": "Maria Oliveira",
    "email": "maria@exemplo.com",
    "idade": 25,
    "ativo": false
  }
]
```

## Primeiros Passos

### Iniciar a Aplicação

1. Execute o arquivo `main.py`:
   ```
   python main.py
   ```

2. A aplicação irá carregar e exibir a janela principal.

### Carregar um Modelo

1. Clique no botão "Carregar Modelo" na barra de ferramentas ou use o menu Arquivo > Carregar Modelo (ou pressione Ctrl+O).
2. Selecione o arquivo JSON contendo a definição `__meta__`.
3. O sistema irá analisar o modelo e configurar a interface apropriadamente.

### Carregar Dados

1. Clique no botão "Carregar Dados" na barra de ferramentas ou use o menu Arquivo > Carregar Dados (ou pressione Ctrl+D).
2. Selecione o arquivo JSON contendo os dados.
3. Os dados serão carregados e validados contra o modelo atual.

## Interface de Usuário

### Componentes Principais

- **Barra de Ferramentas**: Contém botões para as operações mais comuns.
- **Painel de Pesquisa**: Permite buscar informações nos dados.
- **Visualização em Tabela**: Exibe os dados em formato tabular.
- **Barra de Status**: Mostra informações sobre os arquivos carregados.

### Atalhos de Teclado

- `Ctrl+O`: Carregar arquivo de modelo
- `Ctrl+D`: Carregar arquivo de dados
- `Ctrl+S`: Salvar dados
- `Ctrl+N`: Adicionar nova entrada
- `Delete`: Excluir entrada selecionada
- `Ctrl+Z`: Desfazer
- `Ctrl+Y`: Refazer
- `Ctrl+F`: Focar no campo de pesquisa
- `F3`: Próximo resultado de pesquisa
- `Shift+F3`: Resultado anterior de pesquisa

## Operações com Arquivos

### Carregar um Modelo Existente

1. Use o botão "Carregar Modelo" ou o menu Arquivo > Carregar Modelo.
2. Navegue até o arquivo JSON de modelo desejado.
3. Selecione o arquivo e clique em "Abrir".

### Carregar Dados Existentes

1. Use o botão "Carregar Dados" ou o menu Arquivo > Carregar Dados.
2. Navegue até o arquivo JSON de dados desejado.
3. Selecione o arquivo e clique em "Abrir".

### Salvar Dados

1. Use o botão "Salvar Dados" ou o menu Arquivo > Salvar (ou pressione Ctrl+S).
2. Se o arquivo não tiver sido salvo anteriormente, será solicitado um local para salvá-lo.
3. Os dados serão validados e salvos no formato JSON.

### Salvar Dados como Novo Arquivo

1. Use o menu Arquivo > Salvar Como.
2. Navegue até o local desejado e forneça um nome para o arquivo.
3. Clique em "Salvar".

### Exportar para CSV

1. Use o menu Ferramentas > Exportar para CSV.
2. Selecione o local e nome do arquivo CSV.
3. Os dados serão convertidos e salvos no formato CSV.

### Importar de CSV

1. Use o menu Ferramentas > Importar de CSV.
2. Selecione o arquivo CSV a ser importado.
3. Os dados serão convertidos para JSON e validados contra o modelo atual.

## Edição de Dados

### Adicionar Nova Entrada

1. Clique no botão "Adicionar" ou use o menu Editar > Adicionar Entrada (ou pressione Ctrl+N).
2. Uma nova entrada será criada com valores padrão para campos obrigatórios.
3. Um diálogo de edição será aberto para cada campo, permitindo que você preencha os valores.

### Editar Entrada Existente

1. Selecione a entrada que deseja editar na tabela.
2. Clique no botão "Editar", use o menu Editar > Editar Selecionada, ou dê um duplo clique na entrada.
3. Um diálogo de edição será aberto para cada campo, permitindo que você altere os valores.

### Excluir Entrada

1. Selecione a entrada que deseja excluir na tabela.
2. Clique no botão "Excluir", use o menu Editar > Excluir Selecionada, ou pressione a tecla Delete.
3. Confirme a exclusão quando solicitado.

### Desfazer/Refazer

- Para desfazer a última operação, use o botão "Desfazer", o menu Editar > Desfazer, ou pressione Ctrl+Z.
- Para refazer uma operação desfeita, use o botão "Refazer", o menu Editar > Refazer, ou pressione Ctrl+Y.

## Busca e Navegação

### Pesquisar nos Dados

1. Digite o termo de busca no campo de pesquisa na parte superior da janela.
2. Pressione Enter ou clique no botão "Buscar".
3. O primeiro resultado será selecionado automaticamente.

### Navegar entre Resultados

- Para ir para o próximo resultado, clique no botão "Próximo" ou pressione F3.
- Para ir para o resultado anterior, clique no botão "Anterior" ou pressione Shift+F3.

## Configurações

### Acessar Preferências

1. Use o menu Configurações > Preferências.
2. Um diálogo de configurações será aberto com várias abas para diferentes categorias.

### Alternar Tema

1. Clique no botão "Tema Escuro/Claro" na barra de ferramentas ou use o menu Visualizar > Alternar Tema.
2. A interface será atualizada com o novo tema.

### Personalizar Comportamento

O diálogo de configurações permite personalizar vários aspectos do sistema:

- **Interface**: Tamanho da janela, fonte, comportamento de arrastar e soltar, etc.
- **Arquivos**: Criação de backups, salvamento automático, codificação, etc.
- **Validação**: Quando validar, verificação estrita de tipos, etc.
- **Exportação**: Formatos de exportação, delimitadores CSV, etc.
- **Diretórios**: Locais personalizados para arquivos de diferentes tipos.

## Recursos Avançados

### Validação de Dados

O sistema valida automaticamente os dados contra o modelo em vários momentos:

- Ao carregar um arquivo de dados
- Ao editar uma entrada
- Antes de salvar (pode ser desativado nas configurações)

Entradas inválidas são destacadas na visualização da tabela.

### Arrastar e Soltar

Você pode arrastar arquivos JSON diretamente para a janela do aplicativo:

- Se o arquivo contiver um objeto `__meta__`, será tratado como um modelo.
- Caso contrário, será tratado como um arquivo de dados.

### Salvamento Automático

O sistema pode salvar automaticamente os dados em intervalos regulares, se configurado:

1. Acesse Configurações > Preferências > Arquivos.
2. Defina o intervalo de salvamento automático em segundos (0 para desativar).

## Solução de Problemas

### Erros de Validação

Se os dados não corresponderem ao modelo, você verá mensagens de erro detalhando os problemas:

- Campos obrigatórios ausentes
- Tipos de dados incorretos
- Campos não definidos no modelo

### Arquivos Grandes

Para arquivos muito grandes, o sistema usa processamento otimizado:

- Carregamento em chunks
- Validação em partes
- Salvamento otimizado

O limite para considerar um arquivo "grande" pode ser ajustado nas configurações.

### Compatibilidade

- O sistema foi projetado para funcionar em Windows, Linux e macOS.
- Algumas funcionalidades (como arrastar e soltar) podem depender do sistema operacional.
- A funcionalidade completa de arrastar e soltar no Windows requer o módulo pywin32.

### Problemas Comuns

1. **Erro ao carregar modelo**: Verifique se o arquivo contém um objeto JSON válido com uma seção `__meta__`.
2. **Erro ao carregar dados**: Verifique se o arquivo contém JSON válido.
3. **Erro de validação**: Certifique-se de que os dados seguem o formato definido no modelo.
4. **Interface não responsiva**: Para arquivos muito grandes, algumas operações podem levar mais tempo.

Para mais informações, consulte a documentação completa ou entre em contato com o suporte.