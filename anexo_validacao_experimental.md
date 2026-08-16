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
