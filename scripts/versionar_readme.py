import os
import shutil
from datetime import datetime

ARQUIVO_ORIGEM = 'README.md'
DIRETORIO_BACKUP = 'historico_readme'
ARQUIVO_TXT_LOG = 'historico_versoes.txt'

def versionar_documentacao():
    print("🔍 Iniciando versionamento do README...")
    
    if not os.path.exists(ARQUIVO_ORIGEM):
        print(f"❌ Erro: O arquivo '{ARQUIVO_ORIGEM}' não foi encontrado no diretório atual.")
        return

    if not os.path.exists(DIRETORIO_BACKUP):
        os.makedirs(DIRETORIO_BACKUP)
        print(f"📁 Diretório '{DIRETORIO_BACKUP}' criado.")

    # Determina a próxima versão lendo o arquivo txt
    versao_atual = 1
    if os.path.exists(ARQUIVO_TXT_LOG):
        with open(ARQUIVO_TXT_LOG, 'r', encoding='utf-8') as f:
            linhas = [linha for linha in f.readlines() if 'Versão' in linha]
            if linhas:
                try:
                    # Extrai o número da versão da última linha registrada
                    ultima_linha = linhas[-1]
                    versao_atual = int(ultima_linha.split('Versão')[1].split('|')[0].strip()) + 1
                except ValueError:
                    versao_atual = len(linhas) + 1

    # Coleta a data e hora atual do sistema operacional
    agora = datetime.now()
    data_hora_arquivo = agora.strftime("%d-%m-%Y_%Hh%Mm%Ss")
    data_hora_log = agora.strftime("%d/%m/%Y às %H:%M:%S")

    # Cria a cópia física (Backup)
    nome_novo_arquivo = f"README_v{versao_atual}_{data_hora_arquivo}.md"
    caminho_backup = os.path.join(DIRETORIO_BACKUP, nome_novo_arquivo)
    shutil.copy2(ARQUIVO_ORIGEM, caminho_backup)

    # Alimenta o arquivo de texto com o log da alteração
    registro = f"Versão {versao_atual} | Data: {data_hora_log} | Arquivo Gerado: {nome_novo_arquivo}\n"
    with open(ARQUIVO_TXT_LOG, 'a', encoding='utf-8') as f:
        f.write(registro)

    print(f"✅ Sucesso! {ARQUIVO_ORIGEM} salvo como versão {versao_atual}.")
    print(f"📝 Registro adicionado em '{ARQUIVO_TXT_LOG}'.")

if __name__ == '__main__':
    versionar_documentacao()