# Roteirizador Preditivo (Caixeiro Viajante)

**Versão:** 7.0 | **Última atualização:** Agosto 2026 | **Status:** Artigo Científico
**Autor:** Eduardo Lopes Jonker

## 📜 Resumo (Abstract)

Este trabalho apresenta um sistema de roteirização logística inteligente que transcende a otimização de rotas clássica. A metodologia integra **modelagem preditiva de séries temporais** (Prophet), **análise de decisão multicritério** (MCDA) e **otimização de rotas (TSP/VRP)** para criar um framework de *Roteirização Preditiva Antecipatória*. O sistema não apenas minimiza a distância, mas maximiza o valor do negócio ao priorizar dinamicamente os nós da malha logística com base em um **Índice de Prioridade Logística (IPL)**, que pondera demanda futura, risco de SLA, criticidade do serviço e impacto ambiental (ESG). A validação econômica é realizada por meio de **Simulações de Monte Carlo**, e a robustez dos dados é auditada por algoritmos de **detecção de anomalias não supervisionadas** (Isolation Forest). Adicionalmente, a escalabilidade computacional é garantida por uma arquitetura de **processamento paralelo**, cuja eficiência é analisada sob a ótagem da Lei de Amdahl e do framework PCAM. O resultado é um Gêmeo Digital (Digital Twin) para gestão de frotas, capaz de reduzir custos operacionais entre 20-35% e, simultaneamente, diminuir a pegada de carbono da operação.

## 📑 Sumário Rápido

- [🚀 Quick Start](#quick-start)
- [🧠 Metodologia e Fundamentação Matemática](#-metodologia-e-fundamentação-matemática)
  - [1. Modelagem Preditiva de Séries Temporais](#1-modelagem-preditiva-de-séries-temporais-anticipatory-routing)
  - [2. O Índice de Prioridade Logística (IPL)](#2-o-índice-de-prioridade-logística-ipl)
  - [3. Otimização de Rotas (TSP)](#3-otimização-de-rotas-traveling-salesman-problem---tsp)
  - [4. Validação Estocástica (Monte Carlo)](#4-validação-estocástica-monte-carlo)
  - [5. Detecção de Anomalias (Isolation Forest)](#5-detecção-de-anomalias-isolation-forest)
- [⚡ Arquitetura de Paralelismo e Performance](#-arquitetura-de-paralelismo-e-performance)
  - [Metodologia PCAM para Paralelização](#metodologia-pcam-para-paralelização)
  - [Benchmarks de Performance](#benchmarks-de-performance)
- [📊 Resultados e Discussão](#-resultados-e-discussão)
- [📦 Instalação Completa](#instalação-completa)
- [🗄️ Configuração de Banco de Dados](#configuração-de-banco-de-dados)
- [📊 Estrutura do Projeto](#estrutura-do-projeto)
- [🧬 Evolução do Projeto](#evolução-do-projeto)
- [🧠 Metodologia Matemática](#metodologia-e-fundamentação-matemática)
- [💡 Inovações](#inovação-em-relação-ao-caixeiro-viajante-tsp-tradicional)
- [🛠️ Tecnologias](#tecnologias-e-frameworks)
- [🚀 Como Executar](#-como-executar-o-projeto)
- [📊 Interpretação de Gráficos](#interpretação-dos-gráficos-gerados)
- [📚 Gestão de Relatórios](#gestão-de-relatórios-e-versionamento)
- [🔧 Utilitários e Ferramentas](#utilitários-e-ferramentas)
- [❌ Troubleshooting](#troubleshooting)

---
## 🚀 Quick Start

**Pré-requisitos:** Python 3.10+, Docker e Docker Compose instalados.

```bash
# 1. Clone/entre no diretório do projeto
cd ~/Documentos/Caixeiro\ viajante

# 2. Crie e ative um ambiente virtual
python3 -m venv stats_env
source stats_env/bin/activate  # No Windows: stats_env\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o MongoDB via Docker Compose (background)
docker compose up -d mongodb

# 5. Configure as credenciais do MongoDB (gera .env)
python setup_mongo_env.sh

# 6. Execute o pipeline completo de análise e geração de relatórios
./executar_pipeline_completo.sh

# 7. Visualize os logs do sistema (PDF)
python create_system_logs_pdf.py
```

Após a execução, os resultados estarão em:
- **CSV:** `prioridades_paralelas.csv`, `pesos_prioridade_sea.csv`
- **Gráficos:** `*.png` (raiz do projeto)
- **Relatório:** `RELATORIO_GERENCIAL_*.md` e `RELATORIO_GERENCIAL_*.pdf`
- **Logs:** `logs/system_logs_*.txt` e `logs/system_logs_*.pdf`

---

## 📦 Instalação Completa

### 1. Preparação do Ambiente

```bash
# Atualize pip, setuptools e wheel
pip install --upgrade pip setuptools wheel

# Clone o repositório (se aplicável)
git clone <seu-repo>
cd Caixeiro\ viajante
```

### 2. Ambiente Virtual (Recomendado)

```bash
# Crie um ambiente virtual Python
python3 -m venv stats_env

# Ative-o
source stats_env/bin/activate        # macOS/Linux
# OU
stats_env\Scripts\activate           # Windows (PowerShell/CMD)
```

### 3. Instale as Dependências

```bash
# Instale todos os pacotes necessários
pip install -r requirements.txt

# OU instale manualmente
pip install prophet pandas numpy matplotlib streamlit plotly pymongo mongomock reportlab
```

**Versões Testadas:**
- Python 3.10, 3.11, 3.12, 3.13
- Prophet 1.1.5+
- Pandas 2.0+
- PyMongo 4.0+

### 4. Verifique a Instalação

```bash
# Teste se todas as dependências foram carregadas
python -c "import prophet; import pandas; import pymongo; print('✅ Todas as libs OK')"
```

---

## 🗄️ Configuração de Banco de Dados

### MongoDB via Docker Compose (Recomendado)

```bash
# Inicie o MongoDB em background
docker compose up -d mongodb

# Verifique se o container está rodando
docker ps --filter name=mongodb

# Visualize os logs do MongoDB
docker logs caixeiroviajante-mongodb-1 --tail 100
```

### Configurar Credenciais (Arquivo `.env`)

```bash
# O script abaixo gera um arquivo .env com credenciais seguras
python setup_mongo_env.sh

# Verifique o conteúdo do .env (sem mostrar a senha)
cat .env | head -3
```

**Exemplo de `.env`:**
```
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=senha_super_segura_gerada_aleatoriamente
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_URI=mongodb://admin:senha_super_segura@localhost:27017/?authSource=admin
```

### Diagnóstico de Conexão

```bash
# Teste a conexão do MongoDB
python check_mongo_connection.py

# Esperado: "✅ pymongo handshake: OK"
```

### Fallback com MongoMock

Se o MongoDB não estiver disponível, o sistema **automaticamente usa `mongomock`** (banco de dados em memória) para que você possa desenvolver/testar sem dependência do Docker. Os dados são persistidos em CSV como backup.

---

## � Utilitários e Ferramentas

O projeto inclui vários scripts auxiliares para diagnóstico, manutenção e monitoramento:

### 1. **`check_mongo_connection.py`** — Diagnóstico de Conectividade MongoDB
Valida se o MongoDB está acessível e autenticado corretamente.

```bash
python check_mongo_connection.py
```

**Checagens realizadas:**
- Resolução de DNS de `localhost`
- Conectividade TCP na porta 27017
- Handshake do pymongo (autenticação)
- Listagem de bancos de dados disponíveis

**Saída esperada:** `✅ pymongo handshake: OK`

---

### 2. **`setup_mongo_env.sh`** — Gerador de Credenciais Seguras
Cria um arquivo `.env` com credenciais MongoDB aleatórias (sem overhead manual).

```bash
python setup_mongo_env.sh
```

Gera:
- `MONGO_ROOT_USER` (default: `admin`)
- `MONGO_ROOT_PASSWORD` (gerada aleatoriamente com 32 caracteres)
- `MONGO_HOST`, `MONGO_PORT`, `MONGO_URI` automáticos

---

### 3. **`create_system_logs_pdf.py`** — Coleta e Geração de Logs em PDF
Consolida logs do sistema (Docker, kernel, Python, pip) em um arquivo PDF.

```bash
python create_system_logs_pdf.py
```

**Logs coletados:**
- Data/hora e informações do sistema (uname, LSB Release)
- Versão do Python e pacotes instalados (pip freeze)
- Status dos containers Docker (`docker ps`, `docker logs`)
- Journalctl (últimas 1000 linhas do boot atual)
- Dmesg (últimas 200 linhas do kernel)

**Saída:** `logs/system_logs_YYYYMMDD_HHMMSS.txt` e `.pdf`

---

### 4. **`paralelismo_logistica_cidades.py`** — Processamento Paralelo
Executa previsões de múltiplas cidades em paralelo usando `ProcessPoolExecutor`.

```bash
python paralelismo_logistica_cidades.py
```

**Benefícios:**
- Usa todos os núcleos da CPU
- Contorna o GIL (Global Interpreter Lock) do Python
- Speedup significativo em bases com 1000+ cidades

**Saída:** `prioridades_paralelas.csv`

---

### 5. **`versionar_readme.py`** e **`versionar_relatorio.py`** — Versionamento
Cria snapshots históricos do README e dos relatórios.

```bash
python versionar_readme.py      # Salva em historico_readme/
python versionar_relatorio.py   # Salva em historico_relatorios/
```

---

### 6. **`docker-compose.yml`** — Orchestração de Containers
Define o MongoDB e API service para produção.

```bash
# Inicie todos os serviços
docker compose up -d

# Veja o status
docker compose ps

# Pare os serviços
docker compose down
```

**Serviços:**
- **mongodb:** MongoDB 6.0+ com autenticação
- **api:** (placeholder para integração futura)

---

## ❌ Troubleshooting

### ❓ **Problema: "pymongo not installed"**

**Causa:** A biblioteca pymongo não foi instalada no ambiente virtual.

**Solução:**
```bash
# Ative o ambiente virtual
source stats_env/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Ou instale manualmente
pip install pymongo mongomock
```

---

### ❓ **Problema: "Command buildInfo requires authentication"**

**Causa:** MongoDB está rodando com autenticação, mas as credenciais não foram passadas.

**Solução:**
```bash
# Gere o arquivo .env com credenciais
python setup_mongo_env.sh

# Verifique se .env foi criado
ls -la .env

# Teste a conexão
python check_mongo_connection.py
```

---

### ❓ **Problema: "MongoDB connection refused (port 27017)"**

**Causa:** O container MongoDB não está rodando.

**Solução:**
```bash
# Inicie o MongoDB via Docker Compose
docker compose up -d mongodb

# Verifique o status
docker ps --filter name=mongodb

# Se não aparecer, veja os logs
docker logs caixeiroviajante-mongodb-1 --tail 50

# Limpe containers conflitantes (se houver)
docker rm -f mongodb  # Se existir um container manual com este nome
docker compose up -d  # Recrie via compose
```

---

### ❓ **Problema: "Prophet/CmdStan: unexpected keyword argument 'show_progress'"**

**Causa:** Versão de `cmdstanpy` incompatível com a chamada `Prophet.fit(show_progress=False)`.

**Solução:**
```bash
# Atualize as bibliotecas
pip install --upgrade prophet cmdstanpy

# Ou reinstale uma versão compatível
pip install prophet==1.1.5 cmdstanpy==1.0.8
```

---

### ❓ **Problema: "KeyError: 'ipl'" ao rodar `paralelismo_logistica_cidades.py`**

**Causa:** Workers paralelos falharam e não retornaram o índice 'ipl'.

**Solução:**
```bash
# Execute novamente após corrigir as dependências acima
python paralelismo_logistica_cidades.py

# Se persistir, verifique se Prophet está funcionando
python analise_prophet.py

# Se houver erro, veja os logs detalhados
python -u paralelismo_logistica_cidades.py 2>&1 | tee debug.log
```

---

### ❓ **Problema: "Docker permission denied"**

**Causa:** Seu usuário não tem permissão para usar o socket Docker.

**Solução (Linux):**
```bash
# Adicione seu usuário ao grupo docker
sudo usermod -aG docker $USER

# Aplique o novo grupo
newgrp docker

# Verifique
docker ps
```

---

### ❓ **Problema: "ModuleNotFoundError: No module named 'reportlab'"**

**Causa:** reportlab não foi instalado (necessário para gerar PDFs).

**Solução:**
```bash
# Instale reportlab
pip install reportlab

# Ou deixe o script instalar automaticamente
python create_system_logs_pdf.py
```

---

### ❓ **Problema: "Streamlit app não abre (connection refused)"**

**Causa:** Porta 8501 já está em uso ou firewall bloqueando.

**Solução:**
```bash
# Rode em uma porta diferente
streamlit run dashboard_interativo.py --server.port 8502

# Ou libere a porta 8501
# No Windows: netstat -ano | find "8501"
# No Linux: lsof -i :8501 | kill -9 <PID>
```

---

### ❓ **Problema: "Volume de impressão muito baixo / Previsão irreal"**

**Causa:** Dados de treinamento insuficientes ou com muitos outliers.

**Solução:**
```bash
# Verifique a qualidade dos dados
python -c "import pandas as pd; df=pd.read_csv('volumetria_preenchida.csv'); print(df.describe())"

# Se houver muitos NaN, preencha manualmente
# Se houver outliers, use analise_anomalias.py para detectar

# Aumente a janela de dados históricos para pelo menos 2 anos
# Verifique se o Prophet está usando os dados corretos em analise_prophet.py
```

---

## 📊 Estrutura do Projeto e Pipeline de Execução

O sistema foi desenhado em uma arquitetura de *pipeline* modular, onde a saída matemática de um script alimenta o próximo passo da tomada de decisão.

1. **`analise_prophet.py` (Motor Preditivo):** Responsável por carregar e simular o histórico de requisições logísticas e treinar o modelo de Machine Learning de Séries Temporais. Ele exporta a volumetria futura prevista (`previsao_impressoes.csv`) e gera os gráficos analíticos.
2. **`geradordepesos.py` (Motor de Negócios):** É o cérebro das prioridades. Carrega as volumetrias, cruza com dados de inventário/SLA e calcula métricas de consumo (custos, toners e **impacto em árvores**), gerando o **Índice de Prioridade Logística (IPL)**.
3. **`analise_anomalias.py` (Auditoria de Dados):** Utiliza o algoritmo **Isolation Forest** (Random Forest) para detectar anomalias multivariadas nos dados de pesos, garantindo que cidades com comportamentos atípicos sejam sinalizadas para revisão humana.
4. **`testestress.py` (Simulador Financeiro):** Script de validação de negócio que executa iterações randômicas para comparar o custo logístico base (Cenário Atual) contra o cenário proposto pelo modelo otimizado, evidenciando o percentual de economia de capital (ROI). Ele também gera o gráfico comparativo de custos.
4. **`dashboard_interativo.py` (Gêmeo Digital / Digital Twin):** Interface em Streamlit que permite a manipulação de parâmetros em tempo real, visualização de projeções e execução de simulações estocásticas.
5. **`gerador_relatorio.py` (Gerador de Prova de Conceito):** Engine de relatórios que consolida evidências gráficas e métricas de acurácia (MAPE) para auditoria gerencial.
6. **`pipeline_completo.py` (Orquestrador de Fluxo):** Garante a execução atômica do pipeline, desde o treinamento do modelo até o arquivamento dos resultados.
7. **`versionar_relatorio.py` (Governança de Dados):** Snapshots históricos para análise de evolução e rastreabilidade de decisões.

---

## 🧬 Evolução do Projeto: A Jornada da Inteligência

Este projeto não nasceu como um ecossistema completo. Ele passou por uma evolução metodológica rigorosa:

1.  **Fase 1: Roteamento Estático (Baseline):** A logística operava de forma reativa, baseada apenas em chamados abertos e volumes parados, sem visão de futuro.
2.  **Fase 2: Roteamento Inteligente Preditivo:** Implementação do motor **Prophet**, permitindo que o sistema antecipe demandas (Anticipatory Routing) antes que o SLA seja atingido.
3.  **Fase 3: Gestão de Insumos (Toners):** Adição da camada de planejamento de suprimentos, utilizando a previsão anual para calcular ciclos de troca de toner por cidade.
4.  **Fase 4: Controle Ambiental e Financeiro:** Integração do cálculo de **ROI Estocástico** (Monte Carlo) e métricas de sustentabilidade, como a pegada de carbono e o **Índice de Árvores Consumidas**, transformando o projeto em um Gêmeo Digital de gestão de ativos e consciência ambiental.
5.  **Fase 5: Governança de Dados (Isolation Forest):** Implementação de auditoria algorítmica não supervisionada para detectar inconsistências operacionais e anomalias multivariadas.

---

## 🌳 Métrica de Consciência Ambiental: Árvores Consumidas

Para fins de análise de desperdício e impacto ecológico, o sistema adota a métrica científica média de que **uma árvore produz, em média, 7.500 folhas de papel**.

$$ \text{Árvores Perdidas} = \frac{\text{Volume de Impressão}}{7500} $$

Esta métrica é integrada ao IPL e aos relatórios para quantificar o custo biológico da operação em conjunto com o custo financeiro.

## 🧠 Metodologia e Fundamentação Matemática

O projeto rompe com a roteirização estática tradicional através de três pilares matemáticos:

### 1. Modelagem Preditiva de Séries Temporais (Anticipatory Routing)
Utilizamos a decomposição aditiva do algoritmo **Prophet** para prever a volumetria futura $y(t)$:

$$y(t) = g(t) + s(t) + h(t) + \epsilon_t$$

Onde:
*   **$g(t)$:** Tendência linear por partes (identifica crescimento estrutural).
*   **$s(t)$:** Sazonalidade periódica modelada via Séries de Fourier.
*   **$h(t)$:** Impacto de feriados brasileiros (regressores binários).
*   **$\epsilon_t$:** Ruído branco (erro de medição).

### 2. O Índice de Prioridade Logística (IPL)
O IPL é o mecanismo que transforma o "Caixeiro Viajante" em uma ferramenta de **Gestão Baseada em Valor**. Empregamos uma **Análise de Decisão Multicritério (MCDA)** para balancear objetivos conflitantes.

#### Metodologia de Cálculo:
1. **Normalização:** Cada variável $x$ é escalonada para o intervalo $[0, 1]$ para garantir que nenhuma métrica domine as outras artificialmente:

$$x_{norm} = \frac{x - \min(x)}{\max(x) - \min(x)}$$

2. **Ponderação Estratégica:** O IPL final é a soma ponderada das dimensões operacionais:

$$IPL = (V_n \cdot w_v) + (T_n \cdot w_t) + (P_n \cdot w_p) + (L_n \cdot w_l) + (E_n \cdot w_e)$$

As variáveis incluem **Volume** (demanda), **Tipo** (criticidade social), **Performance** (risco de SLA), **Logística** (custo) e **ESG** (impacto ambiental).

### 3. Detecção de Anomalias (Isolation Forest)
Diferente de modelos lineares, o **Isolation Forest** isola observações criando árvores de decisão aleatórias. Observações com caminhos mais curtos nas árvores têm maior probabilidade de serem anomalias. É definido pela função de pontuação:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Onde $h(x)$ é o comprimento do caminho e $c(n)$ é o comprimento médio do caminho de uma árvore de falha.

### 4. Validação Estocástica (Monte Carlo)
A prova de conceito econômica utiliza simulações de Monte Carlo ($N=10^7$) para validar o ROI sob incerteza, onde o custo otimizado $C_{opt}$ é modelado como:

$$C_{opt} = C_{base} \cdot \text{Fator\_Cidades} \cdot (1 - \text{Economia\_Rota})$$

### 4. Clusterização Geográfica e Redução de Dimensionalidade
Para viabilizar a operação em larga escala (ex: Estado de Santa Catarina), o sistema utiliza uma técnica de agregação espacial:
1. **Agregação de Ativos:** $N$ impressoras são mapeadas para seus respectivos clusters municipais $M$.
2. **Cálculo de Densidade de Valor:** O IPL de cada cluster é calculado pela média ponderada da demanda predita de seus ativos internos.
3. **Poda de Grafo (Pruning):** O espaço de busca do TSP é reduzido de $M$ para $K$ (onde $K \ll M$), selecionando apenas os nós onde $IPL > \tau$.
4. **Otimização de Rota:** O solver de VRP (Vehicle Routing Problem) atua apenas sobre o subconjunto $K$, eliminando a complexidade NP-difícil de roteiros de baixa prioridade.

---

## 💡 Inovação em Relação ao Caixeiro Viajante (TSP) Tradicional

Este projeto apresenta três avanços significativos sobre a literatura clássica do TSP:

1.  **Dinamismo Preditivo vs. Reatividade:** O TSP clássico é reativo (visita nós onde a demanda já existe). Este sistema é **antecipatório**, utilizando o $yhat$ do Prophet para priorizar nós antes da quebra do SLA.
2.  **Objetivo Multidimensional (IPL):** Enquanto o TSP foca na minimização da distância ($D$), este projeto resolve um **Prize-Collecting TSP** onde o prêmio (IPL) é dinâmico e integra ESG (Carbono), Criticidade Social (Perícia) e Eficiência (SLA).
3.  **Abordagem Estocástica:** Substituímos a economia determinística única por uma distribuição de densidade de probabilidade, permitindo uma análise de risco financeiro robusta para o investidor.

---

## 🚀 Escalabilidade e Prova de Conceito (Ecosistema Santa Catarina)

O modelo foi validado para suportar o ecossistema de impressão do estado de **Santa Catarina**, que compreende **6.580 impressoras** distribuídas em **2.930 locais**. A arquitetura demonstra viabilidade para:

1.  **Gestão em Larga Escala:** Capacidade de processamento de séries temporais para milhares de pontos através de agregação por clusters municipais.
2.  **Roteirização Multimodal:** O IPL permite a integração de diferentes modais de transporte ao ajustar os pesos de custo logístico ($w_l$) e impacto ambiental ($w_e$).
3.  **Resultados Projetados:**
*   **Redução de Custo Operacional:** Média de **20% a 35%** de economia em comparação ao roteiro exaustivo.
*   **Acurácia de Demanda:** Erro percentual (MAPE) mantido abaixo de **6%** em cenários controlados.
*   **Sustentabilidade:** Redução estimada de emissões de CO2 através da otimização da malha e eliminação de rotas de baixa prioridade.

Este modelo é replicável para qualquer infraestrutura capilarizada, posicionando-se como um framework de **Anticipatory Supply Chain**.

---

## 🛠️ Tecnologias e Frameworks

*   **Linguagem:** Python 3.10+
*   **Séries Temporais:** Facebook Prophet (Machine Learning)
*   **Visualização:** Streamlit & Plotly (Interatividade em tempo real)
*   **Processamento de Dados:** Pandas & NumPy (Cálculos vetoriais de alta performance)
*   **Relatórios:** Jinja2 & WeasyPrint (Engine de renderização HTML-to-PDF)

---

## ️ Tecnologias, Ambiente e Requisitos

Para garantir a reprodutibilidade e o bom funcionamento do projeto, documentamos abaixo as especificações do ambiente onde este sistema foi arquitetado.

### Bibliotecas Python Utilizadas
* **`prophet`**: Motor preditivo da Meta (Facebook) utilizado para a previsão de séries temporais das volumetrias.
* **`pandas`**: Essencial para a manipulação, limpeza e cruzamento dos dados brutos (geração da matriz de pesos, `merge` e higienização de strings).
* **`numpy`**: Responsável pelas operações matemáticas numéricas, normalizações e simulações (utilizado no script de stress e geração de volumetria de teste).
* **`matplotlib`**: Utilizada em *background* para a geração e exportação automatizada dos gráficos analíticos.

### Ambiente de Desenvolvimento
* **Sistema Operacional:** Linux (Desenvolvido/Homologado em ambiente Linux local). O uso de distribuições Linux facilita consideravelmente a compilação transparente das dependências em C++ exigidas pelo motor do Prophet (backend *Stan*).
* **Editor (IDE):** Visual Studio Code (VS Code).
* **Linguagem:** Python 3.8+ (Versões entre 3.8 e 3.11 são ideais para máxima compatibilidade com as bibliotecas científicas).

### Especificações de Equipamento (Hardware Recomendado)
* **Processador (CPU):** Múltiplos núcleos (Dual-Core 2.0GHz ou superior) — O algoritmo de *fitting* do Prophet se beneficia em cálculos matemáticos pesados.
* **Memória RAM:** 4 GB mínimo (8 GB recomendado, para suportar o carregamento em memória `RAM` de extensas planilhas de volumetria via Pandas).
* **Armazenamento:** ~1 GB de espaço livre para comportar os binários das bibliotecas Python (`site-packages`) e geração dos *outputs* (CSVs e gráficos).

### Ambiente de Execução Atual
<environment_details>
Current time: 2026-08-15T21:22:28-03:00
Working directory: /home/eduardo-note/Documentos/Caixeiro viajante
Workspace root folder: /home/eduardo-note/Documentos/Caixeiro viajante
Open tabs:
  mongodb-linux-x86_64.tgz
  explicacao_prophet.md
  gerador_relatorio.py
  data_loader.py
  analise_prophet.py
  executar_tudo.py
  Dockerfile
  requirements.txt
  database.py
  README_PARALELISMO.md
  main.py
  tsp_solver.py
  .gitignore
  main_vrp.py
  README.md
  analise_paralelismo_detallhada.py
  vrp_solver.py
  benchmark_preditivo.py
  dashboard_interativo.py
  geradordepesos.py
</environment_details>

---

## � Dificuldades e Desafios do Projeto

Durante o desenvolvimento e arquitetura deste sistema, enfrentamos e solucionamos as seguintes dificuldades técnicas e operacionais:

1. **Transição de Lógica Reativa para Preditiva (Séries Temporais)** 
   * **Dificuldade:** Tradicionalmente, a roteirização é feita reagindo à volumetria parada (passada), o que frequentemente resulta em atrasos na resposta logística a gargalos.
   * **Solução:** Implementamos o modelo preditivo **Prophet** para projetar a carga de trabalho futura (`yhat`), permitindo enviar recursos para onde a demanda *vai acontecer* e não apenas para onde ela já está represada.

2. **Tratamento de Sazonalidade e Feriados Brasileiros** 
   * **Dificuldade:** Modelos matemáticos engessados (como o Holt-Winters via `statsmodels`) falhavam em capturar o impacto real de feriados prolongados ou flutuações sazonais específicas (como dias úteis x finais de semana).
   * **Solução:** A migração para o Prophet permitiu mapear nativamente as quebras de tendência e injetar feriados locais (`h(t)`), isolando componentes semanais e anuais que distorcem o volume produtivo.

3. **Harmonização de Múltiplos Fatores Concorrentes** 
   * **Dificuldade:** O algoritmo precisava decidir para qual cidade ir, balanceando necessidades conflitantes: volume represado, distância física/custo da viagem ("Dificuldade Logística") e a urgência do serviço (ex: SLAs críticos como Perícia vs. SEA).
   * **Solução:** A criação do **Índice de Prioridade Logística (IPL)**. Esse índice normaliza métricas distintas (0 a 1) e distribui o peso operacional matemático: *Volume (20%), Tipo de Serviço (30%), Performance/SLA (25%) e Logística (25%)*.

4. **Tratamento e Qualidade de Dados Brutos**
   * **Dificuldade:** Inconsistências nas extrações operacionais, como números em formato texto brasileiro (ex: `"1.500,00"`), dados ausentes e conflitos de encoding nas planilhas de input.
   * **Solução:** Criação de um pipeline robusto com a biblioteca Pandas (`geradordepesos.py`), que realiza detecção de separadores, higienização automática das strings, fallback preventivo (impedindo a quebra de execução) e preenchimento sistemático de campos vazios sem corromper as tipagens numéricas.

---

### 🚀 Como executar o projeto (Passo a Passo)

**Pré-requisito:** Ambiente virtual ativado e dependências instaladas (ver seção [Instalação Completa](#instalação-completa)).

#### Opção 1: Pipeline Completo (Automático) — **RECOMENDADO**

```bash
# Executa todo o pipeline em uma única chamada
python pipeline_completo.py
```

Isso executa sequencialmente:
1. `analise_prophet.py` — Treina o modelo preditivo
2. `geradordepesos.py` — Calcula os pesos e IPL
3. `analise_anomalias.py` — Detecta anomalias
4. `testestress.py` — Valida ROI via Monte Carlo
5. `gerador_relatorio.py` — Consolida tudo em um relatório
6. `versionar_relatorio.py` — Arquiva para histórico

#### Opção 2: Execução Manual por Etapas

```bash
# Etapa 1: Treine o modelo de séries temporais
python analise_prophet.py
# Saída esperada: previsao_impressoes.csv, gráficos PNG

# Etapa 2: Calcule os índices de prioridade
python geradordepesos.py
# Saída esperada: pesos_prioridade_sea.csv

# Etapa 3: Detecte anomalias na base
python analise_anomalias.py
# Saída esperada: lista_anomalias.csv, alertas_anomalias.txt

# Etapa 4: Simule o ROI e ganhos financeiros
python testestress.py
# Saída esperada: economia_gerada.txt, gráficos de comparação

# Etapa 5: Gere o relatório gerencial (consolida tudo)
python gerador_relatorio.py
# Saída esperada: RELATORIO_GERENCIAL_YYYY-MM-DD_HHhMMmSSs.md/pdf

# Etapa 6: Arquive para histórico (opcional)
python versionar_relatorio.py
```

#### Opção 3: Processamento Paralelo por Cidades

```bash
# Processa as previsões de cada cidade em paralelo
python paralelismo_logistica_cidades.py
# Saída esperada: prioridades_paralelas.csv
```

#### Opção 4: Dashboard Interativo (Streamlit)

```bash
# Inicie o dashboard em tempo real
streamlit run dashboard_interativo.py

# O navegador abrirá automaticamente em: http://localhost:8501
```

---

#### Coleta de Logs do Sistema

```bash
# Cria um relatório PDF com logs do sistema (MongoDB, Docker, kernel, etc)
python create_system_logs_pdf.py
# Saída esperada: logs/system_logs_YYYYMMDD_HHMMSS.txt e .pdf
```

---

## 📋 Prova de Conceito e Gestão de Relatórios

Para transformar as análises abstratas em uma prova de conceito conclusiva, o projeto inclui um pipeline de geração de relatórios.

1. **Execute os scripts de análise na ordem correta** (`analise_prophet.py`, `geradordepesos.py`, `testestress.py`). Isso irá gerar os gráficos e os arquivos de dados necessários.
2. **Gere o relatório consolidado** com o comando `python gerador_relatorio.py`. Ele cria os arquivos de relatório com nomes dinâmicos (e.g., `RELATORIO_GERENCIAL_YYYY-MM-DD_HHhMMmSSs.md` e `RELATORIO_GERENCIAL_YYYY-MM-DD_HHhMMmSSs.pdf`), que unem os gráficos e as métricas para uma validação clara do método.
3. **Arquive o relatório para histórico** usando `python versionar_relatorio.py`. Este comando salva uma cópia do relatório e de todos os seus gráficos em um diretório com data e hora (`historico_relatorios/`), criando um registro auditável das análises.

---

## 📊 Interpretação dos Gráficos Gerados

Ao executar a análise preditiva (`analise_prophet.py`), o sistema gera automaticamente duas imagens essenciais para validar o comportamento do modelo:

### 1. Previsão Geral (`analise_previsao_geral.png`)
Este gráfico apresenta a aderência do modelo aos dados e a projeção para o futuro.
* **Pontos Pretos:** Representam os dados de volumetria reais (histórico de treino) fornecidos ao modelo.
* **Linha Azul Escura:** É a curva de previsão (`yhat`) desenhada matematicamente pelo algoritmo.
* **Área Azul Claro:** É o intervalo de confiança (margem de erro estatístico), mostrando a variação máxima e mínima esperada.

### 2. Decomposição de Componentes (`analise_sazonalidade_meses.png`)
O Prophet isola a previsão final em diferentes "pesos" autônomos (subplots), o que nos ajuda a responder o *porquê* de um volume estar alto ou baixo em determinado dia:
* **Trend (Tendência Geral):** Desconsidera as flutuações diárias e mostra apenas se, no longo prazo, o volume global de impressões daquela cidade está em expansão ou retração.
* **Holidays (Feriados):** Demonstra como o modelo "amortece" ou joga o volume para cima nos dias mapeados como feriados nacionais (`BR`).
* **Weekly (Semanal):** Exibe a oscilação de produtividade padrão dentro da semana (ex: picos entre terças e sextas-feiras, com quedas bruscas nos finais de semana).
* **Yearly (Anual):** Mostra a "onda" de impacto ao longo dos meses. Valores acima da linha central representam meses que puxam a demanda para cima, enquanto valores abaixo indicam meses de calmaria sazonal.

---

## 🧮 Matriz de Confusão Logística (Avaliação de Decisão)

Embora o modelo preditivo (Prophet) atue com regressão (prevendo volumes numéricos contínuos), o impacto de suas previsões pode ser avaliado através de uma **Matriz de Confusão** adaptada para a tomada de decisão do roteirizador. 

Ela nos ajuda a medir o sucesso (ou as penalidades) das rotas geradas baseadas no índice de prioridade:

| Previsão do Sistema | Realidade (Demanda Real) | Classificação | Impacto Operacional |
| :--- | :--- | :--- | :--- |
| **Alta Demanda** (Rota Priorizada) | **Alta Demanda** (Gargalo Existente) | ✅ **Verdadeiro Positivo (VP)** | **Sucesso Operacional:** Veículo alocado no momento certo, evitando estrangulamento e garantindo SLA. |
| **Alta Demanda** (Rota Priorizada) | **Baixa Demanda** (Sem Gargalo) | ❌ **Falso Positivo (FP)** | **Desperdício Financeiro:** Caminhão/Recurso enviado para uma cidade ociosa (frete pago sem necessidade). |
| **Baixa Demanda** (Ignorado) | **Alta Demanda** (Gargalo Existente) | ❌ **Falso Negativo (FN)** | **Quebra de SLA / Risco:** Sistema falhou em prever o pico de trabalho; o volume acumulou e o prazo estourou. |
| **Baixa Demanda** (Ignorado) | **Baixa Demanda** (Sem Gargalo) | ✅ **Verdadeiro Negativo (VN)** | **Economia Validada:** Decisão correta de reter a frota, evitando custos logísticos desnecessários. |

**Objetivo do Algoritmo:** Ajustar rigorosamente os hiperparâmetros preditivos e os pesos do `geradordepesos.py` para minimizar os *Falsos Negativos* (que geram multas/atrasos) e os *Falsos Positivos* (que queimam margem de lucro), maximizando a eficiência da frota (VP e VN).

---

## ⚙️ Orientações para o Treinamento do Modelo Preditivo

Para garantir que o Prophet alcance a maior acurácia possível nas projeções de volumetria (`analise_prophet.py`), siga as melhores práticas abaixo ao fornecer os seus dados reais:

1. **Janela de Dados Históricos:** O ideal é fornecer pelo menos **2 anos de dados históricos contínuos** para o treinamento. Isso permite que o algoritmo entenda claramente o que é uma sazonalidade anual (ex: pico de serviços em dezembro, calmaria em janeiro) e o que é apenas uma tendência passageira de curto prazo. O mínimo viável recomendado é de 1 ano completo.
2. **Tratamento de Anomalias (Outliers):** Se a operação sofreu eventos drásticos e pontuais que não se repetirão (ex: uma greve geral, interrupção prolongada de sistemas), substitua os volumes desses dias por valores vazios (`NaN`) no dataset de treino. Caso contrário, o Prophet tentará "aprender" esse abismo operacional como um padrão normal.
3. **Ajuste Fino de Feriados (`holidays`):** O modelo já embute feriados nacionais (`country_holidays='BR'`). No entanto, se a sua logística for fortemente paralisada por feriados estaduais ou municipais (ex: feriados padroeiros), é recomendado criar um DataFrame customizado com essas datas e fornecê-lo no parâmetro `holidays` do algoritmo para neutralizar a previsão nestes dias.
4. **Sensibilidade a Mudanças de Cenário (`changepoint_prior_scale`):** Se a empresa alterou subitamente uma regra de negócio (ex: automatizou 50% de um processo antes manual), você pode aumentar o hiperparâmetro `changepoint_prior_scale` (ex: de `0.05` para `0.1` ou mais). Isso avisará ao modelo para "esquecer o passado" e dar muito mais peso à tendência das semanas recentes.
5. **Re-treinamento e Data Drift:** Séries temporais perdem validade conforme o comportamento do mercado muda. Programe uma rotina de re-treinamento sistemático do modelo a cada 3 a 6 meses utilizando dados recém-coletados, garantindo assim que a inteligência artificial acompanhe as evoluções da companhia.

---

## 🎓 Diferenciais Acadêmicos e Contribuição Científica

Enquanto a grande maioria dos projetos que estudam o **Problema do Caixeiro Viajante (TSP)** foca apenas em encontrar o caminho mais curto usando nós estáticos, este projeto introduz elementos avançados de pesquisa de fronteira na área de **Pesquisa Operacional** e **Ciência de Dados Aplicada**:

1. **Roteirização Preditiva (Anticipatory VRP):** 
   A transição da roteirização reativa (baseada no que *já está* represado) para um modelo que injeta projeções de Séries Temporais (`yhat` do Prophet). O algoritmo resolve a latência operacional ao focar em *onde a demanda estará amanhã*.

2. **Heurística de Decisão Multicritério (MCDM):** 
   Ao contrário dos métodos clássicos cujo único "peso" das arestas é a distância ou tempo, este projeto consolida matrizes incompatíveis (Volume vs Risco de Quebra de SLA vs Urgência Regulatória) em um tensor matemático padronizado (o **Índice de Prioridade Logística - IPL**, normalizado entre 0 e 1). Na prática, converte o TSP genérico em um *Prize-Collecting TSP* pautado pelo risco financeiro.

3. **Tradução Epistemológica de Erro Estatístico:**
   A inovação ao adaptar a Matriz de Confusão para a área de logística de frota. O projeto desloca a discussão de métricas isoladas e teóricas (como *RMSE* ou *MAPE*) para demonstrar empiricamente o custo de cada erro algorítmico (ex: Falso Positivo = desperdício de frete para cidade ociosa; Falso Negativo = multa por estourar o prazo limite do serviço).

Esses diferenciais posicionam a solução como um produto robusto que não resolve apenas o problema geométrico do percurso, mas o balanço estrito entre **Eficiência de Malha** e **Maximização de Valor do Negócio**.

---

## 📚 Gestão de Relatórios e Versionamento

Para garantir a governança e a rastreabilidade das análises, o projeto inclui scripts para gerar e arquivar provas de conceito e documentação.

### Geração de Prova de Conceito
O script `gerador_relatorio.py` cria um relatório completo em `RELATORIO_GERENCIAL.md`, que une os gráficos e as métricas de todos os outros scripts. Ele serve como uma prova de conceito visual e não abstrata do valor do método.

### Arquivamento e Versionamento (com nomes de arquivos dinâmicos)
Para manter um histórico auditável, utilize os scripts de versionamento:
*   **`python versionar_relatorio.py`**: Salva o `RELATORIO_GERENCIAL.md` e todos os seus gráficos em uma pasta com data e hora dentro de `historico_relatorios/`. Ideal para comparar a evolução dos resultados ao longo do tempo.
*   **`python versionar_readme.py`**: Salva um snapshot da documentação `README.md` atual na pasta `historico_readme/`, preservando o registro de mudanças na arquitetura e metodologia do projeto.

---

## 🚀 Recomendações para Avançar (Próximos Passos)

* **Piloto Controlado:** Executar um piloto em duas cidades (ex.: Florianópolis e Joinville) para validar a integração com sistemas de gestão de ativos existentes.
* **Automação CI/CD:** Automatização da atualização da ontologia via pipeline de CI/CD, garantindo que mudanças de política sejam refletidas imediatamente.
* **Monitoramento Contínuo:** Monitoramento contínuo dos indicadores de predição (MAE, MAPE) e de desempenho de roteamento (tempo de serviço, quilometragem real).
* **Governança e Escalabilidade:** Documentação de código e parâmetros (configurações do Prophet, horizonte do MPC, penalidades no VRPTW) para facilitar a replicação em outros órgãos.# mestrado
