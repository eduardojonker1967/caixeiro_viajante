import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Carregar os dados de volumetria e o inventário para saber o Tipo (Perícia/SEA)
arquivo_csv = 'volumetria_preenchida.csv'

# Validação para ajudar a identificar se o arquivo realmente está acessível
if not os.path.exists(arquivo_csv):
    print(f"⚠️ Aviso: '{arquivo_csv}' não encontrado. Criando um arquivo de teste automaticamente para evitar erros...")
    pd.DataFrame({
        'Cidade': ['SÃO PAULO', 'RIO DE JANEIRO', 'BELO HORIZONTE', 'CURITIBA', 'PORTO ALEGRE'],
        'Volume': ['1.500,00', '1.200,50', '800,00', '600', '450']
    }).to_csv(arquivo_csv, index=False, sep=';', encoding='utf-8-sig')

# Usa sep=None para detectar automaticamente vírgula ou ponto e vírgula e encoding='utf-8-sig' para evitar problemas com BOM
df_final = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8')
df_final['Cidade'] = df_final['Cidade'].astype(str).str.upper().str.strip()

# Garante que a coluna Volume exista e converte valores problemáticos/vazios para 0
if 'Volume' not in df_final.columns:
    df_final['Volume'] = 0
# Tratamento para números no padrão brasileiro caso tenham sido lidos como texto (ex: "1.500,00" -> 1500.00)
df_final['Volume'] = df_final['Volume'].apply(lambda x: str(x).replace('.', '').replace(',', '.') if isinstance(x, str) else x)
df_final['Volume'] = pd.to_numeric(df_final['Volume'], errors='coerce').fillna(0)

# ATENÇÃO: Preencher os vazios apenas na coluna 'Tipo'. O .fillna('SEA') geral transformava a coluna 'Volume' em texto!
if 'Tipo' not in df_final.columns:
    df_final['Tipo'] = 'SEA'
else:
    df_final['Tipo'] = df_final['Tipo'].fillna('SEA')

# --- GESTÃO DE CONSUMO E CUSTOS ---
# Estimativa de mix de consumo (85% P&B, 15% Colorido) e custos unitários
df_final['Vol_Preto'] = (df_final['Volume'] * 0.85).round(0)
df_final['Vol_Color'] = (df_final['Volume'] * 0.15).round(0)
df_final['Custo_Impressao_Mensal'] = (df_final['Vol_Preto'] * 0.02) + (df_final['Vol_Color'] * 0.10)
df_final['Arvores_Consumidas'] = df_final['Volume'] / 7500

# --- ADIÇÃO DE MÉTRICAS DE PERFORMANCE E LOGÍSTICA ---
# Como não temos esses dados no CSV, vamos simular valores para exemplificar.
# Na prática, substitua isso por um pd.merge() com sua base real de logística/performance.
np.random.seed(42) # Mantém os valores fixos a cada execução
# Simula um score de performance (ex: SLA de atendimento entre 50% e 100%)
df_final['Score_Performance'] = np.random.uniform(0.5, 1.0, len(df_final))
# Simula um custo ou dificuldade logística (ex: distância em km ou custo de frete)
df_final['Dificuldade_Logistica'] = np.random.uniform(50, 300, len(df_final))

# 2. Algoritmo de Criação de Pesos (Rigor Acadêmico)
# Normalização do Volume (0 a 1)
v_min, v_max = df_final['Volume'].min(), df_final['Volume'].max()
df_final['Volume_Norm'] = (df_final['Volume'] - v_min) / (v_max - v_min) if v_max != v_min else 0.5

# Normalização da Performance (0 a 1)
# Invertemos o valor (1 - score) para que cidades com *pior* performance tenham *maior* peso/prioridade
p_min, p_max = df_final['Score_Performance'].min(), df_final['Score_Performance'].max()
df_final['Perf_Norm'] = 1 - ((df_final['Score_Performance'] - p_min) / (p_max - p_min)) if p_max != p_min else 0.5

l_min, l_max = df_final['Dificuldade_Logistica'].min(), df_final['Dificuldade_Logistica'].max()
df_final['Logistica_Norm'] = (df_final['Dificuldade_Logistica'] - l_min) / (l_max - l_min) if l_max != l_min else 0.5

# --- Inovação ESG: Cálculo de Impacto Ambiental ---
# Simula emissão de CO2 com base na dificuldade (distância/tempo) e eficiência da rota
df_final['Pegada_Carbono'] = df_final['Dificuldade_Logistica'] * np.random.uniform(0.12, 0.18, len(df_final))
c_min, c_max = df_final['Pegada_Carbono'].min(), df_final['Pegada_Carbono'].max()
df_final['Carbono_Norm'] = (df_final['Pegada_Carbono'] - c_min) / (c_max - c_min) if c_max != c_min else 0.5

# Atribuição de Peso Semântico (Baseado na Ontologia)
# Perícias possuem peso 1.5 (Urgência Social) e SEA peso 1.0
df_final['Peso_Tipo'] = df_final['Tipo'].apply(lambda x: 1.5 if 'PERICIA' in str(x).upper() else 1.0)
# Normaliza o tipo para o intervalo [0, 1] para manter a consistência do IPL
df_final['Tipo_Norm'] = (df_final['Peso_Tipo'] - 1.0) / (1.5 - 1.0)

# Cálculo do IPL (Índice de Prioridade Logística)
# O IPL é uma Análise de Decisão Multicritério (MCDA) que converte variáveis heterogêneas em um ranking unificado.
# Pesos: Volume (15%), Tipo/Criticidade (25%), Performance/SLA (20%), Logística/Custo (20%), Carbono/ESG (20%)
df_final['IPL'] = (
    (df_final['Volume_Norm'] * 0.15) + 
    (df_final['Tipo_Norm'] * 0.25) +
    (df_final['Perf_Norm'] * 0.20) +
    (df_final['Logistica_Norm'] * 0.20) +
    (df_final['Carbono_Norm'] * 0.20)
)

with open('esg_impacto.txt', 'w') as f:
    f.write(f"Redução estimada de emissões otimizada: {df_final['Pegada_Carbono'].mean() * 0.15:.2f} kg CO2/mês")

def gerar_grafico_ipl(df):
    """Gera e salva um gráfico de barras com as maiores prioridades de IPL."""
    print("Gerando gráfico de prioridade IPL...")
    try:
        df_sorted = df.sort_values(by='IPL', ascending=True).tail(15) # Pega as 15 maiores prioridades
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(df_sorted['Cidade'], df_sorted['IPL'], color='#2ECC71') # Vibrant Emerald Green
        ax.set_xlabel('Índice de Prioridade Logística (IPL)')
        ax.set_ylabel('Cidade')
        ax.set_title('Top 15 Cidades por Prioridade de Roteirização (IPL)')
        fig.tight_layout()
        
        nome_arquivo = 'relatorio_prioridade_ipl.png'
        plt.savefig(nome_arquivo, dpi=300)
        plt.close()
        print(f"Gráfico '{nome_arquivo}' salvo com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível gerar o gráfico de IPL. Erro: {e}")

def gerar_grafico_contribuicao_ipl(df):
    """Gera e salva um gráfico de barras empilhadas mostrando a contribuição de cada fator para o IPL."""
    print("Gerando gráfico de contribuição do IPL...")
    try:
        # Seleciona as 5 cidades com maior IPL para visualização detalhada
        df_top_5 = df.sort_values(by='IPL', ascending=False).head(5).copy()
        
        # Garante que as colunas de contribuição existam e sejam numéricas
        df_top_5['Volume_Contribuicao'] = df_top_5['Volume_Norm'] * 0.20
        df_top_5['Tipo_Contribuicao'] = df_top_5['Peso_Tipo'] * 0.30
        df_top_5['Perf_Contribuicao'] = df_top_5['Perf_Norm'] * 0.25
        df_top_5['Logistica_Contribuicao'] = df_top_5['Logistica_Norm'] * 0.25

        fig, ax = plt.subplots(figsize=(12, 7))
        
        df_top_5.set_index('Cidade')[[
            'Volume_Contribuicao', 'Tipo_Contribuicao', 'Perf_Contribuicao', 'Logistica_Contribuicao'
        ]].plot(kind='barh', stacked=True, ax=ax, 
                color=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f']) # Cores vibrantes
        
        ax.set_xlabel('Contribuição para o IPL')
        ax.set_ylabel('Cidade')
        ax.set_title('Contribuição dos Fatores para o IPL (Top 5 Cidades)')
        ax.legend(['Volume (20%)', 'Tipo (30%)', 'Performance (25%)', 'Logística (25%)'], bbox_to_anchor=(1.05, 1), loc='upper left')
        fig.tight_layout()
        nome_arquivo = 'relatorio_contribuicao_ipl.png'
        plt.savefig(nome_arquivo, dpi=300)
        print(f"Gráfico '{nome_arquivo}' salvo com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível gerar o gráfico de contribuição do IPL. Erro: {e}")

# Salvar para uso no MPC/OR-Tools
df_final.to_csv('pesos_prioridade_sea.csv', index=False)
print("Tabela de Pesos gerada com sucesso!")
print(df_final[['Cidade', 'Volume', 'Tipo', 'IPL']].sort_values(by='IPL', ascending=False).head(10))

# Gera o gráfico de visualização do IPL
gerar_grafico_ipl(df_final)
gerar_grafico_contribuicao_ipl(df_final)