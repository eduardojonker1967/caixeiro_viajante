#!/usr/bin/env python3
"""
Gera PDF com o Environment Details do relatório TSP
"""

import os
from datetime import datetime
from fpdf import FPDF

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
    current_time = "2026-06-21T11:34:11-03:00"
    working_directory = "/home/eduardo-note/Documentos/Caixeiro viajante"
    workspace_root = "/"
    active_file = "gerador_relatorio_tsp.py"
    visible_files = ["gerador_relatorio_tsp.py"]
    open_tabs = ["mongodb-linux-x86_64.tgz", "explicacao_prophet.md", "gerador_relatorio_tsp.py"]

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.chapter_title("Environment Details")

    conteudo = f"""Current time: {current_time}
Working directory: {working_directory}
Workspace root folder: {workspace_root}
Active file: {active_file}
Visible files: {", ".join(visible_files)}
Open tabs: {", ".join(open_tabs)}
"""
    pdf.chapter_body(conteudo)

    pdf.output("environment_details.pdf")
    print("✅ PDF gerado: environment_details.pdf")

if __name__ == "__main__":
    main()
