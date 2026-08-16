
# 📊 Relatório Gerencial de Roteirização Preditiva
**Eduardo Lopes Jonker**  
*Disciplina: Sistemas Inteligentes | UDESC*  
*Gerado em: 2026-04-30 11:00:39.569989*

Este documento consolida os resultados do sistema de roteirização preditiva, utilizando inteligência de dados para otimização logística.

---

## 1. Análise Preditiva de Demanda
### 1.1. Projeção de Volume (30 Dias)
!Previsão Geral 30d
**Acurácia (MAPE):** 5.07%

### 1.2. Sazonalidade e Componentes
!Componentes

---

## 2. Otimização de Rotas (IPL)
O **Índice de Prioridade Logística (IPL)** define a urgência das visitas.

!Prioridade IPL
!Contribuição IPL

**Cidade Prioritária:** FLORIANÓPOLIS (IPL: 0.76)

---

## 3. Análise Financeira e ROI
!Comparativo Custos

**Conclusão:** Economia média de **43.61%** em 10,000,000 simulações.

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
