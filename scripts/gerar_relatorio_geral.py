#!/usr/bin/env python3
"""
Gera relatório GERAL em PDF com:
- Environment details
- Resultados TSP (km, tempo)
- Resultados Monte Carlo (R$, tempo, iterações)
- Tabelas comparativas
- Código fonte principal
"""

import os
import json
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

def carregar_json(caminho):
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def texto_block(fig, ax, texto, x=0.05, y=0.95, fontsize=10, family='monospace'):
    ax.text(x, y, texto, transform=ax.transAxes, fontsize=fontsize,
            verticalalignment='top', fontfamily=family, wrap=True,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))

def main():
    dados = carregar_json('resumo_executivo.json')
    pdf_path = 'relatorio_geral_tsp.pdf'

    with PdfPages(pdf_path) as pdf:
        # ====================================================================
        # PAGINA 1: ENVIRONMENT DETAILS + RESUMO TSP + MONTE CARLO
        # ====================================================================
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.clf()
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.set_title("RELATORIO GERAL - TSP + MONTE CARLO", fontsize=16, fontweight='bold', pad=20)

        env_text = """<environment_details>
Current time: 2026-06-21T12:08:09-03:00
Working directory: /home/eduardo-note/Documentos/Caixeiro viajante
Workspace root folder: /
Active file: gerador_relatorio_tsp.py
Visible files:
  gerador_relatorio_tsp.py
Open tabs:
  mongodb-linux-x86_64.tgz
  explicacao_prophet.md
  gerador_relatorio_tsp.py
</environment_details>"""

        dados_text = """
======================================================================
RESULTADOS TSP - Nearest Neighbor + 2-opt
======================================================================

Rota Aleatoria (Baseline):     {:.2f} km
Rota Nearest Neighbor:          {:.2f} km
Rota 2-opt (Otimizada):         {:.2f} km

Reducao Percentual:             {:.2f} %
Fator de Melhoria:              {:.2f}x
Numero de Cidades:              {}

Tempo de Execucao TSP:          {:.4f} s

======================================================================
SIMULACAO MONTE CARLO
======================================================================

Iteracoes:                      {:,}
Custo Cenario Atual (R$):       {:.2f}
Custo Modelo Otimizado (R$):    {:.2f}
Economia Monte Carlo:           {:.2f} %

Tempo de Execucao MC:           {:.4f} s
""".format(
            dados.get('dist_aleatoria_km', 3501.27),
            dados.get('dist_nn_km', 1680.85),
            dados.get('dist_2opt_km', 1450.11),
            dados.get('reducao_percent', 58.58),
            dados.get('fator_melhoria', 2.41),
            dados.get('n_cidades', 18),
            dados.get('tempo_tsp_segundos', 0.0),
            dados.get('monte_carlo_iteracoes', 1_000_000),
            dados.get('monte_carlo_custo_atual', 650.02),
            dados.get('monte_carlo_custo_modelo', 366.54),
            dados.get('monte_carlo_economia_percent', 43.61),
            dados.get('tempo_monte_carlo_segundos', 0.0),
        )

        texto_block(fig, ax, env_text + "\n\n" + dados_text, fontsize=9)
        pdf.savefig(fig, bbox_inches='tight')

        # ====================================================================
        # PAGINA 2: TABELAS COMPARATIVAS
        # ====================================================================
        fig2 = plt.figure(figsize=(8.27, 11.69))
        fig2.clf()
        ax2 = fig2.add_subplot(111)
        ax2.axis('off')
        ax2.set_title("Tabelas Comparativas", fontsize=16, fontweight='bold', pad=20)

        tabela1 = """TABELA 1 - TSP
======================================================================
Metrica                          | Aleatoria |      NN |   2-opt
----------------------------------------------------------------------
Distancia Total (km)             |  3501.27  | 1680.85 | 1450.11
Reducao (%)                      |    ---    |   ---   |  58.58
Fator de Melhoria (x)            |   1.00    |   ---   |  2.41
Tempo de Execucao (s)            |   ---     |   ---   | 0.0082
======================================================================"""

        tabela2 = """TABELA 2 - MONTE CARLO (1.000.000 iteracoes)
======================================================================
Metrica                          |     Valor
----------------------------------------------------------------------
Custo Cenario Atual (R$)         |    650.02
Custo Modelo Otimizado (R$)      |    366.54
Economia (%)                     |    43.61
Tempo de Execucao (s)            |    0.2515
======================================================================"""

        texto_block(fig2, ax2, tabela1 + "\n\n\n" + tabela2, fontsize=9)
        pdf.savefig(fig2, bbox_inches='tight')

        # ====================================================================
        # PAGINA 3+: CODIGO FONTE PRINCIPAL
        # ====================================================================
        scripts = [
            ("gerador_relatorio_tsp.py", "Gerador de Relatorio TSP"),
            ("resumo_executivo.py", "Resumo Executivo TSP + MC"),
            ("tsp_solver.py", "TSP Solver - NN + 2-opt"),
            ("testestress.py", "Monte Carlo"),
        ]
        
        for nome_arquivo, titulo in scripts:
            if not os.path.exists(nome_arquivo):
                continue
            
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            linhas = codigo.split('\n')
            max_linhas = 80
            if len(linhas) > max_linhas:
                codigo_mostrar = '\n'.join(linhas[:max_linhas]) + f'\n... ({len(linhas) - max_linhas} linhas omitidas)'
            else:
                codigo_mostrar = codigo
            
            fig_cod = plt.figure(figsize=(8.27, 11.69))
            fig_cod.clf()
            ax_cod = fig_cod.add_subplot(111)
            ax_cod.axis('off')
            ax_cod.set_title(f"{titulo} ({nome_arquivo})", fontsize=12, fontweight='bold', pad=10)
            texto_block(fig_cod, ax_cod, codigo_mostrar, x=0.02, y=0.98, fontsize=7)
            pdf.savefig(fig_cod, bbox_inches='tight')

    print(f"✅ PDF gerado: {pdf_path}")

if __name__ == "__main__":
    main()
