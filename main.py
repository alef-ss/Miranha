import discord
from discord.ext import commands
import os
from database import FinanceDB
from bcb_service import BCBService
from finance_planner import FinancePlanner
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DB_URL")
token = os.getenv("TOKEN")

# Configurações do Bot
TOKEN = token # O usuário deve inserir o token aqui
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Instâncias de serviços
db = FinanceDB(db_url)
bcb = BCBService()
planner = FinancePlanner(db, bcb)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

# --- COMANDOS DE TRANSAÇÕES ---

@bot.command()
async def entrada(ctx, valor: float, *, descricao: str):
    """Registra uma entrada de dinheiro: !entrada <valor> <descrição>"""
    db.adicionar_transacao(ctx.author.id, 'entrada', valor, descricao)
    embed = discord.Embed(title="✅ Entrada Registrada", color=discord.Color.blue())
    embed.add_field(name="Valor", value=f"R$ {valor:.2f}")
    embed.add_field(name="Descrição", value=descricao)
    embed.set_footer(text=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await ctx.send(embed=embed)

@bot.command()
async def saida(ctx, valor: float, *, descricao: str):
    """Registra uma saída de dinheiro: !saida <valor> <descrição>"""
    db.adicionar_transacao(ctx.author.id, 'saida', valor, descricao)
    embed = discord.Embed(title="🔻 Saída Registrada", color=discord.Color.red())
    embed.add_field(name="Valor", value=f"R$ {valor:.2f}")
    embed.add_field(name="Descrição", value=descricao)
    embed.set_footer(text=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await ctx.send(embed=embed)

@bot.command()
async def salario(ctx, valor: float):
    """Define o salário mensal: !salario <valor>"""
    db.atualizar_salario(ctx.author.id, valor)
    embed = discord.Embed(title="💰 Salário Atualizado", color=discord.Color.green())
    embed.add_field(name="Novo Salário", value=f"R$ {valor:.2f}")
    await ctx.send(embed=embed)

# --- COMANDOS DE DÍVIDAS ---

@bot.command()
async def divida(ctx, valor: float, banco: str, tipo: str):
    """Registra uma dívida: !divida <valor> <banco> <tipo (cartao, pessoal, etc.)>"""
    # Busca taxa de juros no BCB
    taxa = bcb.get_taxa_juros(tipo)
    db.adicionar_divida(ctx.author.id, banco, tipo, valor, taxa)
    
    embed = discord.Embed(title="📑 Dívida Registrada", color=discord.Color.orange())
    embed.add_field(name="Valor", value=f"R$ {valor:.2f}")
    embed.add_field(name="Banco", value=banco)
    embed.add_field(name="Tipo", value=tipo)
    embed.add_field(name="Taxa Juros (BCB)", value=f"{taxa:.2f}% a.a.")
    await ctx.send(embed=embed)

@bot.command()
async def listar_dividas(ctx):
    """Lista todas as dívidas ativas: !listar_dividas"""
    cursor = db.conn.cursor()
    cursor.execute("SELECT id, banco, tipo, valor_restante, taxa_juros FROM dividas WHERE user_id = %s AND valor_restante > 0", (ctx.author.id,))
    dividas = cursor.fetchall()
    
    if not dividas:
        await ctx.send("✅ Você não possui dívidas ativas!")
        return
        
    embed = discord.Embed(title="📋 Suas Dívidas Ativas", color=discord.Color.orange())
    for d_id, banco, tipo, valor, taxa in dividas:
        embed.add_field(
            name=f"ID: {d_id} | {banco} ({tipo})",
            value=f"Restante: R$ {valor:.2f} | Juros: {taxa:.2f}% a.a.",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def pagar_divida(ctx, divida_id: int, valor_pago: float):
    """Registra pagamento de dívida: !pagar_divida <id> <valor>"""
    sucesso, novo_valor = db.pagar_divida(ctx.author.id, divida_id, valor_pago)
    if sucesso:
        embed = discord.Embed(title="💸 Pagamento Registrado", color=discord.Color.green())
        embed.add_field(name="Valor Pago", value=f"R$ {valor_pago:.2f}")
        embed.add_field(name="Valor Restante", value=f"R$ {novo_valor:.2f}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Dívida não encontrada ou erro no pagamento.")

# --- COMANDOS DE OBJETIVOS ---

@bot.command()
async def objetivo(ctx, valor_total: float, prioridade: str, *, descricao: str):
    """Registra um objetivo: !objetivo <valor> <prioridade (alta, media, baixa)> <descrição>"""
    db.adicionar_objetivo(ctx.author.id, descricao, valor_total, prioridade)
    embed = discord.Embed(title="🎯 Objetivo Criado", color=discord.Color.purple())
    embed.add_field(name="Descrição", value=descricao)
    embed.add_field(name="Valor Total", value=f"R$ {valor_total:.2f}")
    embed.add_field(name="Prioridade", value=prioridade.capitalize())
    await ctx.send(embed=embed)

@bot.command()
async def listar_objetivos(ctx):
    """Lista todos os objetivos: !listar_objetivos"""
    cursor = db.conn.cursor()
    cursor.execute("SELECT id, descricao, valor_total, valor_poupado, prioridade FROM objetivos WHERE user_id = %s AND valor_poupado < valor_total", (ctx.author.id,))
    objetivos = cursor.fetchall()
    
    if not objetivos:
        await ctx.send("✅ Você não possui objetivos ativos!")
        return
        
    embed = discord.Embed(title="🎯 Seus Objetivos Financeiros", color=discord.Color.purple())
    for o_id, desc, total, poupado, prioridade in objetivos:
        progresso = (poupado / total) * 100 if total > 0 else 0
        embed.add_field(
            name=f"ID: {o_id} | {desc}",
            value=f"Progresso: R$ {poupado:.2f} / R$ {total:.2f} ({progresso:.1f}%)\nPrioridade: {prioridade.capitalize()}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def poupar(ctx, objetivo_id: int, valor: float):
    """Registra economia para um objetivo: !poupar <id> <valor>"""
    cursor = db.conn.cursor()
    cursor.execute("SELECT valor_poupado, valor_total FROM objetivos WHERE id = %s AND user_id = %s", (objetivo_id, ctx.author.id))
    res = cursor.fetchone()
    if res:
        novo_poupado = res[0] + valor
        cursor.execute("UPDATE objetivos SET valor_poupado = %s WHERE id = %s", (novo_poupado, objetivo_id))
        db.conn.commit()
        
        # Também registra como uma transação de saída (para controle de saldo)
        db.adicionar_transacao(ctx.author.id, 'saida', valor, f"Poupança para objetivo ID {objetivo_id}")
        
        embed = discord.Embed(title="💰 Economia Registrada", color=discord.Color.green())
        embed.add_field(name="Valor Guardado", value=f"R$ {valor:.2f}")
        embed.add_field(name="Novo Saldo Objetivo", value=f"R$ {novo_poupado:.2f} / R$ {res[1]:.2f}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Objetivo não encontrado.")

# --- RELATÓRIOS E PLANO ---

@bot.command()
async def relatorio(ctx, mes: str = None):
    """Gera um relatório: !relatorio [YYYY-MM]"""
    if mes:
        try:
            datetime.strptime(mes, '%Y-%m')
            query_date = f"{mes}%"
        except ValueError:
            await ctx.send("❌ Formato inválido. Use AAAA-MM (ex: 2026-04).")
            return
    else:
        mes = datetime.now().strftime('%Y-%m')
        query_date = f"{mes}%"

    cursor = db.conn.cursor()

    # Entradas vs saídas
    cursor.execute(
        "SELECT tipo, SUM(valor) FROM transacoes WHERE user_id = %s AND data::text LIKE %s GROUP BY tipo",
        (ctx.author.id, query_date)
    )
    transacoes = dict(cursor.fetchall() or [])

    entradas = transacoes.get('entrada', 0.0)
    saidas = transacoes.get('saida', 0.0)
    saldo = entradas - saidas

    # Top gasto do mês
    cursor.execute(
        "SELECT descricao, SUM(valor) as total FROM transacoes WHERE user_id = %s AND tipo = 'saida' AND data::text LIKE %s GROUP BY descricao ORDER BY total DESC LIMIT 1",
        (ctx.author.id, query_date)
    )
    top_gasto = cursor.fetchone()

    # Total de transações
    cursor.execute(
        "SELECT COUNT(*) FROM transacoes WHERE user_id = %s AND data::text LIKE %s",
        (ctx.author.id, query_date)
    )
    total_transacoes = cursor.fetchone()[0]

    # Dados gerais
    res_geral = db.get_relatorio_geral(ctx.author.id)

    # Indicadores
    economia_pct = (saldo / entradas * 100) if entradas > 0 else 0
    status = "🟢 Saudável" if saldo >= 0 else "🔴 Negativo"

    # Cor dinâmica
    cor = discord.Color.green() if saldo >= 0 else discord.Color.red()

    embed = discord.Embed(
        title=f"📊 Relatório Financeiro ({mes})",
        color=cor
    )

    # Resumo
    embed.add_field(name="💰 Entradas", value=f"R$ {entradas:.2f}", inline=True)
    embed.add_field(name="💸 Saídas", value=f"R$ {saidas:.2f}", inline=True)
    embed.add_field(name="📊 Saldo", value=f"R$ {saldo:.2f}", inline=True)

    # Indicadores
    embed.add_field(name="📈 Economia", value=f"{economia_pct:.1f}%", inline=True)
    embed.add_field(name="📌 Status", value=status, inline=True)
    embed.add_field(name="🔢 Transações", value=str(total_transacoes), inline=True)

    # Destaque
    if top_gasto:
        embed.add_field(
            name="🔥 Maior Gasto",
            value=f"{top_gasto[0]} (R$ {top_gasto[1]:.2f})",
            inline=False
        )

    # Situação geral
    embed.add_field(
        name="🏦 Dívidas Totais",
        value=f"R$ {res_geral['dividas']:.2f}",
        inline=True
    )
    embed.add_field(
        name="🎯 Guardado",
        value=f"R$ {res_geral['objetivos_poupado']:.2f}",
        inline=True
    )

    # Footer
    embed.set_footer(text=f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    await ctx.send(embed=embed)

@bot.command()
async def plano(ctx):
    """Gera o plano financeiro inteligente: !plano"""
    recomendacoes = planner.gerar_plano(ctx.author.id)
    
    embed = discord.Embed(title="🧠 Plano Financeiro Inteligente", color=discord.Color.gold())
    
    # Divide as recomendações em campos do embed ou junta em uma descrição
    texto_plano = "\n".join(recomendacoes)
    if len(texto_plano) > 4096:
        texto_plano = texto_plano[:4090] + "..."
        
    embed.description = texto_plano
    await ctx.send(embed=embed)

@bot.command()
async def manual(ctx):
    """Exibe o manual de uso rápido"""
    texto = """
**📌 Comandos Básicos:**
`!entrada <valor> <desc>` - Registra entrada.
`!saida <valor> <desc>` - Registra gasto.
`!salario <valor>` - Define sua renda mensal.

**📑 Gestão de Dívidas:**
`!divida <valor> <banco> <tipo>` - Tipos: `cartao`, `pessoal`, `cheque_especial`, `veiculo`, `imobiliario`.
`!pagar_divida <id> <valor>` - Registra pagamento de uma dívida.

**🎯 Objetivos:**
`!objetivo <valor> <prioridade> <desc>` - Prioridades: `alta`, `media`, `baixa`.

**📊 Consultas:**
`!relatorio` - Resumo de tudo.
`!plano` - Sugestões inteligentes baseadas em juros e prioridades.
    """
    embed = discord.Embed(title="📖 Manual do Bot Financeiro", description=texto, color=discord.Color.light_grey())
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if TOKEN == '':
        print("AVISO: Você precisa inserir o seu token do Discord no arquivo main.py!")
    else:
        bot.run(TOKEN)
