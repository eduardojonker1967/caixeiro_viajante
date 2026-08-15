# Análise de Séries Temporais com Prophet (Impressões)

O algoritmo **Prophet** (desenvolvido pela equipe do Facebook/Meta) foi escolhido para analisar as séries temporais de impressões das cidades devido à sua robustez para lidar com dados ausentes e mudanças drásticas de tendência.

A ideia central é que o volume de impressões não é estático; ele varia conforme os dias da semana, épocas do ano e feriados. Ao prevermos a volumetria futura (`yhat`), podemos alimentar o **Índice de Prioridade Logística (IPL)** com o volume *esperado* em vez do volume *passado*, tornando o Caixeiro Viajante uma ferramenta de roteirização **preditiva** em vez de reativa.

---

## 🧠 A Fórmula Matemática do Prophet

Diferente dos algoritmos tradicionais como ARIMA, o Prophet utiliza um modelo de decomposição aditiva de séries temporais:

> **y(t) = g(t) + s(t) + h(t) + εt**

### Explicação dos Componentes (Os "Pesos" Internos)

1. **`g(t)` - Peso da Tendência (Trend):** 
   Representa o crescimento ou queda não-periódica do volume de impressões ao longo do tempo. O modelo identifica "pontos de mudança" (*changepoints*) onde a taxa de impressão de uma cidade subitamente aumenta (ex: um novo processo implementado) ou diminui.

2. **`s(t)` - Peso da Sazonalidade (Seasonality):**
   Representa as variações periódicas. O Prophet utiliza a **Série de Fourier** para distribuir pesos a diferentes ciclos:
   - **Semanal:** Identifica que terças e quartas podem ter um pico de peso máximo, enquanto sábados e domingos têm peso negativo ou nulo na produção de impressões.
   - **Anual:** Identifica comportamentos macro, como queda de impressões durante meses tradicionais de férias.

3. **`h(t)` - Peso de Eventos/Feriados (Holidays):**
   Feriados recebem parâmetros próprios. Quando ocorre um feriado (nacional ou municipal inserido no modelo), o Prophet aplica um "peso de correção" para amortecer o volume esperado de impressões naquele momento específico.

4. **`εt` - O Termo de Erro (Ruído):**
   Toda variação que não segue a tendência matemática entra como ruído estatístico. O modelo lida com isso criando o *Intervalo de Confiança* (Upper e Lower bounds).

---

## 🎛️ Configuração dos Pesos Relativos (Hiperparâmetros)

Durante a inicialização da classe `Prophet()`, controlamos o rigor do modelo com os seguintes pesos (priors):

* **`seasonality_prior_scale` (Padrão: 10.0):** 
  Define o quanto a flutuação sazonal influencia a previsão. Se reduzido para `0.1`, o modelo se torna mais rígido, assumindo que as variações nos dias da semana são menos importantes. Em nosso uso, mantemos alto, pois a logística diária é altamente sazonal.

* **`changepoint_prior_scale` (Padrão: 0.05):** 
  Define a sensibilidade do modelo à mudança de tendência. Se a unidade de uma cidade repentinamente dobrar sua capacidade de impressão, um valor maior fará o algoritmo aceitar a nova tendência rapidamente; um valor menor exigirá mais dados para confirmar a mudança.

---

## 📅 O Mês da Implantação Afeta a Tarefa?

Sim! O algoritmo responde diretamente se o mês em que a implantação (ou a execução rotineira) ocorre altera a performance ou o volume de trabalho. Ele faz isso de duas maneiras:

1. **Sazonalidade Anual (`yearly_seasonality`):** O Prophet isola matematicamente o efeito de cada mês. Ao rodar o nosso script atualizado, ele gerará um gráfico chamado `analise_sazonalidade_meses.png`. Na segunda imagem desse arquivo, você verá uma onda anual: valores acima de zero mostram meses que aceleram a execução, e abaixo de zero mostram meses de retração.
2. **Identificação de Quebras de Paradigma (Changepoints):** Se a implantação de um novo sistema (ou a adoção de uma nova política) aconteceu em um mês específico, o Prophet registrará um "Changepoint". A partir dali, a inclinação da reta muda. 

*Dica Avançada:* Se você souber as datas exatas em que uma nova tecnologia ou tarefa foi implantada nas cidades, pode informar explicitamente essas datas na inicialização do Prophet usando o parâmetro `changepoints=['2025-03-15', '2025-08-01']`. Isso força o modelo a verificar se a implantação naqueles meses causou uma mudança drástica no padrão da cidade.

---

## � Integração com o Caixeiro Viajante

A saída principal do modelo Prophet é a coluna **`yhat`** (Volume Predito). 
No momento de calcular a matriz logística de rotas, a variável estática `Volume` da fórmula do **IPL** deve ser substituída pelo `yhat` do dia em que a viagem logística será realizada.

Dessa forma, o veículo será enviado para a cidade que **terá** o maior volume represado, antecipando o gargalo operacional e garantindo o máximo aproveitamento do frete.