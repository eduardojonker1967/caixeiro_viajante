#!/bin/bash

# --- Script para Execução Completa do Pipeline de Roteirização ---
# Este script automatiza a execução de todas as etapas do projeto,
# desde a análise preditiva até a geração e versionamento do relatório.
# Ele foi criado para simplificar o agendamento com o Cron.

# Navega para o diretório onde os scripts estão localizados.
# É crucial para que os scripts encontrem seus arquivos (CSVs, etc.)
PROJECT_DIR="/home/eduardo-note/Documentos/Caixeiro viajante"
cd "$PROJECT_DIR" || { echo "❌ ERRO: Não foi possível acessar o diretório do projeto '$PROJECT_DIR'. Abortando."; exit 1; }

# Define o arquivo de log. Um novo log será criado para cada dia de execução.
LOG_FILE="/tmp/pipeline_roteirizador_$(date +%Y-%m-%d).log"

# Limpa o log antigo (se existir) e inicia um novo
echo "🚀 Iniciando pipeline de roteirização em $(date)" > "$LOG_FILE"
echo "----------------------------------------------------" >> "$LOG_FILE"

# Função para executar um passo do pipeline, registrar o resultado e parar em caso de erro
executar_passo() {
    echo "▶️  Executando: $1..."
    echo "--- [$(date +%H:%M:%S)] Executando: $1 ---" >> "$LOG_FILE"
    
    # Executa o comando, redirecionando stdout e stderr para o arquivo de log
    if ! python3 "$1" >> "$LOG_FILE" 2>&1; then
        echo "❌ ERRO: Falha crítica ao executar o script '$1'."
        echo "👉 Verifique o log em '$LOG_FILE' para detalhes do erro."
        echo ""
        echo "--- 🔍 ÚLTIMAS LINHAS DO LOG DE ERRO ---"
        tail -n 15 "$LOG_FILE"
        echo "----------------------------------------"
        exit 1 # Interrompe todo o pipeline
    fi
    
    echo "✅ Sucesso: '$1' concluído."
}

# --- Execução Sequencial do Pipeline ---
executar_passo "analise_prophet.py"
executar_passo "geradordepesos.py"
executar_passo "analise_anomalias.py"
executar_passo "testestress.py"
executar_passo "gerador_relatorio.py"
executar_passo "versionar_relatorio.py"

echo "----------------------------------------------------" >> "$LOG_FILE"
echo "🎉 Pipeline concluído com sucesso em $(date)!" >> "$LOG_FILE"
echo "🎉 Pipeline concluído com sucesso! Log completo disponível em: $LOG_FILE"

exit 0