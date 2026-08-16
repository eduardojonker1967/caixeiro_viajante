import os
import shutil
from datetime import datetime
import glob

DIRETORIO_HISTORICO = 'relatorios/historico' # Diretório onde os relatórios arquivados serão salvos
ARQUIVOS_GRAFICOS = [
    'analise_previsao_geral_30d.png',
    'analise_previsao_geral_120d.png',
    'analise_previsao_geral_365d.png',
    'analise_sazonalidade_meses.png',
    'relatorio_contribuicao_ipl.png', # Novo gráfico de contribuição do IPL
    'relatorio_prioridade_ipl.png', # Gráfico de prioridade IPL
    'relatorio_comparativo_custos.png', # Gráfico de custos
    'analise_anomalias.png', # Gráfico de Isolation Forest
    'prophet_mape.txt' # Novo arquivo com o MAPE do modelo
]

def arquivar_relatorio_gerencial():
    """
    Cria um arquivo-morto (snapshot) do relatório gerencial e seus gráficos,
    armazenando-os em um diretório com timestamp para gestão e auditoria.
    """
    print("🗄️ Iniciando arquivamento do Relatório Gerencial mais recente...")

    # Encontra o relatório Markdown mais recente
    list_of_md_files = glob.glob('RELATORIO_GERENCIAL_*.md')
    if not list_of_md_files:
        print(f"❌ Erro: Nenhum relatório Markdown ('RELATORIO_GERENCIAL_*.md') encontrado.")
        print("👉 Solução: Execute `python gerador_relatorio.py` primeiro.")
        return
    latest_md_file = max(list_of_md_files, key=os.path.getctime)
    
    # Encontra o relatório PDF mais recente (pode não existir se a conversão falhou)
    latest_pdf_file = None
    list_of_pdf_files = glob.glob('RELATORIO_GERENCIAL_*.pdf')
    if list_of_pdf_files:
        latest_pdf_file = max(list_of_pdf_files, key=os.path.getctime)
    else:
        print("⚠️ Aviso: Nenhum relatório PDF ('RELATORIO_GERENCIAL_*.pdf') encontrado para arquivar.")

    os.makedirs(DIRETORIO_HISTORICO, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")

    # Cria um subdiretório para o relatório atual para manter os arquivos juntos
    diretorio_versao = os.path.join(DIRETORIO_HISTORICO, f"relatorio_{timestamp}")
    os.makedirs(diretorio_versao)
    
    # Copia o relatório MD mais recente para o diretório de arquivamento
    shutil.copy2(latest_md_file, os.path.join(diretorio_versao, os.path.basename(latest_md_file)))
    
    # Copia o relatório PDF mais recente (se existir) para o diretório de arquivamento
    if latest_pdf_file:
        shutil.copy2(latest_pdf_file, os.path.join(diretorio_versao, os.path.basename(latest_pdf_file)))
    
    # Copia os arquivos gráficos (que possuem nomes estáticos)
    for arquivo_a_arquivar in ARQUIVOS_GRAFICOS: 
        if os.path.exists(arquivo_a_arquivar):
            shutil.copy2(arquivo_a_arquivar, os.path.join(diretorio_versao, os.path.basename(arquivo_a_arquivar)))
        else:
            print(f"⚠️ Aviso: Arquivo '{arquivo_a_arquivar}' não encontrado. O relatório arquivado pode ficar incompleto.")
            
    print(f"✅ Sucesso! Relatório e gráficos associados arquivados em '{diretorio_versao}'.")
if __name__ == '__main__':
    arquivar_relatorio_gerencial()