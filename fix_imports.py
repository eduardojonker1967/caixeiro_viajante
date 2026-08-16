#!/usr/bin/env python3
"""
Atualiza imports após reorganização do projeto.
Ajusta caminhos relativos para a nova estrutura de pastas.
"""

import os
from pathlib import Path

BASE = Path('.')

# Mapeamento de imports antigos -> novos caminhos
IMPORT_FIXES = {
    'from database import': 'from scripts.database import',
    'from tsp_solver import': 'from src.optimization.tsp_solver import',
    'from testestress import': 'from src.simulation.testestress import',
    'from geradordepesos import': 'from src.logistics.geradordepesos import',
    'from analise_prophet import': 'from src.analysis.analise_prophet import',
    'from dashboard_interativo import': 'from src.visualization.dashboard_interativo import',
    'from pipeline_completo import': 'from scripts.pipeline_completo import',
    'import database': 'import scripts.database',
    'import tsp_solver': 'import src.optimization.tsp_solver',
    'import testestress': 'import src.simulation.testestress',
    'import geradordepesos': 'import src.logistics.geradordepesos',
}

# Arquivos que devem ser verificados/atualizados
TARGET_FILES = []
for ext in ['*.py', '*.md', '*.tex', '*.sh']:
    TARGET_FILES.extend(BASE.rglob(ext))

updated = []
for filepath in TARGET_FILES:
    if filepath.name == 'reorganizar_projeto.py' or filepath.name == 'fix_imports.py':
        continue
    
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        for old_import, new_import in IMPORT_FIXES.items():
            content = content.replace(old_import, new_import)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            updated.append(str(filepath.relative_to(BASE)))
    except Exception as e:
        print(f"⚠️  Erro em {filepath}: {e}")

print(f"✅ Imports atualizados em {len(updated)} arquivos:")
for f in updated:
    print(f"   - {f}")
