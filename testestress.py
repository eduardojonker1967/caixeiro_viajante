import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import seaborn as sns
except ImportError:
    import sys
    print("❌ ERRO: A biblioteca 'seaborn' não está instalada no seu Python.")
    print("👉 Solução: Abra o terminal e digite: pip install seaborn")
    sys.exit(1)

def simular_testes_monte_carlo(iteracoes=1000000, cidades_rota=14, total_cidades=18):
    print(f"🎲 Iniciando Simulação Monte Carlo com {iteracoes:,} iterações (Rota: {cidades_rota}/{total_cidades} cidades)...")
    
    # Simulação vetorizada com NumPy (Processamento massivo em milissegundos)
    # Simulação de custo aleatório (Cenário Atual visitando TODAS as cidades)
    custo_atual = np.random.uniform(500, 800, iteracoes)
    
    # Otimização 1: Redução por não visitar cidades de baixa prioridade (14 de 18)
    fator_cidades = cidades_rota / total_cidades
    
    # Otimização 2: Eficiência do roteamento entre as 14 cidades (redução de 20% a 35% via OR-Tools)
    economia_rota = np.random.uniform(0.20, 0.35, iteracoes)
    
    # Custo modelo = (Custo base * proporção de cidades) otimizado pelo roteirizador
    custo_modelo = custo_atual * fator_cidades * (1 - economia_rota)
    
    # Consolidação instantânea em DataFrame
    df_testes = pd.DataFrame({'Atual': custo_atual, 'Modelo': custo_modelo})
    
    print(f"Média Custo Atual: {df_testes['Atual'].mean():.2f}")
    print(f"Média Custo Modelo: {df_testes['Modelo'].mean():.2f}")
    print(f"Economia Gerada: {((1 - df_testes['Modelo'].mean()/df_testes['Atual'].mean())*100):.2f}%")
    with open('economia_gerada.txt', 'w') as f:
        f.write(str(((1 - df_testes['Modelo'].mean()/df_testes['Atual'].mean())*100)))
    return df_testes

def gerar_grafico_comparativo(df, iteracoes=1000000, cidades_rota=14, total_cidades=18):
    """Gera e salva um gráfico comparativo dos custos."""
    print("Gerando gráfico de comparação de custos...")
    try:
        plt.figure(figsize=(12, 7))

        # Amostragem para performance no gráfico (evita travar o KDE com 10M de pontos)
        df_sample = df.sample(n=100000) if len(df) > 100000 else df

        # Cria um histograma com a curva de densidade (KDE) para uma visão estatística completa
        sns.histplot(df_sample['Atual'], label='Custo Cenário Atual', color='#E74C3C', kde=True, stat="density", linewidth=0, alpha=0.4)
        sns.histplot(df_sample['Modelo'], label='Custo com Roteirizador', color='#2ECC71', kde=True, stat="density", linewidth=0, alpha=0.4)
        
        # Adiciona os parâmetros da simulação direto no título do gráfico
        plt.title(f'Distribuição Estatística (Monte Carlo): Comparativo de Custos ({iteracoes:,} iterações)\nCenário Otimizado: Roteirizando {cidades_rota} das {total_cidades} Cidades', fontsize=14)
        
        plt.xlabel('Custo Logístico Simulado (R$)', fontsize=12)
        plt.ylabel('Densidade de Probabilidade', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7, color='#BDC3C7') # Light gray grid
        
        # Adiciona linhas verticais para marcar a média de cada cenário
        plt.axvline(df['Atual'].mean(), color='#C0392B', linestyle='--', linewidth=2, label=f"Média Atual: R${df['Atual'].mean():.2f}") # Pomegranate Red
        plt.axvline(df['Modelo'].mean(), color='#27AE60', linestyle='--', linewidth=2, label=f"Média Modelo: R${df['Modelo'].mean():.2f}") # Nephritis Green

        # Garante que todas as legendas apareçam corretamente
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        
        nome_arquivo = 'relatorio_comparativo_custos.png'
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Gráfico '{nome_arquivo}' salvo com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível gerar o gráfico de custos. Erro: {e}")

if __name__ == "__main__":
    iteracoes_sim = 1000000 # Reduzido para 1 milhão para ganho de performance sem perda de rigor
    with open('monte_carlo_iterations.txt', 'w') as f:
        f.write(str(iteracoes_sim))
    df_validacao = simular_testes_monte_carlo(iteracoes=iteracoes_sim, cidades_rota=14, total_cidades=18)
    gerar_grafico_comparativo(df_validacao, iteracoes=iteracoes_sim, cidades_rota=14, total_cidades=18)