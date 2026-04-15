# Arquitetura do Bot Discord Financeiro

## 1. Visão Geral
O bot será desenvolvido em Python utilizando a biblioteca `discord.py` para interação com o Discord. Para persistência de dados, será empregado o `SQLite` devido à sua leveza e facilidade de uso, ideal para um projeto de médio porte. A integração com dados externos, como taxas de juros, será realizada através da biblioteca `python-bcb`, que fornece acesso à API de Dados Abertos do Banco Central do Brasil.

## 2. Componentes Principais

### 2.1. Módulo Discord (`discord.py`)
- **Eventos**: Gerenciamento de eventos do Discord (ex: `on_ready`, `on_message`).
- **Comandos**: Implementação dos comandos do bot, utilizando o sistema de comandos do `discord.py`.
- **Interação**: Envio de mensagens, embeds e reações para comunicação com os usuários.

### 2.2. Módulo de Banco de Dados (`SQLite`)
- **Estrutura**: Um banco de dados `SQLite` será utilizado para armazenar as informações financeiras dos usuários.
- **Tabelas Propostas**:
    - `usuarios`: ID do usuário Discord, salário, objetivos.
    - `transacoes`: ID da transação, ID do usuário, tipo (entrada/saída), valor, descrição, data.
    - `dividas`: ID da dívida, ID do usuário, banco, tipo (cartão, pessoal, etc.), valor original, valor restante, data de registro, juros (referência).
    - `objetivos`: ID do objetivo, ID do usuário, descrição, valor total, valor economizado, prioridade, data de criação.

### 2.3. Módulo de Integração com BCB (`python-bcb`)
- **Consulta de Juros**: Obtenção de taxas de juros de diferentes tipos de crédito e instituições financeiras diretamente do Banco Central.
- **Atualização de Dados**: Mecanismo para atualizar periodicamente as taxas de juros para garantir a precisão dos cálculos.

### 2.4. Módulo de Lógica Financeira
- **Cálculo de Juros**: Lógica para calcular o impacto dos juros nas dívidas e projetar cenários.
- **Priorização Inteligente**: Algoritmo para analisar dívidas e objetivos, sugerindo a melhor estratégia com base nas taxas de juros e prioridades definidas pelo usuário.
- **Geração de Relatórios**: Processamento dos dados armazenados para criar relatórios financeiros detalhados.

## 3. Definição de Comandos

### 3.1. Comandos de Transações
- `!entrada <valor> <descrição>`
    - **Descrição**: Registra uma entrada de dinheiro.
    - **Exemplo**: `!entrada 1500 Salário do mês`
- `!saida <valor> <descrição>`
    - **Descrição**: Registra uma saída de dinheiro (gasto).
    - **Exemplo**: `!saida 50 Supermercado`
- `!salario <valor>`
    - **Descrição**: Define ou atualiza o salário mensal do usuário.
    - **Exemplo**: `!salario 3000`

### 3.2. Comandos de Dívidas
- `!divida <valor> <banco> <tipo>`
    - **Descrição**: Registra uma nova dívida. O bot solicitará o tipo de dívida (ex: `cartao`, `pessoal`, `cheque_especial`) e o banco para buscar as taxas de juros relevantes.
    - **Exemplo**: `!divida 10000 Itau cartao`
- `!pagar_divida <id_divida> <valor_pago>`
    - **Descrição**: Registra um pagamento parcial ou total de uma dívida existente.
    - **Exemplo**: `!pagar_divida 1 200`

### 3.3. Comandos de Objetivos
- `!objetivo <valor_total> <descrição> <prioridade>`
    - **Descrição**: Registra um novo objetivo financeiro. A prioridade pode ser `alta`, `media` ou `baixa`.
    - **Exemplo**: `!objetivo 5000 Viagem_para_praia media`

### 3.4. Comandos de Relatórios e Planejamento
- `!relatorio [periodo]`
    - **Descrição**: Gera um relatório financeiro. O `periodo` pode ser `hoje`, `semana`, `mes`, `ano` ou uma data específica (ex: `2026-03`). Se omitido, será o mês atual.
    - **Exemplo**: `!relatorio mes` ou `!relatorio 2026-03`
- `!plano`
    - **Descrição**: Gera um plano financeiro inteligente, priorizando o pagamento de dívidas com juros mais altos ou a economia para objetivos, com base nas informações do usuário.
    - **Exemplo**: `!plano`

## 4. Fluxo de Interação (Exemplo)
1. Usuário digita `!divida 5000 Bradesco pessoal`.
2. Bot confirma o registro da dívida e informa a taxa de juros estimada para o tipo de dívida e banco.
3. Usuário digita `!plano`.
4. Bot analisa as dívidas e objetivos, e sugere uma estratégia, por exemplo: "Foque em pagar a dívida do Bradesco, pois possui juros de X% ao mês. Após isso, direcione Y% do seu salário para o objetivo 'Viagem para praia'."
