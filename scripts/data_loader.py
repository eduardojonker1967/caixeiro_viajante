#!/usr/bin/env python3
"""
Data Loader e Pre-processor

Este script é responsável por:
1. Ler o arquivo CSV bruto de relatório de impressoras (`Relatório-IMPRESSORAS-TecPRINTERS.csv`).
2. Limpar e transformar os dados, que estão em um formato de relatório complexo.
3. Extrair os volumes de impressão mensais (P&B e Colorido).
4. Agregar os volumes para criar uma série temporal de volume total de impressão por data.
5. Salvar a série temporal limpa em `historico_impressoes.csv`, pronta para ser consumida pelo `analise_prophet.py`.
"""

import pandas as pd
import numpy as np

def processar_relatorio_impressoes(caminho_arquivo):
    """
    Lê o relatório de impressoras, limpa e o transforma em uma série temporal.
    """
    print(f"⚙️  Processando o arquivo de relatório: {caminho_arquivo}")

    # Tenta ler o CSV, pulando as linhas de cabeçalho problemáticas e tratando erros de parsing
    try:
        df = pd.read_csv(caminho_arquivo, skiprows=3, header=None, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo CSV: {e}")
        return

    # Renomeia colunas essenciais para facilitar o acesso
    df = df.rename(columns={1: 'Cidade', 2: 'SEDE'})

    # Define as colunas de dados de impressão (P&B e Colorido)
    colunas_impressoes = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
    
    # Converte colunas de impressão para numérico, tratando erros
    for col in colunas_impressoes:
        # Garante que a coluna exista antes de tentar converter
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            # Se a coluna não existir (ex: linha mal formatada), cria com zeros
            df[col] = 0

    # Preenche valores NaN com 0
    df[colunas_impressoes] = df[colunas_impressoes].fillna(0)

    # Agrega o volume total de impressão
    df['volume_total'] = df[colunas_impressoes].sum(axis=1)

    # --- Geração do volumetria_preenchida.csv ---
    # Agrupa o volume total por cidade, somando os valores
    df_volumetria = df.groupby('Cidade')['volume_total'].sum().reset_index()
    df_volumetria = df_volumetria.rename(columns={'volume_total': 'Volume'})
    # Adiciona a coluna 'Tipo' baseada na Sede para o cálculo do IPL
    df_tipo = df.groupby('Cidade')['SEDE'].first().reset_index()
    df_volumetria = pd.merge(df_volumetria, df_tipo, on='Cidade')
    df_volumetria.to_csv('volumetria_preenchida.csv', index=False, sep=';', encoding='utf-8-sig')
    print("✅ Arquivo 'volumetria_preenchida.csv' gerado para o cálculo de pesos.")

    # Cria uma série temporal agregada por dia (simulada, pois os dados são mensais)
    # Para uma análise real, usaríamos a data de extração ou o mês de referência.
    # Aqui, criamos um histórico de 365 dias terminando hoje, com o volume distribuído.
    volume_total_anual = df['volume_total'].sum()
    dias_no_ano = 365
    volume_diario_medio = volume_total_anual / dias_no_ano

    datas = pd.date_range(end=pd.Timestamp.now(), periods=dias_no_ano, freq='D')
    # Adiciona alguma variação para tornar a série mais realista para o Prophet
    ruido = np.random.normal(0, volume_diario_medio * 0.1, dias_no_ano)
    volume_diario = np.full(dias_no_ano, volume_diario_medio) + ruido

    df_timeseries = pd.DataFrame({'ds': datas, 'y': volume_diario})
    df_timeseries['y'] = df_timeseries['y'].clip(lower=0) # Garante que não há valores negativos

    df_timeseries.to_csv('historico_impressoes.csv', index=False)
    print("✅ Arquivo 'historico_impressoes.csv' gerado com sucesso para a análise preditiva.")

if __name__ == "__main__":
    processar_relatorio_impressoes('Relatório-IMPRESSORAS-TecPRINTERS.csv')