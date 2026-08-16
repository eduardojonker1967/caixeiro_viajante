#!/usr/bin/env python3
import pandas as pd
import numpy as np
import time
import os
import logging
from concurrent.futures import ProcessPoolExecutor
from prophet import Prophet
from scripts.database import db_handler

# Silencia logs do Prophet para não poluir o terminal durante o paralelismo
logging.getLogger('prophet').setLevel(logging.ERROR)
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

def processar_cidade_paralelo(cidade, dados_cidade):
    """
    Função trabalhadora (worker): Executa a predição e cálculo de IPL para uma única cidade.
    Esta função rodará em um processo isolado.
    """
    start_time = time.time()
    
    # 1. Treinamento do Modelo Preditivo (Prophet) para a cidade
    modelo = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    modelo.add_country_holidays(country_name='BR')
    # Some Prophet/cmdstanpy versions don't accept show_progress; call fit without that arg
    modelo.fit(dados_cidade)
    
    # 2. Previsão de 30 dias
    futuro = modelo.make_future_dataframe(periods=30)
    previsao = modelo.predict(futuro)
    yhat_futuro = previsao.iloc[-1]['yhat']
    
    # 3. Cálculo de IPL (Simulação de variáveis de negócio para a cidade)
    # Em um cenário real, esses dados viriam de um banco de dados
    perf_score = np.random.uniform(0.5, 0.95)
    custo_log = np.random.uniform(100, 500)
    
    # Fórmula do IPL simplificada para o exemplo paralelo
    ipl = (yhat_futuro * 0.4) + ((1 - perf_score) * 0.3) + (custo_log * 0.3)
    
    duration = time.time() - start_time
    
    return {
        "cidade": cidade,
        "volume_previsto": round(yhat_futuro, 2),
        "performance": round(perf_score, 2),
        "ipl": round(ipl, 2),
        "tempo_processamento": round(duration, 2)
    }

def main():
    print("🏗️  Iniciando Trabalho de Paralelismo: Processamento Multi-Cidades")

    # 📍 CARREGAMENTO DINÂMICO: Buscando todas as cidades no arquivo de volumetria
    arquivo_vol = 'volumetria_preenchida.csv'
    if os.path.exists(arquivo_vol):
        try:
            df_vol = pd.read_csv(arquivo_vol, sep=None, engine='python', encoding='utf-8-sig')
            col_map = {col: 'Cidade' for col in df_vol.columns if str(col).strip().lower() == 'cidade'}
            df_vol = df_vol.rename(columns=col_map)
            cidades = [str(c).upper().strip() for c in df_vol['Cidade'].dropna().unique().tolist()]
            print(f"✅ Base de dados detectada: {len(cidades)} cidades encontradas para processamento.")
        except Exception as e:
            print(f"⚠️ Erro ao ler {arquivo_vol}: {e}. Usando cidades de teste.")
            cidades = ["FLORIANÓPOLIS", "JOINVILLE", "BLUMENAU", "CHAPECÓ", "ITAJAÍ", "CRICIÚMA", "LAGES", "BALNEÁRIO CAMBORIÚ"]
    else:
        cidades = ["FLORIANÓPOLIS", "JOINVILLE", "BLUMENAU", "CHAPECÓ", "ITAJAÍ", "CRICIÚMA", "LAGES", "BALNEÁRIO CAMBORIÚ"]

    # Gerando dados fictícios para cada cidade para demonstração
    datasets = {}
    for cidade in cidades:
        datas = pd.date_range(end=pd.Timestamp.now(), periods=100)
        y = np.random.normal(1000, 200, 100).cumsum()
        datasets[cidade] = pd.DataFrame({'ds': datas, 'y': y})

    print(f"⚙️  Distribuindo {len(cidades)} tarefas entre os núcleos da CPU...")
    
    start_total = time.time()
    resultados = []

    # O ProcessPoolExecutor cria um pool de processos. 
    # Cada processo roda em um núcleo diferente, permitindo verdadeiro paralelismo (bypass do GIL)
    with ProcessPoolExecutor() as executor:
        # Submetemos as tarefas
        futures = [executor.submit(processar_cidade_paralelo, cid, datasets[cid]) for cid in cidades]
        
        for future in futures:
            try:
                res = future.result()
                resultados.append(res)
                
                # Mostra progresso simplificado para não poluir o terminal em larga escala
                if len(resultados) % 10 == 0 or len(resultados) == len(cidades):
                    print(f"⏳ Progresso: {len(resultados)}/{len(cidades)} cidades concluídas...")
            except Exception as e:
                print(f"❌ Erro no processamento: {e}")

    # Consolidação dos resultados
    if not resultados:
        print("❌ Nenhum resultado foi gerado nas tarefas paralelas. Verifique os erros acima.")
        return

    df_final = pd.DataFrame(resultados).sort_values(by="ipl", ascending=False)

    total_duration = time.time() - start_total
    print("\n" + "="*50)
    print(f"📊 RESULTADO DO PROCESSAMENTO PARALELO")
    print("="*50)
    print(df_final)
    print("="*50)
    print(f"⏱️  Tempo total com paralelismo: {total_duration:.2f} segundos")

    try:
        print("💾 Persistindo resultados no banco de dados e CSV...")
        # Salvando no MongoDB para auditoria
        db_handler.save_dataframe(df_final, "resultados_paralelos_cidades")
        # Exportando CSV para o pipeline
        df_final.to_csv("prioridades_paralelas.csv", index=False)
        print("✅ Dados salvos com sucesso.")
    except KeyboardInterrupt:
        print("\n🛑 Interrupção detectada. Encerrando processos de forma segura...")
    except Exception as e:
        print(f"⚠️ Erro ao salvar dados: {e}")

if __name__ == "__main__":
    main()