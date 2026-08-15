#!/usr/bin/env python3
"""
Gera PDF com o código atualizado do projeto TSP + Monte Carlo
"""

import os
from fpdf import FPDF

ARQUIVOS_PDF = [
    ("resumo_executivo.py", "Resumo Executivo - TSP + Monte Carlo"),
    ("gerador_relatorio_tsp.py", "Gerador de Relatório Consolidado (Markdown + LaTeX)"),
    ("tsp_solver.py", "TSP Solver - Nearest Neighbor + 2-opt"),
    ("testestress.py", "Simulação Monte Carlo"),
]

class PDF(FPDF):
    def header(self):
        self.set_font("Courier", "B", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, "", ln=True)

    def footer(self):
        self.set_y(-15)
        self.set_font("Courier", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def chapter_title(self, titulo):
        self.set_font("Courier", "B", 14)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, titulo, ln=True)
        self.ln(2)
        self.set_draw_color(0, 0, 128)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def chapter_body(self, corpo):
        self.set_font("Courier", "", 8)
        self.set_text_color(0, 0, 0)
        for linha in corpo.split("\n"):
            self.cell(0, 4, linha, ln=True)
        self.ln()

def main():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for arquivo, titulo in ARQUIVOS_PDF:
        if not os.path.exists(arquivo):
            print(f"⚠️  Arquivo não encontrado: {arquivo}")
            continue

        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()

        pdf.add_page()
        pdf.chapter_title(titulo)
        pdf.chapter_body(conteudo)
        print(f"✅ Adicionado: {arquivo}")

    pdf.output("codigo_atualizado_tsp.pdf")
    print("\n✅ PDF gerado: codigo_atualizado_tsp.pdf")

if __name__ == "__main__":
    main()
