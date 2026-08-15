#!/usr/bin/env python3
import subprocess
import sys
import os
import uuid
import concurrent.futures
from database import db_handler

def executar_script(nome_script, run_id):
    """Executa um script Python e trata erros de execução de forma limpa."""
    print(f"\n--- 🚀 Iniciando: {nome_script} ---")
    db_handler.log_pipeline_step(run_id, nome_script, "STARTED")
    
    try:
        # Define variável de ambiente para evitar pop-ups de gráficos durante o pipeline
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        
        # Captura stderr mas mantém stdout limpo para o terminal
        result = subprocess.run(
            [sys.executable, nome_script], 
            check=True, 
            text=True, 
            stderr=subprocess.PIPE, 
            env=env
        )
        print(f"✅ {nome_script} finalizado com sucesso.")
        db_handler.log_pipeline_step(run_id, nome_script, "SUCCESS")
        
    except subprocess.CalledProcessError as e:
        # Registra a falha detalhada
        db_handler.log_pipeline_step(run_id, nome_script, "FAILED", error_msg=e.stderr, return_code=e.returncode)
        
        print(f"❌ Erro crítico: O script '{nome_script}' falhou com código de saída {e.returncode}.")
        print(f"📝 O erro foi registrado no histórico do MongoDB (Run ID: {run_id}).")
        if e.stderr:
            print(f"🔍 Detalhes do erro:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Erro: O script '{nome_script}' não foi encontrado no diretório atual.")
        sys.exit(1)

def main():
    """Orquestra a execução de todo o pipeline de roteirização preditiva."""
    run_id = str(uuid.uuid4())[:8] # ID curto para identificação rápida
    
    print(f"🏗️  Iniciando Pipeline [ID: {run_id}]...")

    # 1 e 2: Devem ser sequenciais pois o gerador de pesos depende da previsão concluída
    executar_script('analise_prophet.py', run_id)
    executar_script('geradordepesos.py', run_id)

    # 3 e 4: TRABALHO DE PARALELISMO
    # Estas tarefas são independentes e podem rodar simultaneamente economizando tempo.
    print("\n--- 🔀 Executando Auditoria e Simulação em Paralelo ---")
    scripts_paralelos = ['analise_anomalias.py', 'testestress.py']
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(executar_script, script, run_id) for script in scripts_paralelos]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"❌ Falha em tarefa paralela: {e}")
                sys.exit(1)

    # 5 e 6: Sequenciais para consolidação final e arquivamento
    executar_script('gerador_relatorio.py', run_id)
    executar_script('versionar_relatorio.py', run_id)

    print("\n" + "═"*50)
    print(" 🎉 PIPELINE FINALIZADO COM SUCESSO ".center(50, "═"))
    print(" 📂 Relatórios gerados em PDF e Markdown".center(50))
    print(" 🗄️ Snapshot salvo em 'historico_relatorios/'".center(50))
    print("═"*50)

if __name__ == "__main__":
    main()