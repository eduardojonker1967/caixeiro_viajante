import os
from datetime import datetime
import pandas as pd
import platform, sys # 'sys' é necessário para sys.version.split()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
try:
    from jinja2 import Template
    import markdown
    from weasyprint import HTML
except Exception as e:
    import sys
    print(f"❌ ERRO: Bibliotecas para geração de PDF não disponíveis ({e}).")
    sys.exit(1)

# Capacidade do toner (cópias) - Definido globalmente
TONER_CAPACITY = 10000

# Configurações Financeiras de Impressão (R$)
VALOR_PRETO = 0.02
VALOR_COLOR = 0.10
MIX_COLORIDO = 0.15 # 15% das impressões são coloridas

def get_code_snippet(file_path, start_line, end_line):
    """
    Lê um arquivo e retorna as linhas entre start_line e end_line (inclusive).
    As linhas são 1-indexadas.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return "".join(lines[max(0, start_line - 1):min(len(lines), end_line)])
    except FileNotFoundError:
        return f"// Arquivo '{file_path}' não encontrado."
    except Exception as e:
        return f"// Erro ao ler snippet: {str(e)}"
def gerar_relatorio():
    """
    Compila os resultados dos scripts de análise em um relatório gerencial
    em formato Markdown, criando uma prova de conceito visual.
    """
    print("🔎 Compilando resultados para o Relatório Gerencial...")

    # --- PRÉ-VERIFICAÇÃO DE ARQUIVOS EXTERNOS ---
    # Lista de arquivos que são gerados por OUTROS scripts e são necessários ANTES de qualquer processamento.
    arquivos_externos_necessarios = [
        'previsao_impressoes_30d.csv',
        'pesos_prioridade_sea.csv',
        'analise_previsao_geral_30d.png',
        'analise_sazonalidade_meses.png',
        'relatorio_prioridade_ipl.png',
        'relatorio_comparativo_custos.png',
        'analise_anomalias.png',
        'prophet_mape.txt',
        'economia_gerada.txt',
        'monte_carlo_iterations.txt',
        'alertas_anomalias.txt',
        'alertas_anomalias_forest.txt',
        'esg_impacto.txt'
    ]

    
    arquivos_necessarios = [
        'previsao_impressoes_30d.csv',
        'previsao_impressoes_120d.csv',
        'previsao_impressoes_180d.csv',
        'previsao_impressoes_365d.csv',
        'pesos_prioridade_sea.csv',
        'analise_previsao_geral_30d.png',
        'analise_previsao_geral_120d.png',
        'analise_previsao_geral_180d.png',
        'analise_previsao_geral_365d.png',
        'analise_sazonalidade_meses.png',
        'relatorio_prioridade_ipl.png', # Gráfico de prioridade IPL
        'relatorio_contribuicao_ipl.png', # Novo gráfico de contribuição do IPL
        'relatorio_comparativo_custos.png', # Gráfico de custos
        'analise_anomalias.png', # Gráfico de Isolation Forest
        'relatorio_comparativo_roi.png', # Novo gráfico de ROI comparativo
        'prophet_mape.txt', # Arquivo com o MAPE do modelo
        'prophet_mae.txt', # Arquivo com o MAE do modelo
        'economia_gerada.txt', # Arquivo com a economia gerada
        'monte_carlo_iterations.txt' # Novo arquivo com o número de iterações do Monte Carlo
    ]
    
    # Verifica se os arquivos gerados por outros scripts existem
    for arquivo in arquivos_externos_necessarios:
        if not os.path.exists(arquivo):
            print(f"❌ ERRO: Artefato de análise '{arquivo}' não encontrado.")
            print("👉 Solução: Execute os scripts na seguinte ordem para gerar os resultados:")
            print("1. python analise_prophet.py")
            print("2. python geradordepesos.py")
            print("3. python testestress.py")
            print("4. python analise_anomalias.py")
            return

    # A economia gerada é lida do arquivo, mas o arquivo 'economia_gerada.txt' precisa ser criado pelo testestress.py
    with open('economia_gerada.txt', 'r') as f:
        economia_gerada = float(f.read())

    # --- GERAÇÃO DO GRÁFICO DE ROI COMPARATIVO (FINANCEIRO VS AMBIENTAL) ---
    # Este gráfico é gerado por este script, então não precisa ser pré-verificado.
    print("🎨 Gerando gráfico de ROI Comparativo (Financeiro vs. Ambiental)...")
    try:
        # ROI Ambiental baseado na redução de deslocamentos/visitas ineficientes
        roi_financeiro = economia_gerada
        roi_ambiental = (1 - (14/18)) * 100 # Redução proporcional baseada na poda do grafo

        plt.figure(figsize=(8, 5))
        categories = ['ROI Financeiro (Economia R$)', 'ROI Ambiental (Árvores Salvas)']
        values = [roi_financeiro, roi_ambiental]
        colors = ['#2980b9', '#27ae60']
        
        bars = plt.bar(categories, values, color=colors, alpha=0.8)
        plt.ylabel('Percentual de Eficiência (%)')
        plt.title('Comparativo de Impacto: Financeiro vs Sustentabilidade')
        plt.ylim(0, 100)
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.1f}%', ha='center', fontweight='bold')
        
        plt.savefig('relatorio_comparativo_roi.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Gráfico 'relatorio_comparativo_roi.png' gerado com sucesso.")
    except Exception as e:
        print(f"⚠️ Aviso: Falha ao gerar o gráfico 'relatorio_comparativo_roi.png'. Erro: {e}")
        # Decide se deve parar ou continuar. Vamos continuar, mas o relatório ficará sem a imagem.
        pass

    # --- VERIFICAÇÃO FINAL ---
    # Agora que este script gerou seus próprios arquivos, verificamos a lista completa.
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            print(f"❌ ERRO FATAL: O artefato '{arquivo}' ainda está faltando após todas as etapas.")
            return

    # Leitura dos dados para extrair insights quantitativos
    df_previsao_30d = pd.read_csv('previsao_impressoes_30d.csv')
    df_previsao_120d = pd.read_csv('previsao_impressoes_120d.csv')
    df_previsao_180d = pd.read_csv('previsao_impressoes_180d.csv')
    df_previsao_365d = pd.read_csv('previsao_impressoes_365d.csv')
    df_pesos = pd.read_csv('pesos_prioridade_sea.csv')
    
    cidade_prioritaria = df_pesos.sort_values(by='IPL', ascending=False).iloc[0]
    total_previsto_30d = df_previsao_30d['yhat'].sum()
    total_previsto_120d = df_previsao_120d['yhat'].sum()
    total_previsto_180d = df_previsao_180d['yhat'].sum()
    total_previsto_365d = df_previsao_365d['yhat'].sum()

    total_historical_volume = df_pesos['Volume'].sum()
    # Agora utiliza a previsão real de 365 dias para o cálculo de toners
    annual_predicted_total_volume = total_previsto_365d
    
    # Distribui o volume anual previsto total proporcionalmente ao volume histórico de cada cidade
    df_pesos['Volume_Anual_Previsto'] = (df_pesos['Volume'] / total_historical_volume) * annual_predicted_total_volume
    df_pesos['Trocas_Toner_Anual'] = df_pesos['Volume_Anual_Previsto'] / TONER_CAPACITY

    # Cálculos de Custo de Impressão (Gestão de Consumo)
    custo_unitario_medio = (VALOR_PRETO * (1 - MIX_COLORIDO)) + (VALOR_COLOR * MIX_COLORIDO)
    custo_mensal_total = total_previsto_30d * custo_unitario_medio
    custo_trimestral_total = total_previsto_120d * custo_unitario_medio
    custo_semestral_total = total_previsto_180d * custo_unitario_medio
    custo_anual_total = total_previsto_365d * custo_unitario_medio
    
    # Cálculos Ambientais (Árvores)
    arvores_30d = total_previsto_30d / 7500
    arvores_120d = total_previsto_120d / 7500
    arvores_365d = total_previsto_365d / 7500

    # Leitura do MAPE do modelo Prophet
    with open('prophet_mape.txt', 'r') as f:
        mape_prophet = float(f.read())

    # Leitura do MAE do modelo Prophet
    with open('prophet_mae.txt', 'r') as f:
        mae_prophet = float(f.read())

    # Leitura do número de iterações do Monte Carlo
    with open('monte_carlo_iterations.txt', 'r') as f:
        iteracoes_sim = int(f.read())

    # Leitura das métricas de inovação
    with open('alertas_anomalias.txt', 'r') as f:
        alerta_anomalias = f.read()
    
    with open('alertas_anomalias_forest.txt', 'r') as f:
        alerta_forest = f.read()
    
    with open('esg_impacto.txt', 'r') as f:
        impacto_esg = f.read()

    # --- Extração de trechos de código para documentação ---
    prophet_init_code = get_code_snippet('analise_prophet.py', 50, 61)
    prophet_mape_code = get_code_snippet('analise_prophet.py', 64, 71)
    ipl_calculation_code = get_code_snippet('geradordepesos.py', 70, 90)
    monte_carlo_code = get_code_snippet('testestress.py', 14, 23)

    # Coleta lista de arquivos visíveis para o bloco de auditoria
    try:
        visible_files = sorted([os.path.basename(f) for f in glob.glob('*') if os.path.isfile(f)])[:15]
    except Exception:
        visible_files = []

    agora = datetime.now()

    env_details_block = f"""<environment_details>
Current time: {agora.strftime('%Y-%m-%dT%H:%M:%S%z')}
Working directory: {os.getcwd()}
Workspace root folder: {os.path.abspath(os.sep)}
Active file: {os.path.relpath(__file__, os.path.abspath(os.sep))}
Visible files: {', '.join(visible_files) if visible_files else ''}
Baseline real (antes): regiao + ordem de chamados + experiencia do tecnico (reacao a volume represado, sem previsao)
Modelo proposto (depois): IPL preditivo + solver TSP (NN + 2-opt)
SO: {platform.system()} {platform.release()} ({platform.version()})
Arquitetura: {platform.machine()}
Python: {sys.version.split(' ')[0]}
Host: {platform.node()}
</environment_details>"""

    # Equações matemáticas
    prophet_equation = "`y(t) = g(t) + s(t) + h(t) + εt`"
    prophet_equation_explanation = """
- `y(t)`: O volume de impressões previsto no tempo `t`.
- `g(t)`: A componente de tendência, representando o crescimento ou queda não-periódica.
- `s(t)`: A componente de sazonalidade, capturando padrões periódicos (semanal, anual).
- `h(t)`: A componente de feriados, ajustando a previsão para eventos específicos.
- `εt`: O termo de erro, representando variações não modeladas."""
    # Geração do conteúdo do relatório em Markdown
    agora = datetime.now()
    
    # Coleta informações de ambiente e auditoria (Python e Máquina)
    # Coleta informações de ambiente e auditoria (Python e Máquina)
    info_os = f"{platform.system()} {platform.release()} ({platform.version()})"
    info_arch = platform.machine()
    info_python = sys.version.split(' ')[0]
    info_node = platform.node()
    
    # Gerar um timestamp para nomes de arquivos dinâmicos
    timestamp_str = agora.strftime("%Y-%m-%d_%Hh%Mm%Ss")

    # Formatação da tabela de toner para o template
    toner_table_rows = ""
    for _, row in df_pesos.sort_values(by='Trocas_Toner_Anual', ascending=False).head(10).iterrows():
        custo_anual_cidade = row['Volume_Anual_Previsto'] * custo_unitario_medio
        toner_table_rows += f"| {row['Cidade']} | {row['Volume_Anual_Previsto']:.0f} | {row['Trocas_Toner_Anual']:.2f} | R$ {custo_anual_cidade:,.2f} |\n"

    trend_table_rows = "" # Inicializa para evitar NameError no render
    # Estrutura completa do Relatório com correção de sintaxe de imagens e restauração de seções
    template_markdown_antigo = r"""
# 📊 Relatório Gerencial de Roteirização Preditiva
**Autor:** Eduardo Lopes Jonker  
**Disciplina:** Sistemas Inteligentes | UDESC  
**Data de Geração:** {{ agora }}

**Resumo Executivo:** Este documento consolida os resultados do sistema de roteirização preditiva, que integra modelagem de séries temporais, análise multicritério e simulação estocástica para otimizar a logística de frotas. O objetivo é transformar dados brutos em inteligência acionável, resultando em redução de custos e aumento da eficiência operacional.
 
---

## 1. Fundamentação Matemática e Metodologia

O projeto rompe com a roteirização estática tradicional através de uma arquitetura preditiva baseada em três pilares matemáticos:

### 1.1. Modelagem de Séries Temporais (Anticipatory Routing)
Utilizamos a decomposição aditiva do algoritmo **Prophet** para prever a volumetria futura $y(t)$:
 
$$ y(t) = g(t) + s(t) + h(t) + \epsilon_t $$
 
Onde $g(t)$ é a tendência, $s(t)$ a sazonalidade (via Séries de Fourier), $h(t)$ o impacto de feriados e $\epsilon_t$ o ruído estatístico. Esta abordagem nos permite antecipar a demanda em vez de apenas reagir a ela.

### 1.2. Projeção de Volume (30 Dias)
![Previsão Geral 30d](analise_previsao_geral_30d.png)

**Insight Chave:** O volume total previsto para os próximos 30 dias é de **{{ total_30d }} unidades**.
**Acurácia (MAPE):** {{ mape_prophet }}% (Erro Percentual Médio).
**Erro Médio Absoluto (MAE):** {{ mae_prophet }} (Desvio médio em unidades).

### 1.3. Sazonalidade e Componentes
![Componentes](analise_sazonalidade_meses.png)

A decomposição permite isolar o "peso" sazonal na operação, garantindo um planejamento de frota proativo.

### 1.4. Planejamento Tático e Estratégico (120d e 365d)
![Previsão 120d](analise_previsao_geral_120d.png)
![Previsão 365d](analise_previsao_geral_365d.png)

**Volume Acumulado (Anual):** O sistema projeta uma demanda total de **{{ total_365d }} unidades** para os próximos 12 meses.

---

## 2. Otimização e Priorização Logística (MCDA)

O **Índice de Prioridade Logística (IPL)** é o núcleo decisório deste projeto. Ele utiliza uma **Análise de Decisão Multicritério (MCDA)** para transformar variáveis de naturezas distintas em um indicador único e comparável de prioridade.

### 2.1. Metodologia de Normalização
Como as variáveis (volume, SLA, custo, pegada de carbono) possuem unidades diferentes, aplicamos a normalização *Min-Max* para o intervalo $[0, 1]$:

$$x_{norm} = \frac{x - \min(x)}{\max(x) - \min(x)}$$

### 2.2. Composição dos Pilares
O IPL consolida cinco dimensões estratégicas para uma tomada de decisão holística:
1. **Volume Futuro ($V_n$):** Projeção de demanda para evitar gargalos operacionais.
2. **Criticidade do Serviço ($T_n$):** Prioridade social (Perícias têm peso superior a atendimentos SEA).
3. **Risco de SLA ($P_n$):** Identificação de unidades com performance em queda ($1 - \text{score}$).
4. **Dificuldade Logística ($L_n$):** Otimização baseada na distância e custos de deslocamento.
5. **Sustentabilidade (ESG) ($E_n$):** Penalização de rotas com maior impacto ambiental.

A fórmula consolidada para a tomada de decisão é:

$$IPL = (V_n \cdot w_v) + (T_n \cdot w_t) + (P_n \cdot w_p) + (L_n \cdot w_l) + (E_n \cdot w_e)$$
 
![Prioridade IPL](relatorio_prioridade_ipl.png)
![Contribuição IPL](relatorio_contribuicao_ipl.png)
 
**Insight Chave:** A cidade prioritária identificada é **{{ cidade_prioritaria }}**, com score **{{ ipl_valor }}**, indicando o maior risco de rompimento de serviço se não atendida no próximo ciclo.

---

## 3. Análise Financeira e Viabilidade (ROI)

A prova de conceito econômica utiliza simulações de Monte Carlo ($N={{ iteracoes }}$) para validar o ROI sob incerteza. O custo otimizado $C_{opt}$ é modelado como:

$$C_{opt} = C_{base} \cdot \text{Fator\_Cidades} \cdot (1 - \text{Economia\_Rota})$$

![Comparativo Custos](relatorio_comparativo_custos.png)

**Conclusão Financeira:** A simulação indica uma economia média esperada de **{{ economia }}%** no custo operacional logístico.

### 3.1. Eficiência Sustentável e Governança (ESG)
![ROI Comparativo](relatorio_comparativo_roi.png)
O modelo não apenas otimiza o capital, mas reduz o impacto ambiental de forma proporcional, gerando um "ROI Verde" através da eliminação de rotas de baixa prioridade.

**Análise de Carbono:** {{ impacto_esg }}

### 3.2. Auditoria de Dados com Aprendizado Não Supervisionado
Além da análise preditiva, o sistema utiliza **Aprendizado Não Supervisionado** (Isolation Forest) para auditar a integridade dos dados e detectar comportamentos atípicos.

![Anomalias Forest](analise_anomalias.png)

**Resultado da Auditoria:** {{ alerta_forest }}

**Monitoramento de Anomalias:** {{ alerta_anomalias }}

---

## 🚀 Análise de Escalabilidade: Ecossistema Santa Catarina

O sistema demonstra robustez matemática para a gestão integral do contrato estadual:
*   **Ativos Monitorados:** 6.580 impressoras.
*   **Capilaridade:** 2.930 locais em 295 municípios.
*   **Tese Científica:** A utilização de **Clusterização Geográfica Hierárquica** permite a redução da dimensionalidade do problema em 90%. Ao aplicar o IPL como critério de seleção de nós (*Node Selection*), o sistema converte um TSP estático massivo em um **Selective VRP** dinâmico, garantindo escalabilidade para infraestruturas críticas estaduais.

---

## 4. Contribuições Científicas e Inovação

Este projeto avança em relação à literatura clássica de otimização ao introduzir três diferenciais de fronteira:

1.  **Roteirização Preditiva (Anticipatory VRP):** Transição da logística reativa para um modelo que antecipa a demanda futura (`yhat` do Prophet), resolvendo a latência operacional ao focar em *onde a demanda estará amanhã*.
2.  **Heurística de Decisão Multicritério (MCDM):** Ao contrário de métodos que usam apenas distância, o **Índice de Prioridade Logística (IPL)** consolida métricas heterogêneas (Volume, Risco de SLA, Criticidade) em um tensor matemático unificado. Na prática, converte o TSP genérico em um **Prize-Collecting TSP** orientado ao valor do negócio.
3.  **Tradução Epistemológica de Erro Estatístico:** A adaptação da Matriz de Confusão para a área de logística de frota, demonstrando empiricamente o custo de cada erro algorítmico (ex: Falso Positivo = desperdício de frete; Falso Negativo = multa por quebra de SLA).

---

## 5. Planejamento de Suprimentos e Gastos Multitemporais
| Cidade | Vol. Anual | Toners | Custo/Pág (Méd) | Custo Anual | Árvores |
| :----- | :--------- | :----- | :-------------- | :---------- | :------ |
{{ toner_table }}

**Resumo de Custos Projetados:**
- **Projeção Mensal (30 dias):** R$ {{ custo_30d }}
- **Projeção Trimestral (120 dias):** R$ {{ custo_120d }}
- **Projeção Semestral (180 dias):** R$ {{ custo_180d }}
- **Projeção Anual (365 dias):** R$ {{ custo_365d }}

---

## 6. Impacto Ambiental e Consciência Ecológica

Como elemento de análise de desperdício, o sistema quantifica o impacto em árvores (Base: 7.500 folhas/árvore):

- **Impacto Mensal:** {{ arv_30d }} árvores.
- **Impacto Anual:** {{ arv_365d }} árvores.

---

## 7. Avaliação de Decisão: Matriz de Confusão Logística

| Previsão | Realidade | Classificação | Impacto |
| :--- | :--- | :--- | :--- |
| Alta Demanda | Alta Demanda | ✅ VP | Sucesso na alocação de frota. |
| Alta Demanda | Baixa Demanda | ❌ FP | Desperdício de frete (ociosidade). |
| Baixa Demanda | Alta Demanda | ❌ FN | Quebra de SLA (atraso crítico). |
| Baixa Demanda | Baixa Demanda | ✅ VN | Economia validada (frota retida). |

---

## 8. Auditoria e Reprodutibilidade

### 8.1. Baseline Operacional Real

Na prática, antes da implementação do modelo, a definição da rota dependia de:
- **Região geográfica**: agrupamento informal por proximidade.
- **Ordem de chamados**: priorização por demanda já represada.
- **Experiência do técnico**: ajustes manuais baseados em conhecimento tácito.

Essa baseline não possuía previsão de demanda nem priorização por valor de negócio, resultando em rotas reativas.

### 8.2. Comparativo Antes/Depois

| Métrica | Baseline Real (antes) | Modelo Otimizado (depois) |
|:--------|:---------------------:|:-------------------------:|
| Distância total (km) | 3501.27 | 1430.76 |
| Redução de distância | — | 59.14% |
| Custo operacional (R$/mês) | 1526.79 | 1333.54 |
| Economia mensal | — | R$ 193.25 |

### 8.3. Solver de Referência / Ótimo

Para validar o gap das heurísticas, foi utilizado como referência o melhor resultado
entre 2-opt e Simulated Annealing (melhor heurística = 1430.76 km).
A rota aleatória serve como baseline inferior (3501.27 km).

| Métrica | Valor |
|:--------|------:|
| Ótimo local (referência) | 1430.76 km |
| Rota aleatória | 3501.27 km |
| Gap heurístico | 59.14% |

### 8.3. Benchmark de Solvers e Gap para o Ótimo

A Tabela X compara os algoritmos implementados contra a melhor heurística (óbito de referência).

| Solver | Distância (km) | Gap vs ótimo (%) |
|:-------|---------------:|-----------------:|
| Aleatória | 3251.87 | 124.25% |
| NN | 1680.85 | 15.91% |
| 2-opt | 1450.11 | 0.00% |
| SA | 1481.91 | 2.19% |
| AG | 1638.11 | 12.96% |

Ótimo local de referência: **1450.11 km** (melhor heurística para 18 nós).

### 8.4. Validação Estocástica (Reprodutibilidade)

Foram executadas 30 seeds para SA e 30 seeds para AG, com as seguintes estatísticas:

**Simulated Annealing (SA)**

| Estatística | Valor (km) |
|:---|:---:|
| Média | 1455.45 |
| Mediana | 1450.11 |
| Melhor | 1430.76 |
| Pior | 1517.52 |
| Desvio padrão | 21.24 |
| CV (%) | 1.46% |
| IC 95% | [1447.85, 1463.05] |
| Tempo médio | 0.0736 s |

**Algoritmo Genético (AG)**

| Estatística | Valor (km) |
|:---|:---:|
| Média | 1525.36 |
| Mediana | 1514.02 |
| Melhor | 1443.61 |
| Pior | 1741.11 |
| Desvio padrão | 69.86 |
| CV (%) | 4.58% |
| IC 95% | [1500.36, 1550.35] |
| Tempo médio | 0.6904 s |

Arquivo completo: `validacao_estocastica.csv` (60 registros).

### 8.5. Validação Multi-Ciclo (Antes/Depois)

Foram simulados 10 ciclos operacionais, comparando baseline real (rota aleatória) vs modelo otimizado (2-opt).

| Ciclo | Baseline (km) | Modelo (km) | Redução (%) |
|:------|--------------:|------------:|------------:|
| 1 | 4008.92 | 1450.11 | 63.83% |
| 2 | 3626.90 | 1450.11 | 60.02% |
| 3 | 2983.67 | 1450.11 | 51.40% |
| 4 | 3724.10 | 1450.11 | 61.06% |
| 5 | 3263.22 | 1450.11 | 55.56% |
| 6 | 3447.01 | 1450.11 | 57.93% |
| 7 | 3176.04 | 1450.11 | 54.34% |
| 8 | 3472.08 | 1450.11 | 58.24% |
| 9 | 3325.81 | 1450.11 | 56.40% |
| 10 | 2853.75 | 1450.11 | 49.19% |

Redução média: **56.80%** | Desvio padrão: **4.42%**

Arquivo completo: `validacao_campo.csv`.

### 8.6. Premissas Econômicas (TCO/ROI)

- Custo fixo mensal: R$ 1200,00 (salário, depreciação, seguro)
- Custo variável: R$ 2,80/km (combustível + manutenção)
- Investimento de implantação: R$ 15000,00
- Vida útil: 3 anos
- Taxa de desconto: 10% a.a.

Cenários:
- **Pessimista**: economia de 47.31%
- **Base**: economia de 59.14%
- **Otimista**: economia de 65.05%

ROI: payback em 77.6 meses; retorno anual de 15.5%.

### 8.5. Origem das Distâncias

As distâncias entre as 18 cidades de Santa Catarina foram calculadas a partir das
coordenadas geográficas (latitude/longitude) de cada município, utilizando a fórmula
de Haversine para obter a distância geodésica em quilômetros (raio terrestre = 6371 km).
Essa matriz representa a distância de percurso mais curta entre pares de cidades,
independentemente de modo de transporte ou condição de tráfego. Data de referência:
agosto/2026.

### 8.6. Logs de Sementes SA/AG

Foram executadas 30 seeds para Simulated Annealing (SA) e 30 seeds para Algoritmo Genético (AG).
Abaixo, resumo estatístico das distâncias obtidas.

**Simulated Annealing (SA)**

| Estatística | SA (km) |
|:---|:---:|
| Média | 1456.49 |
| Mediana | 1450.11 |
| Melhor | 1430.76 |
| Pior | 1517.52 |
| Desvio | 21.61 |

**Algoritmo Genético (AG)**

| Estatística | AG (km) |
|:---|:---:|
| Média | 1720.76 |
| Mediana | 1687.54 |
| Melhor | 1453.75 |
| Pior | 1956.61 |
| Desvio | 135.18 |

O arquivo completo com as 60 sementes está em `logs_sa_ag_sementes.csv`.

### 8.7. Snippets de Implementação

**Treinamento do Modelo:**
```python
{{ code_prophet }}
```

**Cálculo do IPL:**
```python
{{ code_ipl }}
```

---

## 9. Informações do Ambiente e Auditoria
{{ env_details_block }}
"""

    # Renderização do template
    template_markdown = r"""
# 📄 Relatório Científico Automatizado: Roteirização Preditiva

**Autor:** Eduardo Lopes Jonker  
**Data de Geração:** {{ agora }}

## Abstract

Este relatório apresenta um sistema de roteirização logística inteligente que transcende a otimização de rotas clássica. A metodologia integra modelagem preditiva de séries temporais (Prophet), análise de decisão multicritério (MCDA) e otimização de rotas (TSP) para criar um framework de **Roteirização Preditiva Antecipatória**. O sistema não apenas minimiza a distância, mas maximiza o valor do negócio ao priorizar dinamicamente os nós da malha logística com base em um **Índice de Prioridade Logística (IPL)**. A validação econômica é realizada por meio de Simulações de Monte Carlo, e a robustez dos dados é auditada por algoritmos de detecção de anomalias. O resultado é um Gêmeo Digital para gestão de frotas, capaz de reduzir custos operacionais e a pegada de carbono da operação.

---

## 1. Introdução

O Problema do Caixeiro Viajante (TSP) é um dos desafios mais emblemáticos da otimização combinatória. Soluções tradicionais, no entanto, tratam o problema de forma estática, assumindo que a necessidade de visita é binária e o único custo é a distância. Em cenários logísticos reais, a decisão de *qual cidade visitar* é dinâmica e multifacetada.

Este trabalho propõe uma solução híbrida que transforma o TSP clássico em um problema de roteirização preditiva e orientada a valor. A inovação central reside na criação do **Índice de Prioridade Logística (IPL)**, uma métrica que converte o problema de "qual a rota mais curta?" para "qual a rota de maior valor para o negócio?".

## 2. Metodologia Proposta

A arquitetura do sistema é um pipeline modular onde a saída de cada etapa alimenta a subsequente.

### 2.1. Modelagem Preditiva com Prophet

Utilizamos o algoritmo Prophet para modelar a série temporal de volume de impressões. A natureza aditiva do Prophet decompõe a série em tendência, sazonalidade e feriados:

$$ y(t) = g(t) + s(t) + h(t) + \epsilon_t $$

Onde:
- **$g(t)$**: Tendência de crescimento ou queda.
- **$s(t)$**: Padrões periódicos (semanal, anual).
- **$h(t)$**: Efeito de feriados.
- **$\epsilon_t$**: Termo de erro (ruído).

A saída, **yhat**, representa a demanda *esperada*, permitindo uma roteirização antecipatória.

![Previsão Geral 30d](analise_previsao_geral_30d.png)
*Gráfico 1: Projeção de demanda para os próximos 30 dias com intervalo de confiança.*

**Acurácia (MAPE):** {{ mape_prophet }}% (Erro Percentual Médio).

### 2.2. Índice de Prioridade Logística (IPL)

O IPL é o núcleo decisório do sistema, utilizando uma Análise de Decisão Multicritério (MCDA) para fundir variáveis heterogêneas em um único score de prioridade. Cada variável é normalizada (Min-Max) e então ponderada:

$$ IPL = \sum_{i=1}^{n} w_i \cdot V_{i,norm} $$

Os pesos $w_i$ representam a importância estratégica de cada variável $V_i$ (Volume, Criticidade, Performance, Custo Logístico, ESG).

![Prioridade IPL](relatorio_prioridade_ipl.png)
*Gráfico 2: Ranking de cidades por prioridade de roteirização (IPL).*

### 2.3. Otimização de Rota (TSP)

Com as cidades priorizadas pelo IPL, o problema é reduzido a um TSP clássico. A implementação atual utiliza uma abordagem heurística em duas fases:
1.  **Nearest Neighbor (NN)**: Uma heurística construtiva e gulosa que gera uma rota inicial de boa qualidade em tempo $O(n^2)$.
2.  **2-opt**: Uma heurística de melhoria local que refina a rota do NN, removendo cruzamentos de arestas até atingir um ótimo local.

---

## 3. Análise Comparativa de Estratégias para o TSP

A escolha do algoritmo para resolver o TSP é um trade-off entre a qualidade da solução e o tempo computacional. A tabela abaixo compara a abordagem do projeto com outras estratégias da literatura.

| Categoria | Algoritmos Exemplo | Garantia de Otimalidade | Complexidade e Aplicação |
| :--- | :--- | :--- | :--- |
| **Métodos Exatos** | Branch-and-Bound, Concorde | Sim, encontra a solução ótima. | Exponencial ($O(n^2 2^n)$). Inviável para problemas com mais de algumas dezenas de cidades. |
| **Heurísticas Construtivas** | **Nearest Neighbor (NN)**, Inserção Mais Distante | Não. Soluções 15-25% piores que a ótima. | Polinomial ($O(n^2)$). Muito rápido, ideal para gerar soluções iniciais. **(Usado no projeto)** |
| **Heurísticas de Melhoria Local** | **2-opt**, 3-opt, Lin-Kernighan (LKH) | Não, encontra ótimos locais. | Polinomial ($O(n^2)$ a $O(n^3)$). Rápido e eficaz para refinar rotas. **(2-opt usado no projeto)** |
| **Meta-heurísticas** | Simulated Annealing (SA), Algoritmos Genéticos (GA), Ant Colony (ACO) | Não. Projetadas para escapar de ótimos locais. | Iterativas e estocásticas. Mais lentas, mas com potencial para soluções de altíssima qualidade. |
| **Aprendizado de Máquina** | Reinforcement Learning (RL), GNNs | Não. Aprendem políticas a partir dos dados. | Inferência rápida, mas treinamento caro. Generalização é um desafio ativo de pesquisa. |

### Justificativa da Abordagem Adotada

A combinação **Nearest Neighbor + 2-opt** foi escolhida por oferecer um excelente balanço entre simplicidade, velocidade e qualidade da solução para o escopo do problema (18 cidades). Para problemas de maior escala (centenas de cidades), uma evolução natural seria usar algoritmos mais robustos como o **Lin-Kernighan-Helsgaun (LKH)** ou bibliotecas especializadas como o **Google OR-Tools**.

---

## 4. Resultados e Discussão

### 4.1. Validação Econômica (Simulação de Monte Carlo)

Para validar o impacto financeiro, uma simulação de Monte Carlo com $N={{ iteracoes }}$ iterações foi executada. A simulação compara o custo operacional de um cenário "reativo" com o custo do modelo preditivo otimizado.

![Comparativo Custos](relatorio_comparativo_custos.png)
*Gráfico 3: Distribuição de probabilidade de custos, comparando o cenário atual com o modelo otimizado.*

**Conclusão Financeira:** A simulação indica uma economia média esperada de **{{ economia }}%** no custo operacional logístico.

### 4.2. Auditoria de Dados com Isolation Forest

O sistema utiliza o algoritmo **Isolation Forest** para auditar a integridade dos dados e detectar comportamentos atípicos que poderiam distorcer a priorização.

![Anomalias Forest](analise_anomalias.png)
*Gráfico 4: Detecção de anomalias no cruzamento de Volume vs. IPL.*

**Resultado da Auditoria:** {{ alerta_forest }}

---

## 5. Variações do Problema: do TSP ao VRP

O TSP é a base, mas problemas logísticos reais frequentemente se manifestam como o **Problema de Roteamento de Veículos (VRP)**, que generaliza o TSP para múltiplos veículos. O projeto já contém uma estrutura inicial para essa evolução (`main_vrp.py`). Futuras integrações podem incluir:

- **CVRP (Capacitated VRP):** Veículos com capacidade de carga limitada.
- **VRPTW (VRP with Time Windows):** Clientes com janelas de tempo para visita.
- **DVRP (Dynamic VRP):** Novos pedidos surgem em tempo real, exigindo re-roteirização.

---

## 6. Conclusão

Este trabalho demonstrou com sucesso a implementação de um sistema de roteirização preditiva que supera as limitações do TSP tradicional. Ao integrar modelagem de séries temporais e análise de decisão multicritério, o sistema transforma a otimização logística de um problema puramente geométrico para uma decisão estratégica orientada a valor. A abordagem heurística (Nearest Neighbor + 2-opt) provou ser altamente eficaz para o escopo do problema, com baixo custo computacional. Os resultados financeiros e de performance reforçam que a verdadeira inovação na logística moderna não está apenas em encontrar a rota ótima, mas em prever e priorizar de forma inteligente *quais paradas devem compor essa rota*.

---

## Apêndice: Informações de Auditoria

{{ env_details_block }}
"""
    j2_template = Template(template_markdown)
    conteudo_md = j2_template.render(
        agora=agora,
        total_30d=f"{total_previsto_30d:,.0f}",
        total_365d=f"{total_previsto_365d:,.0f}",
        custo_30d=f"{custo_mensal_total:,.2f}",
        custo_120d=f"{custo_trimestral_total:,.2f}",
        custo_180d=f"{custo_semestral_total:,.2f}",
        custo_365d=f"{custo_anual_total:,.2f}",
        roi_ambiental=f"{(1 - (14/18)) * 100:.1f}",
        arv_30d=f"{arvores_30d:.2f}",
        arv_120d=f"{arvores_120d:.2f}",
        arv_365d=f"{arvores_365d:.2f}",
        valor_preto=f"{VALOR_PRETO:.2f}",
        valor_color=f"{VALOR_COLOR:.2f}",
        mix_color=int(MIX_COLORIDO * 100),
        mape_prophet=f"{mape_prophet:.2f}",
        mae_prophet=f"{mae_prophet:.2f}",
        cidade_prioritaria=cidade_prioritaria['Cidade'],
        ipl_valor=f"{cidade_prioritaria['IPL']:.2f}",
        toner_capacity=TONER_CAPACITY,
        toner_table=toner_table_rows,
        trend_table=trend_table_rows,
        economia=f"{economia_gerada:.2f}",
        iteracoes=f"{iteracoes_sim:,}",
        equation=prophet_equation,
        explanation=prophet_equation_explanation,
        code_prophet=prophet_init_code,
        code_ipl=ipl_calculation_code,
        info_os=info_os,
        info_arch=info_arch,
        info_python=info_python,
        info_node=info_node,
        alerta_forest=alerta_forest,
        alerta_anomalias=alerta_anomalias
    )
    
    # Salva o relatório
    nome_arquivo_relatorio = f'RELATORIO_GERENCIAL_{timestamp_str}.md'
    with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(conteudo_md)
        
    print(f"✅ Sucesso! Relatório MD '{nome_arquivo_relatorio}' gerado.")
    
    # --- Geração do PDF Estilizado ---
    print("🎨 Convertendo relatório para PDF com estilos CSS...")
    
    css_style = """
    @page { margin: 2cm; size: A4; }
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; font-size: 11pt; }
    h1 { color: #1e1b4b; border-bottom: 3px solid #4f46e5; padding-bottom: 10px; font-size: 24pt; }
    h2 { color: #312e81; margin-top: 25px; font-size: 18pt; border-left: 4px solid #6366f1; padding-left: 10px;}
    h3 { color: #4338ca; font-size: 14pt; }
    img { max-width: 100%; height: auto; display: block; margin: 20px auto; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    code { background-color: #eef2ff; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9em; color: #4338ca; }
    pre { background-color: #1e293b; color: #e2e8f0; border-left: 4px solid #818cf8; padding: 15px; overflow-x: auto; border-radius: 8px; }
    pre code { background-color: transparent; padding: 0; color: #e2e8f0; }
    hr { border: 0; height: 1px; background: #e2e8f0; margin: 40px 0; }
    .insight { background-color: #eef2ff; padding: 15px; border-left: 5px solid #6366f1; margin: 20px 0; border-radius: 4px; }
    .insight strong { color: #312e81; }
    
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; font-weight: bold; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    /* Estilos da Capa */
    .capa { text-align: center; margin-top: 150px; page-break-after: always; }
    .capa h1 { border-bottom: none; font-size: 36pt; margin-bottom: 10px; color: #1e1b4b; }
    .capa h2.subtitulo { color: #475569; font-weight: 300; margin-top: 0; border: none; font-size: 20pt; }
    .capa .autor { margin-top: 50px; font-size: 14pt; color: #334155; }
    .capa .data { margin-top: 100px; color: #64748b; font-size: 12pt; }
    """
    
    conteudo_html = markdown.markdown(conteudo_md, extensions=['extra'])
    
    # Aplicando classes CSS nas tags geradas
    conteudo_html = conteudo_html.replace('<p><strong>Insight Chave:</strong>', '<p class="insight"><strong>Insight Chave:</strong>')
    conteudo_html = conteudo_html.replace('<p><strong>Decisão Orientada por Dados:</strong>', '<p class="insight"><strong>Decisão Orientada por Dados:</strong>')
    conteudo_html = conteudo_html.replace('<p><strong>Conclusão Financeira:</strong>', '<p class="insight"><strong>Conclusão Financeira:</strong>')
    # Removido o aviso sobre o diagrama Mermaid, permitindo que o código seja exibido como texto pré-formatado.
    
    html_template = f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Gerencial de Roteirização</title>
        <style>{css_style}</style>
    </head>
    <body>
        <!-- Capa do Relatório -->
        <div class="capa">
            <h1>Relatório Gerencial de Roteirização Preditiva</h1>
            <h2 class="subtitulo">Otimização Logística com Inteligência Artificial e Simulação</h2>
            <p class="autor"><strong>Autor:</strong> Eduardo Lopes Jonker</p>
            <p class="autor"><strong>Disciplina:</strong> Sistemas Inteligentes | UDESC</p>
            <div class="data">Gerado em: {agora}</div>
        </div>
        
        {conteudo_html}
    </body>
    </html>
    '''

    nome_arquivo_pdf = f'RELATORIO_GERENCIAL_{timestamp_str}.pdf'
    try:
        HTML(string=html_template, base_url=os.path.abspath('.')).write_pdf(nome_arquivo_pdf)
        print(f"✅ Sucesso! Relatório em PDF '{nome_arquivo_pdf}' gerado com alta qualidade visual.")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível gerar o PDF. Erro: {e}")
        
    print("👉 Abra os arquivos gerados (MD ou PDF) para ver os gráficos e a análise.")

if __name__ == "__main__":
    gerar_relatorio()
