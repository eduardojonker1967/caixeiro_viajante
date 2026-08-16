#!/usr/bin/env python3
"""Gera PDF do relatório final"""
from weasyprint import HTML
import markdown
import datetime

with open('RELATORIO_PARALELISMO_FINAL.md', 'r') as f:
    md = f.read()

html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
@page {{ margin: 2.5cm; size: A4; }}
body {{ font-family: 'Helvetica', Arial, sans-serif; color: #2c3e50; line-height: 1.6; font-size: 12pt; }}
h1 {{ color: #2980b9; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
h2 {{ color: #16a085; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
th {{ background: #3498db; color: white; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.code {{ background: #f1f2f6; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
</style>
</head>
<body>
{markdown.markdown(md)}
<div style="text-align: center; margin-top: 50px; color: #7f8c8d; font-size: 10pt;">
Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}
</div>
</body>
</html>
"""

HTML(string=html).write_pdf('RELATORIO_PARALELISMO_FINAL.pdf')
print("✅ PDF gerado: RELATORIO_PARALELISMO_FINAL.pdf")