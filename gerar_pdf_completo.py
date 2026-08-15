#!/usr/bin/env python3
"""
Gera um UNICO PDF completo com TODAS as informacoes do projeto:
- Environment details
- Resultados TSP + Monte Carlo (km, R$, tempo)
- Graficos comparativos
- Relatorio consolidado completo
- Codigo fonte dos scripts
"""

import os
import json
import glob
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# COLETA DE DADOS
# ============================================================================

def coletar_environment():
    return {
        "Current time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "Working directory": os.getcwd(),
        "Workspace root folder": os.path.abspath(os.sep),
        "Active file": os.path.basename(__file__),
        "Visible files": sorted([os.path.basename(f) for f in glob.glob('*.py') + glob.glob('*.json') + glob.glob('*.txt') + glob.glob('*.md') + glob.glob('*.tex') if os.path.isfile(f)])[:15],
    }

def carregar_resumo():
    path = 'resumo_executivo.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def carregar_relatorio_md():
    path = 'RELATORIO_TSP_CONSOLIDADO.md'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Relatório não encontrado."

def carregar_codigo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    return f"Arquivo {nome_arquivo} não encontrado."

# ============================================================================
# RENDERIZACAO DE TEXTO NO PDF
# ============================================================================

def adicionar_texto(fig, ax, texto, fontsize=9, x=0.05, y=0.95, family='monospace'):
    ax.text(x, y, texto, transform=ax.transAxes, fontsize=fontsize,
            verticalalignment='top', fontfamily=family, wrap=True,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

# ============================================================================
# PAGINAS DO PDF
# ============================================================================

def pagina_environment(pdf, env):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.clf()
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_title("Environment Details", fontsize=16, fontweight='bold', pad=20)

    linhas = ["<environment_details>"]
    for k, v in env.items():
        if isinstance(v, list):
            linhas.append(f"{k}:")
            for item in v:
                linhas.append(f"  - {item}")
        else:
            linhas.append(f"{k}: {v}")
    linhas.append("</environment_details>")

    adicionar_texto(fig, ax, "\n".join(linhas), fontsize=10, x=0.05, y=0.95)
    pdf.savefig(fig, bbox_inches='tight')

def pagina_resultados_tsp(pdf, dados):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.clf()
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_title("Resultados TSP - Nearest Neighbor + 2-opt", fontsize=16, fontweight='bold', pad=20)

    linhas = [
        "="*60,
        "TRAVELING SALESMAN PROBLEM (TSP)",
        "="*60,
        "",
        f"Rota Aleatoria (Baseline):     {dados.get('dist_aleatoria_km', 0):.2f} km",
        f"Rota Nearest Neighbor:          {dados.get('dist_nn_km', 0):.2f} km",
        f"Rota 2-opt (Otimizada):         {dados.get('dist_2opt_km', 0):.2f} km",
        "",
        f"Reducao Percentual:             {dados.get('reducao_percent', 0):.2f} %",
        f"Fator de Melhoria:              {dados.get('fator_melhoria', 0):.2f}x",
        f"Numero de Cidades:              {dados.get('n_cidades', 18)}",
    ]
    if dados.get('tempo_tsp_segundos') is not None:
        linhas.append(f"Tempo de Execucao TSP:         {dados.get('tempo_tsp_segundos', 0):.4f} s")

    adicionar_texto(fig, ax, "\n".join(linhas), fontsize=11, x=0.1, y=0.9)
    pdf.savefig(fig, bbox_inches='tight')

def pagina_resultados_mc(pdf, dados):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.clf()
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_title("Resultados Monte Carlo", fontsize=16, fontweight='bold', pad=20)

    linhas = [
        "="*60,
        "SIMULACAO MONTE CARLO",
        "="*60,
        "",
        f"Iteracoes:                      {dados.get('monte_carlo_iteracoes', 0):,}",
        f"Custo Cenário Atual (R$):       {dados.get('monte_carlo_custo_atual', 0):.2f}",
        f"Custo Modelo Otimizado (R$):    {dados.get('monte_carlo_custo_modelo', 0):.2f}",
        f"Economia Monte Carlo:           {dados.get('monte_carlo_economia_percent', 0):.2f} %",
    ]
    if dados.get('tempo_monte_carlo_segundos') is not None:
        linhas.append(f"Tempo de Execucao MC:          {dados.get('tempo_monte_carlo_segundos', 0):.4f} s")

    adicionar_texto(fig, ax, "\n".join(linhas), fontsize=11, x=0.1, y=0.9)
    pdf.savefig(fig, bbox_inches='tight')

def pagina_graficos_tsp(pdf, dados):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.clf()
    ax1 = fig.add_subplot(211)
    categorias = ['Aleatoria\n(Baseline)', 'Nearest\nNeighbor', '2-opt\n(Otimizada)']
    valores = [dados.get('dist_aleatoria_km', 0), dados.get('dist_nn_km', 0), dados.get('dist_2opt_km', 0)]
    cores = ['#E74C3C', '#F39C12', '#2ECC71']
    bars = ax1.bar(categorias, valores, color=cores, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Distancia (km)', fontsize=11, fontweight='bold')
    ax1.set_title('Comparativo de Rotas - TSP', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    for bar, val in zip(bars, valores):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val:.2f} km', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax1.set_ylim(0, max(valores)*1.15)

    ax2 = fig.add_subplot(212)
    categorias_mc = ['Custo Atual\n(R$)', 'Custo Modelo\n(R$)']
    valores_mc = [dados.get('monte_carlo_custo_atual', 0), dados.get('monte_carlo_custo_modelo', 0)]
    cores_mc = ['#E74C3C', '#2ECC71']
    bars2 = ax2.bar(categorias_mc, valores_mc, color=cores_mc, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Custo (R$)', fontsize=11, fontweight='bold')
    ax2.set_title('Comparativo de Custos - Monte Carlo', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    for bar, val in zip(bars2, valores_mc):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'R$ {val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax2.set_ylim(0, max(valores_mc)*1.15)

    plt.tight_layout(pad=3.0)
    pdf.savefig(fig, bbox_inches='tight')

def pagina_codigo(pdf, titulo, codigo, max_linhas=80):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.clf()
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_title(titulo, fontsize=13, fontweight='bold', pad=10)

    linhas = codigo.split('\n')
    if len(linhas) > max_linhas:
        texto = "\n".join(linhas[:max_linhas]) + f"\n... ({len(linhas) - max_linhas} linhas omitidas)"
    else:
        texto = codigo

    adicionar_texto(fig, ax, texto, fontsize=6.5, x=0.02, y=0.98)
    pdf.savefig(fig, bbox_inches='tight')

def pagina_relatorio_md(pdf, md_texto):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.clf()
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set_title("Relatorio Consolidado (Markdown)", fontsize=14, fontweight='bold', pad=10)

    linhas = md_texto.split('\n')
    texto = "\n".join(linhas[:120])
    if len(linhas) > 120:
        texto += f"\n... ({len(linhas) - 120} linhas omitidas)"

    adicionar_texto(fig, ax, texto, fontsize=7, x=0.02, y=0.98)
    pdf.savefig(fig, bbox_inches='tight')

# ============================================================================
# MAIN
# ============================================================================

def main():
    env = coletar_environment()
    dados = carregar_resumo()
    relatorio_md = carregar_relatorio_md()

    pdf_path = 'relatorio_completo_tsp.pdf'

    total_paginas = 0

    total_paginas = 0

    with PdfPages(pdf_path) as pdf:
        # Pagina 1: Environment + Resultados TSP
        pagina_environment(pdf, env)
        pagina_resultados_tsp(pdf, dados)

        # Pagina 2: Resultados Monte Carlo
        pagina_resultados_mc(pdf, dados)

        # Pagina 3: Graficos comparativos
        pagina_graficos_tsp(pdf, dados)

        # Pagina 4: Relatorio Markdown
        pagina_relatorio_md(pdf, relatorio_md)

        # Pagina 5+: Codigo fonte
        scripts = [
            ("resumo_executivo.py - Resumo Executivo TSP + MC", "resumo_executivo.py"),
            ("tsp_solver.py - Nearest Neighbor + 2-opt", "tsp_solver.py"),
            ("testestress.py - Simulacao Monte Carlo", "testestress.py"),
            ("gerador_relatorio_tsp.py - Gerador de Relatorio", "gerador_relatorio_tsp.py"),
        ]
        for titulo, arquivo in scripts:
            codigo = carregar_codigo(arquivo)
            pagina_codigo(pdf, titulo, codigo)

    print(f"✅ PDF completo gerado: {pdf_path}")

if __name__ == "__main__":
    main()
