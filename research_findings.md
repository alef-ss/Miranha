# Descobertas de Pesquisa - Bot Discord Financeiro

## APIs de Taxas de Juros (Brasil)
- **python-bcb**: Interface para o Sistema Gerenciador de Séries Temporais (SGS) do Banco Central do Brasil. Permite obter taxas de juros, Selic, inflação, etc.
- **Séries Temporais (SGS) relevantes**:
  - Taxas de juros de operações de crédito por instituição financeira (ex: cheque especial, cartão de crédito, crédito pessoal).
  - Taxa Selic (Série 11).

## Bibliotecas Python
- **discord.py**: Biblioteca principal para o bot.
- **sqlite3**: Banco de dados leve e nativo do Python para armazenar transações, dívidas e metas.
- **pandas**: Útil para processar dados das taxas de juros e gerar relatórios.
- **matplotlib/seaborn**: Para gerar gráficos nos relatórios (opcional, mas recomendado para visualização).

## Estrutura de Comandos Planejada
- `!entrada <valor> <descrição>`: Registra ganho.
- `!saida <valor> <descrição>`: Registra gasto.
- `!salario <valor>`: Registra renda mensal fixa.
- `!divida <valor> <banco> <tipo>`: Registra nova dívida.
- `!pagar_divida <id> <valor>`: Registra pagamento parcial/total.
- `!objetivo <valor> <descrição> <prioridade>`: Registra meta de economia.
- `!relatorio [data/mes]`: Gera resumo financeiro.
- `!plano`: Gera o plano de ação inteligente (priorização de dívidas vs objetivos).
