
# 📊 Relatório Gerencial de Roteirização Preditiva
*Relatório gerado em: 28/04/2026 às 05:06:39*

Este documento consolida os resultados do sistema de roteirização preditiva, oferecendo uma prova de conceito visual e quantitativa da metodologia aplicada. O objetivo é fornecer uma visão conclusiva e menos abstrata sobre a otimização logística.

---

## 1. Análise Preditiva de Demanda (Prophet)

A primeira etapa consiste em prever a volumetria de impressões para os próximos 30 dias. Isso transforma nossa logística de reativa para **preditiva**.

### 1.1. Projeção de Volume Futuro

O gráfico abaixo mostra a tendência de volume projetada (`yhat`) em azul, com base nos dados históricos (pontos pretos). A área sombreada representa o intervalo de confiança da previsão.

!Previsão Geral de Volume

**Insight Chave:** O volume total de impressões esperado para os próximos 30 dias é de **50,353 unidades**.

### 1.2. Decomposição e Análise de Sazonalidade

Para entender *por que* o volume flutua, o modelo decompõe a série temporal em seus componentes: tendência, feriados e sazonalidade semanal/anual.

!Componentes do Modelo Prophet

**Insight Chave:** O gráfico de sazonalidade anual (`Yearly`) nos permite identificar os meses de alta e baixa demanda, auxiliando no planejamento estratégico de recursos e férias da equipe.

---

## 2. Prova de Conceito: Priorização de Rotas (IPL)

Com a previsão em mãos, o "Motor de Negócios" calcula o **Índice de Prioridade Logística (IPL)**. Este índice determina qual cidade deve ser visitada com maior urgência, balanceando volume, criticidade do serviço, performance e custo logístico. O gráfico abaixo demonstra a prova de conceito da priorização, exibindo as cidades com maior IPL.

!Gráfico de Prioridade IPL

**Decisão Orientada por Dados:** A cidade com maior prioridade para a próxima rota é **FLORIANÓPOLIS**, com um IPL de **0.76**.

---

## 3. Análise de Viabilidade Financeira (ROI)

Para validar o método, um teste de estresse compara o custo logístico do cenário atual com o custo obtido pelo modelo de roteirização otimizado. O gráfico de densidade abaixo ilustra a distribuição de custos em 1.000 simulações, provando o conceito de economia.

!Comparativo de Custos

**Conclusão Financeira:** O modelo preditivo demonstra uma **redução de custos consistente**, deslocando a curva de gastos para a esquerda. A economia média gerada nas simulações valida o retorno sobre o investimento (ROI) da implementação deste sistema.
