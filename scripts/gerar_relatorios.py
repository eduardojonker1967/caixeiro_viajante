#!/usr/bin/env python3
"""
Runner principal para geração de relatórios.
Após a reorganização do projeto, os scripts foram movidos para src/reporting/.
Este arquivo mantém compatibilidade com chamadas antigas da raiz.
"""

import sys
from pathlib import Path

BASE = Path(__file__).parent

# Relatório gerencial
sys.path.insert(0, str(BASE / 'src/reporting'))
exec(open(BASE / 'src/reporting/gerador_relatorio.py', encoding='utf-8').read())

# Relatório TSP
exec(open(BASE / 'src/reporting/gerador_relatorio_tsp.py', encoding='utf-8').read())
