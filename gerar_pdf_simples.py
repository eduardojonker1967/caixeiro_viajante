#!/usr/bin/env python3
"""
Gera PDF com os resultados do TSP + Monte Carlo usando matplotlib
"""

import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def main():
    json_path = 'resumo_executivo.json'
    if not os.path.exists(json_path):
        print(f"❌ Arquivo {json_path} não encontrado. Execute resumo_executivo.py primeiro.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    pdf_path = 'relatorio_tsp_resultados.pdf'
    with PdfPages(pdf_path) as pdf:
        # Página 1: Capa e Resumo
        fig = plt.figure(figsize=(8.27, 11.69))  # A4
        fig.clf()
        ax = fig.add_subplot(111)
        ax.axis('off')

        texto = (
            "RELATÓRIO DE RESULTADOS - TSP + MONTE CARLO\n\n"
            f"Data: {dados.get('timestamp', 'N/A')}\n\n"
            "="*60 + "\n"
            "TSP SOLVER (Nearest Neighbor + 2-opt)\n"
            "="*60 + "\n\n"
            f"Rota Aleatória (Baseline): {dados.get('dist_aleatoria_km', 0):.2f} km\n"
            f"Rota Nearest Neighbor:     {dados.get('dist_nn_km', 0):.2f} km\n"
            f"Rota 2-opt (Otimizada):    {dados.get('dist_2opt_km', 0):.2f} km\n\n"
            f"Redução:                   {dados.get('reducao_percent', 0):.2f}%\n"
            f"Fator de Melhoria:         {dados.get('fator_melhoria', 0):.2f}x\n"
        )
        if dados.get('tempo_tsp_segundos') is not None:
            texto += f"Tempo de Execução TSP:     {dados.get('tempo_tsp_segundos', 0):.4f} s\n"

        texto += (
            "\n" + "="*60 + "\n"
            "SIMULAÇÃO MONTE CARLO\n"
            "="*60 + "\n\n"
            f"Iterações:                 {dados.get('monte_carlo_iteracoes', 0):,}\n"
            f"Custo Cenário Atual (R$):  {dados.get('monte_carlo_custo_atual', 0):.2f}\n"
            f"Custo Modelo Otimizado (R$):{dados.get('monte_carlo_custo_modelo', 0):.2f}\n"
            f"Economia Monte Carlo:      {dados.get('monte_carlo_economia_percent', 0):.2f}%\n"
        )
        if dados.get('tempo_monte_carlo_segundos') is not None:
            texto += f"Tempo de Execução MC:      {dados.get('tempo_monte_carlo_segundos', 0):.4f} s\n"

        ax.text(0.05, 0.95, texto, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        pdf.savefig(fig, bbox_inches='tight')

        # Página 2: Gráfico comparativo TSP
        fig2 = plt.figure(figsize=(8.27, 11.69))
        fig2.clf()
        ax2 = fig2.add_subplot(111)
        categorias = ['Aleatória\n(Baseline)', 'Nearest\nNeighbor', '2-opt\n(Otimizada)']
        valores = [
            dados.get('dist_aleatoria_km', 0),
            dados.get('dist_nn_km', 0),
            dados.get('dist_2opt_km', 0),
        ]
        cores = ['#E74C3C', '#F39C12', '#2ECC71']
        bars = ax2.bar(categorias, valores, color=cores, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Distância Total (km)', fontsize=12, fontweight='bold')
        ax2.set_title('Comparativo de Distâncias - TSP', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        for bar, val in zip(bars, valores):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{val:.2f} km', ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax2.set_ylim(0, max(valores)*1.15)
        pdf.savefig(fig2, bbox_inches='tight')

        # Página 3: Gráfico Monte Carlo
        fig3 = plt.figure(figsize=(8.27, 11.69))
        fig3.clf()
        ax3 = fig3.add_subplot(111)
        categorias_mc = ['Custo Atual\n(R$)', 'Custo Modelo\n(R$)']
        valores_mc = [
            dados.get('monte_carlo_custo_atual', 0),
            dados.get('monte_carlo_custo_modelo', 0),
        ]
        cores_mc = ['#E74C3C', '#2ECC71']
        bars3 = ax3.bar(categorias_mc, valores_mc, color=cores_mc, edgecolor='black', linewidth=1.5)
        ax3.set_ylabel('Custo Logístico (R$)', fontsize=12, fontweight='bold')
        ax3.set_title('Comparativo de Custos - Monte Carlo', fontsize=14, fontweight='bold')
        ax3.grid(axis='y', linestyle='--', alpha=0.7)
        for bar, val in zip(bars3, valores_mc):
            ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'R$ {val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax3.set_ylim(0, max(valores_mc)*1.15)
        pdf.savefig(fig3, bbox_inches='tight')

    print(f"✅ PDF gerado: {pdf_path}")

if __name__ == "__main__":
    main()
