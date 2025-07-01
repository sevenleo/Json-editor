# Contexto do Projeto: Json-database

Este documento descreve o projeto Json-database, suas funcionalidades principais, as tecnologias que o fundamentam e o histórico de alterações.

## Sobre o Projeto

O Json-database é um editor visual de arquivos JSON, desenvolvido em Python com Tkinter, que funciona como uma "planilha de JSON". Ele se destaca pela validação rigorosa de dados, utilizando um esquema (`__meta__`) que define a estrutura, tipos e obrigatoriedade dos campos. A aplicação garante a integridade dos dados através de validação contra este modelo, oferecendo uma interface gráfica intuitiva para manipulação (CRUD) segura e estruturada.

### Funcionalidades Principais:
*   Edição de valores com widgets apropriados para cada tipo de dado.
*   Adição e exclusão de novos registros em conformidade com o modelo.
*   Visualização hierárquica (em árvore) para estruturas aninhadas.
*   Funcionalidade de busca por chaves ou valores.
*   Validação de dados em tempo real com feedback visual.
*   Geração de novos arquivos JSON baseados apenas no modelo.

## Bases de Desenvolvimento

As principais bases de desenvolvimento deste projeto são:

*   **Linguagem de Programação**: Python
*   **Biblioteca Gráfica**: Tkinter (usando `ttk.Treeview` para a visualização em tabela).
*   **Formato de Dados**: JSON
*   **Arquitetura**: Separação clara entre o modelo de dados (`__meta__`) e os dados em si, com código modularizado.
*   **Testes**: Testes unitários para garantir a robustez do modelo de dados.
*   **Filosofia**: Foco em edição segura, estruturada e visualmente intuitiva de dados JSON.

## Alterações e Ideias Implementadas

Esta seção resume as principais ideias e correções que foram implementadas ao longo do desenvolvimento do projeto.

### Ideias Iniciais e Melhorias:
*   **Separação de Modelo e Dados**: Reutilização de modelos para diferentes conjuntos de dados.
*   **Interface de Planilha**: Uso do `ttk.Treeview` para uma edição de dados intuitiva.
*   **Validação em Tempo Real**: Feedback instantâneo para o usuário sobre a validade dos dados inseridos.
*   **Suporte a Tipos Compostos**: Manipulação de listas e objetos aninhados.
*   **Geração de JSON em Branco**: Criação de novos arquivos JSON a partir de um modelo.
*   **Foco em Usabilidade**: Suporte a drag-and-drop e interface amigável.

### Correções Recentes (FIXES):
*   **Edição de Campo Específico**: Melhoria na interface para permitir a edição direta de um campo sem a necessidade de percorrer todos os outros campos de um registro. A interface agora também exibe o tipo de dado esperado e se o campo é obrigatório.
*   **Janela de Novo Elemento**: Ao adicionar um novo registro, uma janela dedicada é aberta com campos de entrada para cada coluna, indicando os tipos de dados e a obrigatoriedade.
*   **Remoção do Tema Escuro**: A opção de tema escuro foi removida.