# Apresentação da Proposta - Trabalho de Paralelismo
## Otimização de Rotas de Logística com TSP Paralelo

---

## Slide 1: Problema

**Problema:** Otimização de rotas logísticas para atendimento de 18 cidades em Santa Catarina

**Contexto:**
- 6.580 impressoras em 2.930 locais
- Necessidade de redução de custos de deslocamento
- Caixeiro Viajante (TSP) é NP-difícil - O(n!)

---

## Slide 2: Abordagem PCAM

### P - Particionamento
```
Unidade: geração de rota aleatória única
Decomposição: 10.000 seeds → 10.000 rotas independentes
Padrão: embarrassingly parallel
```

### C - Comunicação
```
Dados compartilhados: matriz_dist (read-only, ~3KB)
Dados privados: seed, rota, distância
Comunicação: Scatter-Gather (zero durante processamento)
```

### A - Agrupamento
```
Chunksize: 100 iterações por lote
Overhead: redução de 15% → 3%
IPC otimizado: 100 mensagens vs 10.000
```

### M - Mapeamento
```
Workers: multiprocessing.cpu_count() (12 CPUs)
Política: Round-robin + work-stealing
Escalabilidade: linear até overhead dominar
```

---

## Slide 3: Implementação

**Serial:**
```python
for seed in range(10000):
    rota = gerar_rota_aleatoria(matriz_dist, seed)
    # processa 1 rota de cada vez
```

**Paralelo:**
```python
with ProcessPoolExecutor(max_workers=12) as executor:
    args = [(seed, matriz_dist) for seed in range(10000)]
    resultados = executor.map(gerar_rota_worker, args, chunksize=100)
```

---

## Slide 4: Métricas Esperadas

| Iterações | Serial (s) | Paralelo (s) | Speedup |
|-----------|------------|--------------|---------|
| 1,000     | ~0.05      | ~0.10        | 0.5x    |
| 10,000    | ~0.25      | ~0.15        | 1.7x    |
| 100,000   | ~1.20      | ~0.22        | **5.6x** |
| 1,000,000 | ~12.0      | ~2.5         | **4.8x** |

---

## Slide 5: Cronograma

- **03/06**: Proposta + Slides da PCAM
- **10/06**: Implementação do TSP paralelo
- **17/06**: Testes + Benchmarks + PDF
- **24/06**: Apresentação (10 min)