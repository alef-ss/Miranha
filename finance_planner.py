class FinancePlanner:
    def __init__(self, db_service, bcb_service):
        self.db = db_service
        self.bcb = bcb_service

    def gerar_plano(self, user_id):
        """
        Gera um plano de ação com base em dívidas (taxas de juros) e objetivos (prioridades).
        """
        cursor = self.db.conn.cursor()
        
        # Obter salário
        cursor.execute("SELECT salario FROM usuarios WHERE user_id = ?", (user_id,))
        salario = cursor.fetchone()[0] or 0.0
        
        # Obter dívidas ativas ordenadas por taxa de juros (descendente)
        cursor.execute(
            "SELECT id, banco, tipo, valor_restante, taxa_juros FROM dividas WHERE user_id = ? AND valor_restante > 0 ORDER BY taxa_juros DESC",
            (user_id,)
        )
        dividas = cursor.fetchall()
        
        # Obter objetivos ativos ordenados por prioridade (alta > media > baixa)
        cursor.execute(
            "SELECT id, descricao, valor_total, valor_poupado, prioridade FROM objetivos WHERE user_id = ? AND valor_poupado < valor_total ORDER BY CASE prioridade WHEN 'alta' THEN 1 WHEN 'media' THEN 2 WHEN 'baixa' THEN 3 END",
            (user_id,)
        )
        objetivos = cursor.fetchall()
        
        # Cálculo de recomendações
        recomendacoes = []
        if salario == 0:
            recomendacoes.append("⚠️ **Atenção:** Você ainda não registrou seu salário. Use `!salario <valor>` para um plano mais preciso.")
        
        if not dividas and not objetivos:
            recomendacoes.append("✅ Você não possui dívidas ou objetivos registrados. Comece registrando-os!")
            return recomendacoes

        # Lógica de priorização: Dívidas com juros altos primeiro (especialmente cartão e cheque especial)
        # Comparar juros da dívida com rendimento esperado (Selic)
        selic = self.bcb.get_taxa_selic()
        
        if dividas:
            recomendacoes.append("### 🔴 Prioridade: Pagamento de Dívidas")
            for d_id, banco, tipo, valor, taxa in dividas:
                if taxa > selic:
                    recomendacoes.append(f"- **{banco} ({tipo})**: Taxa de {taxa:.2f}% a.a. é superior ao rendimento da Selic ({selic:.2f}%). **Pague esta dívida o quanto antes.**")
                else:
                    recomendacoes.append(f"- **{banco} ({tipo})**: Taxa de {taxa:.2f}% a.a. é relativamente baixa. Considere equilibrar com investimentos.")

        if objetivos:
            recomendacoes.append("### 🔵 Próximos Passos: Objetivos Financeiros")
            for o_id, desc, total, poupado, prioridade in objetivos:
                falta = total - poupado
                recomendacoes.append(f"- **{desc}**: Falta R$ {falta:.2f}. Prioridade: {prioridade.capitalize()}.")

        # Sugestão de alocação de salário (exemplo simples: 50/30/20)
        if salario > 0:
            pago_divida = salario * 0.3
            pago_objetivo = salario * 0.2
            recomendacoes.append(f"\n💡 **Sugestão de Alocação de Salário (R$ {salario:.2f}):**")
            recomendacoes.append(f"- Destine **R$ {pago_divida:.2f} (30%)** para abater as dívidas com maiores juros.")
            recomendacoes.append(f"- Reserve **R$ {pago_objetivo:.2f} (20%)** para seus objetivos.")
            recomendacoes.append(f"- Use os outros **R$ {salario * 0.5:.2f} (50%)** para gastos essenciais e lazer.")

        return recomendacoes
