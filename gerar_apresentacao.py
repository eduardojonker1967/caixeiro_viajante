#!/usr/bin/env python3
"""Gera PDF da apresentação"""
from weasyprint import HTML
import markdown

with open('apresentacao_proposta.md', 'r') as f:
    md = f.read()

html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
@page {{ size: A4 landscape; margin: 1.5cm; }}
body {{ font-family: 'Helvetica', Arial, sans-serif; }}
h1 {{ color: #2980b9; text-align: center; font-size: 24pt; }}
h2 {{ color: #16a085; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
pre {{ background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 8px; overflow-x: auto; }}
code {{ font-family: 'Courier New', monospace; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #3498db; padding: 10px; text-align: center; }}
th {{ background: #3498db; color: white; }}
tr:nth-child(even) {{ background: #f1f2f6; }}
.slide {{ page-break-after: always; padding: 20px; }}
</style>
</head>
<body>
{markdown.markdown(md, extensions=['fenced_code'])}
</body>
</html>
"""

HTML(string=html).write_pdf('apresentacao_proposta.pdf')
print("✅ PDF gerado")