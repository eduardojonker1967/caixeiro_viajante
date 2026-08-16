
# 📊 Relatório Gerencial de Roteirização Preditiva
*Relatório gerado em: 28/04/2026 às 07:03:58*

Este documento consolida os resultados do sistema de roteirização preditiva, oferecendo uma prova de conceito visual e quantitativa da metodologia aplicada. O objetivo é fornecer uma visão conclusiva e menos abstrata sobre a otimização logística.

---

## 1. Análise Preditiva de Demanda (Prophet)

A primeira etapa consiste em prever a volumetria de impressões para os próximos 30 dias. Isso transforma nossa logística de reativa para **preditiva**.

### 1.1. Projeção de Volume Futuro

O gráfico abaixo mostra a tendência de volume projetada (`yhat`) em azul, com base nos dados históricos (pontos pretos). A área sombreada representa o intervalo de confiança da previsão.

![Previsão Geral de Volume](analise_previsao_geral.png)

**Insight Chave:** O volume total de impressões esperado para os próximos 30 dias é de **50,353 unidades**.

### 1.2. Decomposição e Análise de Sazonalidade

Para entender *por que* o volume flutua, o modelo decompõe a série temporal em seus componentes: tendência, feriados e sazonalidade semanal/anual.

![Componentes do Modelo Prophet](analise_sazonalidade_meses.png)

**Insight Chave:** O gráfico de sazonalidade anual (`Yearly`) nos permite identificar os meses de alta e baixa demanda, auxiliando no planejamento estratégico de recursos e férias da equipe.

---

## 2. Prova de Conceito: Priorização de Rotas (IPL)

Com a previsão em mãos, o "Motor de Negócios" calcula o **Índice de Prioridade Logística (IPL)**. Este índice determina qual cidade deve ser visitada com maior urgência, balanceando volume, criticidade do serviço, performance e custo logístico. O gráfico abaixo demonstra a prova de conceito da priorização, exibindo as cidades com maior IPL.

!Gráfico de Prioridade IPL

![Gráfico de Prioridade IPL](relatorio_prioridade_ipl.png)

---

## 3. Análise de Viabilidade Financeira (ROI)

Para validar o método, um teste de estresse compara o custo logístico do cenário atual com o custo obtido pelo modelo de roteirização otimizado. O gráfico de distribuição estatística abaixo ilustra a simulação de Monte Carlo com **1.000.000 de iterações**, provando o conceito de economia.

![Comparativo de Custos](relatorio_comparativo_custos.png)

**Decisão Orientada por Dados:** A cidade com maior prioridade para a próxima rota é **FLORIANÓPOLIS**, com um IPL de **0.76**.


## 4. Detalhamento Técnico e Arquitetura (Digital Twin)

O sistema atua como um **Digital Twin** (Gêmeo Digital) da operação logística, simulando as condições de contorno matemáticas antes de despachar a frota física.

### 4.1. Diagrama de Fluxo do Digital Twin

```mermaid
graph TD
    A[Dados Históricos ERP] -->|Séries Temporais| B(Motor Preditivo: Prophet)
    B -->|Previsão de Demanda| C[Motor de Regras: Negócios]
    C -->|Variáveis Críticas| D[Cálculo do IPL]
    D -->|Normalização| E[Matriz de Prioridades]
    E --> F((Solucionador MPC / VRP))
    F --> G[Restrição de Malha Otimizada]
    G --> H[Simulador Monte Carlo]
    H -->|Cálculo de Risco/ROI| I[Decisão de Despacho]
    
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
```

### 4.2. Parâmetros do Motor Preditivo (Prophet)
- **`seasonality_prior_scale`**: `10.0` (Garante alta flexibilidade para capturar oscilações rápidas de produtividade na semana).
- **`changepoint_prior_scale`**: `0.05` (Balanço conservador para identificar quebras estruturais de tendência).
- **Feriados Locais**: Injeção nativa de calendário (`country_holidays='BR'`) para amortecer quedas de volumetria.

### 4.3. Configuração do MPC (Model Predictive Control) e VRP
O controlador preditivo consome o **Índice de Prioridade Logística (IPL)** para resolver o problema *Prize-Collecting VRP* via heurística do OR-Tools:
- **Função Objetivo**: Minimizar custo global x Maximizar cobertura de nós urgentes.
- **Restrição de Janela**: O solver restringe a malha dinâmica isolando apenas as principais cidades prioritárias (ex: 14 das 18 unidades), maximizando a alocação de frota.

---

## 5. Informações do Ambiente e Hardware

Detalhes do ambiente de execução e recomendações de hardware para o projeto.

### 5.1. Ambiente de Execução
- **Sistema Operacional:** `Linux 6.14.0-15-generic (#15-Ubuntu SMP PREEMPT_DYNAMIC Sun Apr  6 15:05:05 UTC 2025)`
- **Arquitetura da Máquina:** `x86_64`
- **Versão do Python:** `3.13.11`
- **Nome do Host:** `eduardonote-Inspiron-15-3530`

### 5.2. Recomendações de Hardware
Para garantir a performance ideal do sistema, especialmente para o treinamento do modelo Prophet e manipulação de grandes volumes de dados com Pandas, as seguintes especificações de hardware são recomendadas:
- **Processador (CPU):** Múltiplos núcleos (Dual-Core 2.0GHz ou superior) — O algoritmo de *fitting* do Prophet se beneficia em cálculos matemáticos pesados.
- **Memória RAM:** 4 GB mínimo (8 GB recomendado, para suportar o carregamento em memória `RAM` de extensas planilhas de volumetria via Pandas).
- **Armazenamento:** ~1 GB de espaço livre para comportar os binários das bibliotecas Python (`site-packages`) e geração dos *outputs* (CSVs e gráficos).

---

## Apêndice: Código-Exemplo (Open Repository)

Trecho base da arquitetura do Motor de Prioridade Multicritério:

```python
# Cálculo Estrito do Índice de Prioridade Logística (IPL)
df['IPL'] = (
    (df['Volume_Norm'] * 0.20) +     # Necessidade de Vazão Quantitativa
    (df['Peso_Tipo'] * 0.30) +       # Criticidade Regulatória (Perícia = 1.5)
    (df['Perf_Norm'] * 0.25) +       # Risco de Rompimento de SLA
    (df['Logistica_Norm'] * 0.25)    # Custo / Dificuldade de Deslocamento
)
```
*Nota: O código-fonte do pipeline é modular e os scripts integrais (.py) estão disponíveis no repositório logístico central para auditoria.*
