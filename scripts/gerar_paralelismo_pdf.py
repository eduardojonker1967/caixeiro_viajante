#!/usr/bin/env python3
"""
Gera PDF do README_PARALELISMO.md com estilos profissionais
"""

import markdown
from weasyprint import HTML
import os
from datetime import datetime

with open('README_PARALELISMO.md', 'r', encoding='utf-8') as f:
    conteudo_md = f.read()

css_style = """
@page { margin: 2cm; size: A4; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; line-height: 1.6; font-size: 11pt; }
h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; font-size: 24pt; }
h2 { color: #2980b9; margin-top: 25px; font-size: 16pt; border-left: 4px solid #3498db; padding-left: 10px; }
h3 { color: #16a085; font-size: 13pt; }
code { background-color: #f8f9fa; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9em; color: #c7254e; }
pre { background-color: #2d3436; color: #dfe6e9; border-left: 4px solid #3498db; padding: 15px; overflow-x: auto; border-radius: 4px; }
pre code { background-color: transparent; padding: 0; color: #dfe6e9; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #3498db; color: white; font-weight: bold; }
tr:nth-child(even) { background-color: #f9f9f9; }
tr:hover { background-color: #f1f2f6; }
hr { border: 0; height: 1px; background: linear-gradient(90deg, transparent, #bdc3c7, transparent); margin: 30px 0; }
.capa { text-align: center; margin-top: 100px; margin-bottom: 50px; }
.capa h1 { border-bottom: none; font-size: 32pt; margin-bottom: 10px; }
.capa .data { margin-top: 20px; color: #7f8c8d; font-size: 12pt; }
"""

conteudo_html = markdown.markdown(conteudo_md)

html_final = f'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Paralelismo no TSP - Documentação</title>
    <style>{css_style}</style>
</head>
<body>
    <div class="capa">
        <h1>Paralelismo na Metodologia do Caixeiro Viajante (TSP)</h1>
        <div class="data">Documento gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
    </div>
    {conteudo_html}
</body>
</html>
'''

nome_arquivo = f'PARALELISMO_TSP_{datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")}.pdf'

try:
    HTML(string=html_final, base_url=os.path.abspath('.')).write_pdf(nome_arquivo)
    print(f"✅ PDF '{nome_arquivo}' gerado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao gerar PDF: {e}")