#!/usr/bin/env python3
"""
Arquivo Mestre de Execução do Pipeline de Roteirização Preditiva

Este script orquestra a execução de todo o pipeline usando Docker Compose
para garantir que os serviços (como o MongoDB) estejam ativos.

Uso:
    python executar_tudo.py
"""

import subprocess
import sys
import os

# Define a sequência de scripts a serem executados
PIPELINE_SCRIPTS = [
    ('data_loader.py', 'Pré-processamento de Dados'),
    ('analise_prophet.py', 'Análise Preditiva (Prophet)'),
    ('geradordepesos.py', 'Cálculo de Pesos e IPL'),
    ('analise_anomalias.py', 'Detecção de Anomalias'),
    ('testestress.py', 'Simulação de ROI (Monte Carlo)'),
    ('gerador_relatorio.py', 'Geração de Relatório Gerencial'),
    ('versionar_relatorio.py', 'Versionamento e Arquivamento'),
]

def run_command(command, description):
    """Executa um comando no shell e trata o resultado."""
    print(f"\n{'─'*60}")
    print(f"▶️  {description}")
    print(f"{'─'*60}")
    try:
        subprocess.run(command, check=True, shell=True, text=True)
        print(f"✅ SUCESSO: '{description}' concluído.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO em '{description}'.")
        print(f"   Comando: {e.cmd}")
        print(f"   Código de Saída: {e.returncode}")
        print(f"   Saída de Erro:\n{e.stderr}")
        return False

def main():
    """Orquestra a execução completa do pipeline."""
    print("\n" + "="*60)
    print(" 🚀 INICIANDO PIPELINE COM DOCKER COMPOSE ".center(60))
    print("="*60)

    # Garante que os contêineres (especialmente o MongoDB) estejam de pé
    if not run_command("docker compose up -d", "Iniciando serviços com Docker Compose"):
        sys.exit(1)

    # Executa cada script do pipeline
    for script, description in PIPELINE_SCRIPTS:
        # O comando `docker compose run --rm app ...` executa o script dentro do contêiner de serviço 'app'
        # que tem acesso à rede do Docker e pode se comunicar com o MongoDB.
        command = f"docker compose run --rm api python {script}"
        if not run_command(command, f"Executando: {description}"):
            print("\n❌ Pipeline interrompido devido a erro.")
            run_command("docker compose down", "Parando serviços Docker.")
            sys.exit(1)

    run_command("docker compose down", "Finalizando e parando serviços Docker.")

    print("\n" + "="*60)
    print("🎉 PIPELINE FINALIZADO COM SUCESSO!".center(60))
    print("="*60)

if __name__ == "__main__":
    main()