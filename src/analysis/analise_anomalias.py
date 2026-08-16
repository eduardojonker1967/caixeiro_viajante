import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from sklearn.ensemble import IsolationForest
import os

def detectar_anomalias():
    print("🕵️ Iniciando detecção de anomalias multivariadas (Isolation Forest)...")
    
    arquivo = 'pesos_prioridade_sea.csv'
    if not os.path.exists(arquivo):
        print(f"❌ Erro: {arquivo} não encontrado.")
        return

    df = pd.read_csv(arquivo)
    
    # Seleção de variáveis para análise (Volume, Logística e IPL)
    features = ['Volume_Norm', 'Logistica_Norm', 'IPL']
    X = df[features]
    
    # Inicializa o modelo (contamination=0.1 define que esperamos ~10% de anomalias)
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    df['anomaly_score'] = model.fit_predict(X)
    
    # -1 indica anomalia, 1 indica dado normal
    df['is_anomaly'] = df['anomaly_score'].apply(lambda x: 'Sim' if x == -1 else 'Não')
    
    anomalias_detectadas = df[df['is_anomaly'] == 'Sim']
    num_anomalias = len(anomalias_detectadas)
    
    # Salva log para o relatório
    with open('alertas_anomalias_forest.txt', 'w') as f:
        f.write(f"O algoritmo Isolation Forest identificou {num_anomalias} cidades com comportamento atípico no cruzamento de Volume vs Logística.")

    # Geração do Gráfico de Dispersão
    plt.figure(figsize=(10, 6))
    colors = df['is_anomaly'].map({'Sim': '#e74c3c', 'Não': '#3498db'})
    
    plt.scatter(df['Volume'], df['IPL'], c=colors, s=100, alpha=0.7, edgecolors='k')
    
    # Adiciona etiquetas nas anomalias
    for i, row in anomalias_detectadas.iterrows():
        plt.annotate(row['Cidade'], (row['Volume'], row['IPL']), xytext=(5,5), textcoords='offset points', fontsize=9, fontweight='bold')

    plt.title('Detecção de Anomalias: Volume vs IPL (Isolation Forest)', fontsize=14)
    plt.xlabel('Volume de Impressões', fontsize=12)
    plt.ylabel('Índice de Prioridade Logística (IPL)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Legenda manual
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Normal', markerfacecolor='#3498db', markersize=10),
                       Line2D([0], [0], marker='o', color='w', label='Anomalia', markerfacecolor='#e74c3c', markersize=10)]
    plt.legend(handles=legend_elements)

    plt.savefig('analise_anomalias.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Sucesso! {num_anomalias} anomalias detectadas e gráfico 'analise_anomalias.png' gerado.")
    
    # Salva a lista de cidades anômalas para o relatório
    df[['Cidade', 'is_anomaly']].to_csv('lista_anomalias.csv', index=False)

if __name__ == "__main__":
    detectar_anomalias()