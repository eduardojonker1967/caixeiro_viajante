#!/usr/bin/env python3
"""
Runner principal do projeto: executa pipeline completo de geração
de testes, relatórios e anexos a partir da raiz.

Uso:
    python run_all.py
"""

import os
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).parent.resolve()

SCRIPTS = [
    ('src/analysis/analise_prophet.py', 'Predição Prophet'),
    ('src/logistics/geradordepesos.py', 'Cálculo IPL'),
    ('src/simulation/testestress.py', 'Monte Carlo'),
    ('src/simulation/resumo_executivo.py', 'Resumo executivo'),
    ('scripts/gerar_logs_sementes.py', 'Logs SA/AG'),
    ('scripts/validacao_completa.py', 'Validação experimental'),
    ('validacao/complementar/validacao_avancada.py', 'Validação avançada'),
    ('src/reporting/gerador_relatorio.py', 'Relatório gerencial'),
    ('src/reporting/gerador_relatorio_tsp.py', 'Relatório TSP'),
]


def run_step(path, label):
    print(f"\n{'='*70}")
    print(f"▶ {label}: {path}")
    print(f"{'='*70}")
    full_path = BASE / path
    if not full_path.exists():
        print(f"❌ Arquivo não encontrado: {full_path}")
        return False
    result = subprocess.run([sys.executable, str(full_path)], cwd=str(BASE), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ERRO em '{label}'")
        print(result.stdout)
        print(result.stderr)
        return False
    print(result.stdout)
    print(f"✅ {label} concluído.")
    return True


def main():
    print("=" * 70)
    print("🚀 RUNNER PRINCIPAL - PIPELINE COMPLETO".center(70, "="))
    print("=" * 70)

    ok = []
    fail = []
    for path, label in SCRIPTS:
        success = run_step(path, label)
        if success:
            ok.append(label)
        else:
            fail.append(label)

    print("\n" + "=" * 70)
    print("📊 RESUMO DA EXECUÇÃO".center(70, "="))
    print(f"✅ Sucesso: {len(ok)}/{len(SCRIPTS)}")
    if fail:
        print(f"❌ Falhas: {', '.join(fail)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
