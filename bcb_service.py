import pandas as pd
from bcb import sgs
import datetime

class BCBService:
    def __init__(self):
        # Mapeamento de tipos de dívida para códigos de séries SGS (exemplos)
        # 25433 - Taxa de juros - Pessoas físicas - Cartão de crédito - Rotativo total - Instituições financeiras
        # 25434 - Taxa de juros - Pessoas físicas - Crédito pessoal - Total - Instituições financeiras
        # 25435 - Taxa de juros - Pessoas físicas - Cheque especial - Instituições financeiras
        self.series_map = {
            'cartao': 25433,
            'pessoal': 25434,
            'cheque_especial': 25435,
            'veiculo': 25439,
            'imobiliario': 25442
        }

    def get_taxa_juros(self, tipo_divida):
        """
        Busca a taxa de juros média do mercado para um tipo de dívida.
        Retorna a taxa anual (%).
        """
        codigo_serie = self.series_map.get(tipo_divida.lower())
        if not codigo_serie:
            return 10.0  # Taxa padrão caso não encontre o tipo

        try:
            # Busca o último valor disponível na série
            df = sgs.get({'taxa': codigo_serie}, last=1)
            if not df.empty:
                return float(df['taxa'].iloc[0])
            return 10.0
        except Exception as e:
            print(f"Erro ao buscar taxa BCB: {e}")
            return 10.0

    def get_taxa_selic(self):
        """Retorna a taxa Selic atual (Série 11)."""
        try:
            df = sgs.get({'selic': 11}, last=1)
            if not df.empty:
                return float(df['selic'].iloc[0])
            return 13.75
        except Exception as e:
            print(f"Erro ao buscar Selic: {e}")
            return 13.75

# Teste simples (comentado para produção)
# if __name__ == "__main__":
#     service = BCBService()
#     print(f"Taxa Cartão: {service.get_taxa_juros('cartao')}%")
#     print(f"Taxa Selic: {service.get_taxa_selic()}%")
