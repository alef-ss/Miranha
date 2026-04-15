# Manual de Uso - Bot Financeiro Discord

Bem-vindo ao seu novo assistente financeiro pessoal no Discord! Este bot foi desenvolvido para ajudar você a controlar suas entradas, saídas, gerenciar dívidas com inteligência (baseado em taxas de juros reais do Banco Central) e alcançar seus objetivos financeiros.

## 1. Configuração Inicial

Antes de executar o bot, você precisa configurá-lo com o seu token do Discord e instalar as dependências necessárias.

### 1.1. Requisitos
Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina. As bibliotecas necessárias estão listadas no arquivo `requirements.txt`. Para instalá-las, execute o seguinte comando no terminal:

```bash
pip install -r requirements.txt
```

### 1.2. Configurando o Token
Abra o arquivo `main.py` e localize a linha 9:
```python
TOKEN = 'SEU_TOKEN_AQUI'
```
Substitua `'SEU_TOKEN_AQUI'` pelo token real do seu bot, que pode ser obtido no [Discord Developer Portal](https://discord.com/developers/applications).

### 1.3. Executando o Bot
Após configurar o token e instalar as dependências, inicie o bot com o comando:
```bash
python main.py
```
O bot criará automaticamente o banco de dados `finance_bot.db` na primeira execução.

---

## 2. Guia de Comandos

O bot utiliza o prefixo `!` para todos os comandos. Abaixo está a lista completa de funcionalidades.

### 2.1. Gestão de Fluxo de Caixa

Estes comandos ajudam a registrar o dinheiro que entra e sai da sua conta no dia a dia.

| Comando | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `!salario <valor>` | Define ou atualiza a sua renda mensal fixa. Isso é crucial para que o bot possa gerar planos financeiros precisos. | `!salario 3500.50` |
| `!entrada <valor> <descrição>` | Registra um ganho ou receita extra. | `!entrada 200 Venda de bolo` |
| `!saida <valor> <descrição>` | Registra um gasto ou despesa. | `!saida 50.00 Supermercado` |

### 2.2. Gestão de Dívidas Inteligente

O bot se conecta à API do Banco Central do Brasil para estimar a taxa de juros da sua dívida com base no tipo de crédito, ajudando a priorizar o que deve ser pago primeiro.

| Comando | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `!divida <valor> <banco> <tipo>` | Registra uma nova dívida. Os tipos suportados são: `cartao`, `pessoal`, `cheque_especial`, `veiculo`, `imobiliario`. | `!divida 1500 Nubank cartao` |
| `!listar_dividas` | Exibe todas as suas dívidas ativas, mostrando o ID de cada uma, o valor restante e a taxa de juros estimada. | `!listar_dividas` |
| `!pagar_divida <id> <valor>` | Registra o pagamento (parcial ou total) de uma dívida específica usando o ID fornecido pelo comando anterior. | `!pagar_divida 1 300` |

### 2.3. Objetivos Financeiros

Você pode definir metas para economizar dinheiro, como comprar equipamentos para o seu negócio ou fazer uma viagem.

| Comando | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `!objetivo <valor> <prioridade> <descrição>` | Cria uma nova meta. A prioridade deve ser `alta`, `media` ou `baixa`. | `!objetivo 2000 alta Produtos Lava-Rapido` |
| `!listar_objetivos` | Mostra todos os seus objetivos em andamento, com o ID, progresso atual e prioridade. | `!listar_objetivos` |
| `!poupar <id> <valor>` | Adiciona dinheiro a um objetivo específico. O bot também registrará isso como uma "saída" no seu fluxo de caixa geral para manter o saldo correto. | `!poupar 2 150` |

### 2.4. Relatórios e Planejamento

A inteligência do bot brilha nestes comandos, onde ele analisa seus dados para fornecer insights.

| Comando | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `!relatorio [AAAA-MM]` | Gera um resumo financeiro. Se você não informar a data, ele mostrará o relatório do mês atual. Você pode especificar um mês passado para ver o histórico. | `!relatorio` ou `!relatorio 2026-03` |
| `!plano` | O comando mais poderoso. O bot analisa seu salário, suas dívidas (comparando os juros com a taxa Selic atual) e seus objetivos. Ele dirá exatamente se você deve focar em pagar uma dívida com juros abusivos ou se pode começar a investir nos seus objetivos, sugerindo até mesmo como dividir seu salário. | `!plano` |
| `!manual` | Exibe um resumo rápido dos comandos diretamente no Discord, caso você esqueça algum. | `!manual` |

---

## 3. Como o Plano Inteligente Funciona?

Quando você digita `!plano`, o bot realiza as seguintes análises:
1. **Consulta da Selic:** Ele verifica a taxa básica de juros atual.
2. **Análise de Dívidas:** Ele compara a taxa de juros das suas dívidas com a Selic. Se a dívida tiver juros maiores que o rendimento padrão do mercado (como costuma ser o caso de cartão de crédito e cheque especial), ele colocará o pagamento dessa dívida como **Prioridade Máxima**, acima de qualquer objetivo.
3. **Análise de Objetivos:** Se as dívidas estiverem controladas (ou se os juros forem baixos, como em alguns financiamentos imobiliários), ele organizará seus objetivos pela prioridade que você definiu (`alta`, `media`, `baixa`).
4. **Sugestão de Alocação:** Com base no seu salário registrado, ele sugere uma divisão percentual (ex: 30% para dívidas, 20% para objetivos, 50% para gastos livres) para ajudar você a se organizar no mês.

Aproveite o seu novo controle financeiro!
