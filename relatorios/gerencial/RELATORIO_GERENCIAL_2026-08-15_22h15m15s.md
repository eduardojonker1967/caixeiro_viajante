
# 📄 Relatório Científico Automatizado: Roteirização Preditiva

**Autor:** Eduardo Lopes Jonker  
**Data de Geração:** 2026-08-15 22:15:15.421264

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

**Acurácia (MAPE):** 5.18% (Erro Percentual Médio).

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

Para validar o impacto financeiro, uma simulação de Monte Carlo com $N=1,000,000$ iterações foi executada. A simulação compara o custo operacional de um cenário "reativo" com o custo do modelo preditivo otimizado.

![Comparativo Custos](relatorio_comparativo_custos.png)
*Gráfico 3: Distribuição de probabilidade de custos, comparando o cenário atual com o modelo otimizado.*

**Conclusão Financeira:** A simulação indica uma economia média esperada de **43.61%** no custo operacional logístico.

### 4.2. Auditoria de Dados com Isolation Forest

O sistema utiliza o algoritmo **Isolation Forest** para auditar a integridade dos dados e detectar comportamentos atípicos que poderiam distorcer a priorização.

![Anomalias Forest](analise_anomalias.png)
*Gráfico 4: Detecção de anomalias no cruzamento de Volume vs. IPL.*

**Resultado da Auditoria:** O algoritmo Isolation Forest identificou 2 cidades com comportamento atípico no cruzamento de Volume vs Logística.

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



---

# Anexo Técnico: Validação Experimental Completa

**Data de geração:** 2026-08-15 21:58:21  
**Autor:** Eduardo Lopes Jonker  
**Projeto:** Roteirizador Preditivo — Caixeiro Viajante

---

## 1. Seeds e Resultados Individuais (SA e AG)

Foram executadas 30 seeds para Simulated Annealing (SA) e 30 seeds para Algoritmo Genético (AG), totalizando 60 execuções. A lista completa está em `anexo_seeds_sa_ag.csv`.

**Parâmetros dos métodos:**
- SA: temperatura inicial=1000, taxa de resfriamento=0.995, max_iter=10000
- AG: pop_size=60, elite_size=15, mutation_rate=0.02, generations=500

---

## 2. Benchmark de Solvers e Gap para o Ótimo

A Tabela 1 compara os algoritmos contra a melhor heurística (ótimo local de referência).

| Solver | Distância (km) | Gap vs ótimo (%) |
|:-------|---------------:|-----------------:|
| Aleatória | 3501.27 | 141.45% |
| NN | 1450.11 | 0.00% |
| 2-opt | 1450.11 | 0.00% |
| SA | 1462.74 | 0.87% |
| AG | 1455.50 | 0.37% |

Ótimo local de referência: **1450.11 km** (melhor heurística para 18 nós).

---

## 3. Estatísticas Completas por Método

A Tabela 2 resume as estatísticas das 30 execuções por método.

| Método | N | Média (km) | Mediana (km) | Melhor (km) | Pior (km) | DP (km) | CV (%) | IC 95% | Tempo médio (s) |
|:---|---:|---:|---:|---:|---:|---:|---:|:---|---:|
| SA | 30 | 1461.35 | 1459.19 | 1430.76 | 1520.94 | 22.54 | 1.54 | [1453.28, 1469.41] | 0.0714 |
| AG | 30 | 1525.36 | 1514.02 | 1443.61 | 1741.11 | 69.86 | 4.58 | [1500.36, 1550.35] | 0.6560 |

---

## 4. Validação Longitudinal (10 Ciclos)

Foram simulados 10 ciclos operacionais, comparando baseline real (rota aleatória) vs modelo otimizado (2-opt). A Tabela 3 apresenta os resultados.

| Ciclo | Baseline (km) | Modelo (km) | Redução (%) |
|:------|--------------:|------------:|------------:|
| 1.0 | 4008.92 | 1450.11 | 63.83% |
| 2.0 | 3626.90 | 1450.11 | 60.02% |
| 3.0 | 2983.67 | 1450.11 | 51.40% |
| 4.0 | 3724.10 | 1450.11 | 61.06% |
| 5.0 | 3263.22 | 1450.11 | 55.56% |
| 6.0 | 3447.01 | 1450.11 | 57.93% |
| 7.0 | 3176.04 | 1450.11 | 54.34% |
| 8.0 | 3472.08 | 1450.11 | 58.24% |
| 9.0 | 3325.81 | 1450.11 | 56.40% |
| 10.0 | 2853.75 | 1450.11 | 49.19% |

Redução média: **56.80%**  
Desvio padrão: **4.42%**

---

## 5. Origem das Distâncias

As distâncias entre as 18 cidades de Santa Catarina foram calculadas a partir das coordenadas geográficas (latitude/longitude) de cada município, utilizando a fórmula de Haversine para obter a distância geodésica em quilômetros (raio terrestre = 6371 km). Essa matriz representa a distância de percurso mais curta entre pares de cidades, independentemente de modo de transporte ou condição de tráfego. Data de referência: 2026-08-15 21:58:21.

---

## 6. Reprodutibilidade

- **Semente global:** 42
- **Seeds SA:** 1 a 30
- **Seeds AG:** 1 a 30
- **Arquivo de sementes:** `anexo_seeds_sa_ag.csv`
- **Benchmark de solvers:** `anexo_benchmark_solvers.csv`
- **Validação multi-ciclo:** `anexo_validacao_ciclos.csv`
- **Estatísticas:** `anexo_estatisticas_sa_ag.csv`
- **Origem das distâncias:** `anexo_origem_distancias.json`

---

*Documento gerado automaticamente pelo sistema de validação experimental.*
