import pandas as pd
import numpy as np
import os
import logging
from scripts.database import db_handler
from concurrent.futures import ProcessPoolExecutor

# Configura o Matplotlib para rodar em segundo plano (evita erro de interface gráfica)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# É necessário instalar o Prophet:
# pip install prophet
try:
    from prophet import Prophet
    from prophet.diagnostics import cross_validation, performance_metrics
except ImportError:
    import sys
    print("❌ ERRO: A biblioteca 'prophet' não está instalada no seu Python.")
    print("👉 Solução: Abra o terminal e digite: pip install prophet")
    sys.exit(1)

def simular_historico_impressoes():
    """
    Gera 1 ano de dados simulados de volume de impressões.
    """
    np.random.seed(42)
    # Ancoramos o fim do histórico na data atual para que a previsão seja "do dia"
    datas = pd.date_range(end=pd.Timestamp.now().floor('D'), periods=365)
    
    volume_base = 1200
    tendencia = np.linspace(0, 500, 365) # Crescimento gradual ao longo do ano
    sazonalidade = np.sin(np.arange(365) * (2 * np.pi / 7)) * 300 # Flutuação semanal
    ruido = np.random.normal(0, 100, 365) # Variações aleatórias reais
    
    y = volume_base + tendencia + sazonalidade + ruido
    
    df = pd.DataFrame({'ds': datas, 'y': y})
    df['y'] = df['y'].astype(float).clip(lower=0.0)
    
    return df

def carregar_dados_reais(caminho_arquivo):
    """
    Tenta carregar os dados reais de treinamento a partir de um arquivo CSV.
    Espera que o arquivo tenha alguma coluna de 'Data' e 'Volume'.
    """
    try:
        if not os.path.exists(caminho_arquivo):
            print(f"⚠️ Aviso: Base de dados '{caminho_arquivo}' não encontrada. Utilizando simulador...")
            return simular_historico_impressoes()

        print(f"Lendo base de dados pré-processada: {caminho_arquivo}")
        df = pd.read_csv(caminho_arquivo)
        df['ds'] = pd.to_datetime(df['ds'])
        df['y'] = pd.to_numeric(df['y'], errors='coerce').fillna(0)
        df = df.dropna(subset=['ds', 'y']).sort_values(by='ds')
        return df
    except Exception as e:
        print(f"❌ Erro ao ler os dados reais ({e}). Utilizando simulador como fallback...")
        return simular_historico_impressoes()

def executar_analise_prophet(arquivo_treino='historico_impressoes.csv', forecast_periods=30, output_prefix=''):
    print("1. Carregando dados históricos de impressão...")
    df_historico = carregar_dados_reais(arquivo_treino)
    
    print("2. Inicializando e treinando o modelo Prophet...")
    logging.getLogger('prophet').setLevel(logging.ERROR)
    logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

    modelo = Prophet(
        seasonality_prior_scale=10.0,
        changepoint_prior_scale=0.05,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        uncertainty_samples=1000
    )
    
    modelo.add_country_holidays(country_name='BR')
    modelo.fit(df_historico)
    
    df_historico_forecast = modelo.predict(df_historico)
    compare_cols = ['ds', 'yhat']
    if 'yhat_lower' in df_historico_forecast.columns and 'yhat_upper' in df_historico_forecast.columns:
        compare_cols += ['yhat_lower', 'yhat_upper']
    
    df_compare = df_historico.set_index('ds').join(df_historico_forecast.set_index('ds')[compare_cols])
    df_compare = df_compare.dropna()

    df_compare['abs_error'] = np.abs(df_compare['y'] - df_compare['yhat'])
    df_compare['percentage_error'] = np.where(df_compare['y'] != 0, df_compare['abs_error'] / df_compare['y'], 0)
    mape = np.mean(df_compare['percentage_error']) * 100
    mae = np.mean(df_compare['abs_error'])

    db_handler.db["model_metadata"].update_one(
        {"metrica": "MAPE", "horizonte": output_prefix or "global"},
        {"$set": {"valor": mape, "data_execucao": pd.Timestamp.now()}},
        upsert=True
    )
    db_handler.db["model_metadata"].update_one(
        {"metrica": "MAE", "horizonte": output_prefix or "global"},
        {"$set": {"valor": mae, "data_execucao": pd.Timestamp.now()}},
        upsert=True
    )

    if forecast_periods == 30:
        with open('prophet_mape.txt', 'w') as f:
            f.write(f"{mape:.2f}")
        with open('prophet_mae.txt', 'w') as f:
            f.write(f"{mae:.2f}")
        print(f"📈 MAPE (30d): {mape:.2f}% | MAE (30d): {mae:.2f}")

    if 'yhat_upper' in df_historico_forecast.columns and 'yhat_lower' in df_historico_forecast.columns:
        df_compare_anom = df_historico.merge(df_historico_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')
        anomalias = df_compare_anom[(df_compare_anom['y'] > df_compare_anom['yhat_upper']) | (df_compare_anom['y'] < df_compare_anom['yhat_lower'])]
        
        if not anomalias.empty:
            db_handler.save_dataframe(anomalias, "anomalias_prophet")
        
        print(f"Detectadas {len(anomalias)} anomalias significativas no histórico.")
    else:
        print("Aviso: Intervalos de confiança indisponíveis; detecção de anomalias ignorada.")
    
    print(f"3. Gerando previsões para os próximos {forecast_periods} dias...")
    futuro = modelo.make_future_dataframe(periods=forecast_periods, freq='D')
    previsao = modelo.predict(futuro)
    
    df_previsao = previsao[['ds', 'yhat']].tail(forecast_periods)
    collection_name = f"previsoes_{output_prefix}" if output_prefix else "previsoes_impressoes"
    
    csv_name = f"previsao_impressoes_{output_prefix}.csv" if output_prefix else "previsao_impressoes.csv"
    df_previsao.to_csv(csv_name, index=False)
    
    db_handler.save_dataframe(df_previsao, collection_name)
    
    print("4. Gerando gráficos de análise de Componentes e Sazonalidade...")
    try:
        if forecast_periods == 30:
            fig_components = modelo.plot_components(previsao)
            axes = fig_components.get_axes()
            colors = ['#FF6347', '#6A5ACD', '#20B2AA', '#FFD700']
            for i, ax in enumerate(axes):
                if ax.lines:
                    ax.lines[0].set_color(colors[i % len(colors)])
                    ax.lines[0].set_linewidth(2)
            fig_components.savefig('analise_sazonalidade_meses.png', bbox_inches='tight', dpi=300)
            plt.close(fig_components)
        
        output_png_name = f'analise_previsao_geral_{output_prefix}.png' if output_prefix else 'analise_previsao_geral.png'
        fig_forecast = modelo.plot(previsao)
        fig_forecast.savefig(output_png_name, bbox_inches='tight', dpi=300)
        plt.close(fig_forecast)
    except Exception as e:
        print(f"Aviso: O modelo gerou as previsões com sucesso, mas houve um erro ao desenhar o gráfico: {e}")

def gerar_artefatos_previsao(modelo, df_historico, forecast_periods, output_prefix):
    """Gera CSV e PNG de previsão para um horizonte específico, incluindo métricas se for 30d."""
    futuro = modelo.make_future_dataframe(periods=forecast_periods, freq='D')
    previsao = modelo.predict(futuro)
    
    df_previsao = previsao[['ds', 'yhat']].tail(forecast_periods)
    df_previsao.to_csv(f"previsao_impressoes_{output_prefix}.csv", index=False)
    
    output_png_name = f'analise_previsao_geral_{output_prefix}.png'
    fig_forecast = modelo.plot(previsao)
    fig_forecast.savefig(output_png_name, bbox_inches='tight', dpi=300)
    plt.close(fig_forecast)

    if forecast_periods == 30:
        fig_comp = modelo.plot_components(previsao)
        fig_comp.savefig('analise_sazonalidade_meses.png', bbox_inches='tight', dpi=300)
        plt.close(fig_comp)
        
        df_hist_forecast = modelo.predict(df_historico)
        hist_cols = ['ds', 'yhat']
        if 'yhat_lower' in df_hist_forecast.columns and 'yhat_upper' in df_hist_forecast.columns:
            hist_cols += ['yhat_lower', 'yhat_upper']
        df_hist_forecast = df_hist_forecast[hist_cols]
        df_comp = df_historico.merge(df_hist_forecast, on='ds')
        mape = np.mean(np.abs((df_comp['y'] - df_comp['yhat']) / df_comp['y'].replace(0, np.nan).dropna())) * 100
        mae = np.mean(np.abs(df_comp['y'] - df_comp['yhat']))
        
        if 'yhat_upper' in df_comp.columns and 'yhat_lower' in df_comp.columns:
            with open('alertas_anomalias.txt', 'w') as f:
                f.write(f"O modelo Prophet identificou {len(df_comp[df_comp['y'] > df_comp['yhat_upper']])} picos e {len(df_comp[df_comp['y'] < df_comp['yhat_lower']])} quedas atípicas no volume de impressão.")
        else:
            with open('alertas_anomalias.txt', 'w') as f:
                f.write("O modelo Prophet não gerou intervalos de confiança; detecção de anomalias indisponível.")

        with open('prophet_mape.txt', 'w') as f: f.write(f"{mape:.2f}")
        with open('prophet_mae.txt', 'w') as f: f.write(f"{mae:.2f}")

def otimizar_hyperparametros(df_historico):
    """
    Utiliza validação cruzada para encontrar os melhores hiperparâmetros para o Prophet.
    """
    print("🛠️  Iniciando otimização de hiperparâmetros com validação cruzada...")
    
    # Grade de parâmetros para testar
    param_grid = {  
        'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
        'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
    }

    # Armazena os resultados
    all_params = [dict(zip(param_grid.keys(), v)) for v in np.array(np.meshgrid(*param_grid.values())).T.reshape(-1, len(param_grid.keys()))]
    mapes = []

    # Itera sobre os parâmetros e executa a validação cruzada
    for params in all_params:
        m = Prophet(**params, yearly_seasonality=True, weekly_seasonality=True, uncertainty_samples=1000).fit(df_historico)
        
        # Validação cruzada com horizonte de 30 dias, a cada 90 dias
        df_cv = cross_validation(m, initial='180 days', period='90 days', horizon='30 days', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=1)
        mapes.append(df_p['mape'].values[0])

    # Encontra a melhor combinação
    tuning_results = pd.DataFrame(all_params)
    tuning_results['mape'] = mapes
    
    best_params = tuning_results.sort_values('mape').iloc[0].to_dict()
    
    print("✅ Otimização concluída.")
    print("Melhores parâmetros encontrados:")
    print(f"  - changepoint_prior_scale: {best_params['changepoint_prior_scale']}")
    print(f"  - seasonality_prior_scale: {best_params['seasonality_prior_scale']}")
    print(f"  - MAPE resultante: {best_params['mape']:.4f}")
    
    # Remove a coluna 'mape' para retornar apenas os parâmetros do Prophet
    del best_params['mape']
    
    return best_params

def main():
    print("🚀 Iniciando análise preditiva multitemporal otimizada...")
    df_historico = carregar_dados_reais('historico_impressoes.csv')
    
    print("2. Treinando modelo Prophet (Único para todos os horizontes)...")
    logging.getLogger('prophet').setLevel(logging.ERROR)
    logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

    # Passo de otimização adicionado
    melhores_parametros = otimizar_hyperparametros(df_historico.copy())
    modelo = Prophet(
        **melhores_parametros, yearly_seasonality=True, weekly_seasonality=True,
        uncertainty_samples=1000
    )
    
    modelo.add_country_holidays(country_name='BR')
    modelo.fit(df_historico)

    horizontes = [30, 120, 180, 365]
    print(f"⚡ Iniciando processamento paralelo para {len(horizontes)} horizontes temporais...")
    
    # Paralelismo computacional: distribui as previsões pelos cores da CPU
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(gerar_artefatos_previsao, modelo, df_historico, d, f"{d}d") for d in horizontes]
        for future in futures:
            future.result() # Garante a conclusão de todos antes de prosseguir

    print("✅ Análise multitemporal concluída.")

if __name__ == "__main__":
    main()