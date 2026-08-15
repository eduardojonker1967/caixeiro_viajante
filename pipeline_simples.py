#!/usr/bin/env python3
"""
Pipeline Simplificado de Roteirização Preditiva
Versão limpa e objetiva do pipeline_completo.py
Executa: Previsão → Pesos → Auditoria + Teste (paralelo) → Relatório
"""

import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Configuração
SCRIPTS_SEQUENCIAIS = [
    ('data_loader.py', 'Pré-processamento de Dados (DataLoader)'),
    ('analise_prophet.py', 'Análise Preditiva (Prophet)'),
    ('geradordepesos.py', 'Cálculo de Pesos e IPL'),
]

SCRIPTS_PARALELOS = [
    ('analise_anomalias.py', 'Detecção de Anomalias'),
    ('testestress.py', 'Simulação Monte Carlo'),
]

SCRIPTS_FINAIS = [
    ('gerador_relatorio.py', 'Geração de Relatório'),
    ('versionar_relatorio.py', 'Versionamento'),
]

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def executar_script(script_path, descricao):
    """Executa um script Python de forma limpa"""
    try:
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"  # Sem pop-ups gráficos
        
        subprocess.run(
            [sys.executable, script_path],
            check=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"  ✅ {descricao}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {descricao} - FALHOU")
        return False
    except FileNotFoundError:
        print(f"  ❌ {descricao} - Script não encontrado")
        return False

def executar_fase_sequencial(scripts_info, nome_fase):
    """Executa scripts sequencialmente"""
    print(f"\n{'─'*60}")
    print(f"  📍 FASE: {nome_fase}")
    print(f"{'─'*60}")
    
    for script, descricao in scripts_info:
        if not executar_script(script, descricao):
            return False
    
    return True

def executar_fase_paralela(scripts_info, nome_fase):
    """Executa scripts em paralelo"""
    print(f"\n{'─'*60}")
    print(f"  🔀 FASE PARALELA: {nome_fase}")
    print(f"{'─'*60}")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(executar_script, script, desc): (script, desc)
            for script, desc in scripts_info
        }
        
        for future in futures:
            if not future.result():
                return False
    
    return True

def main():
    """Orquestra o pipeline completo"""
    
    # ════════════════════════════════════════════════════════════════════════
    # INÍCIO
    # ════════════════════════════════════════════════════════════════════════
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'═'*60}")
    print(f"  🚀 PIPELINE DE ROTEIRIZAÇÃO PREDITIVA".center(60))
    print(f"  Início: {timestamp}".center(60))
    print(f"{'═'*60}")
    
    # ════════════════════════════════════════════════════════════════════════
    # FASE 1: SEQUENCIAL - Previsão e Pesos
    # ════════════════════════════════════════════════════════════════════════
    
    if not executar_fase_sequencial(SCRIPTS_SEQUENCIAIS, "Previsão e Priorização"):
        print("\n❌ Pipeline interrompido na fase de previsão.")
        sys.exit(1)
    
    # ════════════════════════════════════════════════════════════════════════
    # FASE 2: PARALELA - Auditoria e Testes
    # ════════════════════════════════════════════════════════════════════════
    
    if not executar_fase_paralela(SCRIPTS_PARALELOS, "Auditoria e Validação"):
        print("\n❌ Pipeline interrompido na fase paralela.")
        sys.exit(1)
    
    # ════════════════════════════════════════════════════════════════════════
    # FASE 3: SEQUENCIAL - Geração de Relatórios
    # ════════════════════════════════════════════════════════════════════════
    
    if not executar_fase_sequencial(SCRIPTS_FINAIS, "Relatórios e Arquivamento"):
        print("\n❌ Pipeline interrompido na fase final.")
        sys.exit(1)
    
    # ════════════════════════════════════════════════════════════════════════
    # SUCESSO
    # ════════════════════════════════════════════════════════════════════════
    
    timestamp_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'═'*60}")
    print(f"  ✅ PIPELINE FINALIZADO COM SUCESSO".center(60))
    print(f"  Término: {timestamp_fim}".center(60))
    print(f"  📂 Relatórios em: historico_relatorios/".center(60))
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    main()
