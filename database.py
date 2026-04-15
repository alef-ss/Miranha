import psycopg2
from datetime import datetime

class FinanceDB:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id BIGINT PRIMARY KEY,
                salario REAL DEFAULT 0.0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                tipo TEXT,
                valor REAL,
                descricao TEXT,
                data TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dividas (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                banco TEXT,
                tipo TEXT,
                valor_original REAL,
                valor_restante REAL,
                taxa_juros REAL,
                data_registro TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS objetivos (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                descricao TEXT,
                valor_total REAL,
                valor_poupado REAL DEFAULT 0.0,
                prioridade TEXT,
                data_criacao TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (user_id)
            )
        ''')
        
        self.conn.commit()

    def registrar_usuario(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            (user_id,)
        )
        self.conn.commit()

    def atualizar_salario(self, user_id, salario):
        self.registrar_usuario(user_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET salario = %s WHERE user_id = %s",
            (salario, user_id)
        )
        self.conn.commit()

    def adicionar_transacao(self, user_id, tipo, valor, descricao):
        self.registrar_usuario(user_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO transacoes (user_id, tipo, valor, descricao, data) VALUES (%s, %s, %s, %s, %s)",
            (user_id, tipo, valor, descricao, datetime.now())
        )
        self.conn.commit()

    def adicionar_divida(self, user_id, banco, tipo, valor, taxa_juros):
        self.registrar_usuario(user_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO dividas (user_id, banco, tipo, valor_original, valor_restante, taxa_juros, data_registro) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user_id, banco, tipo, valor, valor, taxa_juros, datetime.now())
        )
        self.conn.commit()

    def pagar_divida(self, user_id, divida_id, valor_pago):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT valor_restante FROM dividas WHERE id = %s AND user_id = %s",
            (divida_id, user_id)
        )
        res = cursor.fetchone()
        if res:
            novo_valor = max(0, res[0] - valor_pago)
            cursor.execute(
                "UPDATE dividas SET valor_restante = %s WHERE id = %s",
                (novo_valor, divida_id)
            )
            self.conn.commit()
            return True, novo_valor
        return False, 0

    def adicionar_objetivo(self, user_id, descricao, valor_total, prioridade):
        self.registrar_usuario(user_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO objetivos (user_id, descricao, valor_total, prioridade, data_criacao) VALUES (%s, %s, %s, %s, %s)",
            (user_id, descricao, valor_total, prioridade, datetime.now())
        )
        self.conn.commit()

    def get_relatorio_geral(self, user_id):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT tipo, SUM(valor) FROM transacoes WHERE user_id = %s GROUP BY tipo",
            (user_id,)
        )
        transacoes = dict(cursor.fetchall())

        cursor.execute(
            "SELECT SUM(valor_restante) FROM dividas WHERE user_id = %s",
            (user_id,)
        )
        total_dividas = cursor.fetchone()[0] or 0.0

        cursor.execute(
            "SELECT SUM(valor_total), SUM(valor_poupado) FROM objetivos WHERE user_id = %s",
            (user_id,)
        )
        obj_res = cursor.fetchone()
        total_objetivos = obj_res[0] or 0.0
        poupado_objetivos = obj_res[1] or 0.0

        return {
            "entradas": transacoes.get('entrada', 0.0),
            "saidas": transacoes.get('saida', 0.0),
            "dividas": total_dividas,
            "objetivos_total": total_objetivos,
            "objetivos_poupado": poupado_objetivos
        }

    def close(self):
        self.conn.close()