import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import logging
import sys
import subprocess
from database import db_handler

# Configuração da Página
st.set_page_config(page_title="Dashboard Roteirização Preditiva", layout="wide")

# Verificação de dependência do Prophet (necessário após set_page_config)
try:
    from prophet import Prophet
except ImportError:
    st.error("❌ Erro: A biblioteca 'prophet' não está instalada.")
    st.info("👉 Solução: No terminal, execute: `pip install prophet`")
    st.stop()

st.title("📊 Dashboard de Roteirização Inteligente (Digital Twin)")
st.markdown("---")

# --- ESTILO CUSTOMIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
    .stSidebar { background-color: #1e293b; color: white; }
    .stButton>button { background-color: #4f46e5; color: white; border-radius: 8px; width: 100%; border: none; height: 3em; }
    .stButton>button:hover { background-color: #4338ca; border: none; color: white; }
    h1, h2, h3 { color: #1e1b4b; }
    div[data-baseweb="tab-list"] { gap: 20px; }
    button[data-baseweb="tab"] { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Configurações e Parâmetros ---
st.sidebar.header("🕹️ Controle de Dados")

if st.sidebar.button("🚀 Rodar Pipeline Completo"):
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    try:
        status_text.text("Preparando ambiente...")
        progress_bar.progress(10)
        
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_pipeline = os.path.join(diretorio_atual, "pipeline_completo.py")
        
        status_text.text("Executando modelos e cálculos (isso pode levar um tempo)...")
        progress_bar.progress(40)
        
        # Execução com captura de saída para evitar travamentos
        processo = subprocess.Popen(
            [sys.executable, caminho_pipeline],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = processo.communicate()
        if processo.returncode != 0:
            st.sidebar.error("❌ Falha na execução do pipeline.")
            with st.expander("Ver detalhes do erro"):
                st.code(stderr)
            st.stop()
        
        progress_bar.progress(100)
        st.cache_data.clear()
        st.sidebar.success("✅ Dados sincronizados!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"❌ Erro: {e}")
    finally:
        progress_bar.empty()
        status_text.empty()

st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Histórico do Pipeline")
try:
    # Busca os últimos 5 logs de passos do pipeline no MongoDB
    df_logs = db_handler.load_as_dataframe("pipeline_history")
    if not df_logs.empty:
        df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
        df_logs = df_logs.sort_values("timestamp", ascending=False).head(5)
        for _, log in df_logs.iterrows():
            status_map = {"SUCCESS": "✅", "FAILED": "❌", "STARTED": "⏳"}
            emoji = status_map.get(log['status'], "❓")
            st.sidebar.caption(f"{emoji} **{log['script']}**")
            st.sidebar.caption(f"_{log['timestamp'].strftime('%d/%m %H:%M:%S')}_")
    else:
        st.sidebar.info("Nenhum log encontrado.")
except Exception as e:
    st.sidebar.error("Erro ao carregar histórico.")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Pesos do IPL (Prioridade)")

w_vol = st.sidebar.slider("Peso Volume (%)", 0, 100, 15, help="Prioriza cidades com maior volume previsto de impressões.") / 100
w_tipo = st.sidebar.slider("Peso Tipo de Serviço (%)", 0, 100, 25, help="Diferencia criticidade (ex: Perícias vs. SEA).") / 100
w_perf = st.sidebar.slider("Peso Performance (%)", 0, 100, 20, help="Dá mais peso para cidades com baixo cumprimento de SLA.") / 100
w_log = st.sidebar.slider("Peso Logística (%)", 0, 100, 20, help="Considera distância e custo de deslocamento.") / 100
w_carb = st.sidebar.slider("Peso ESG (Carbono) (%)", 0, 100, 20, help="Penaliza rotas com alta pegada de carbono.") / 100

if round(w_vol + w_tipo + w_perf + w_log + w_carb, 2) != 1.0:
    st.sidebar.warning(f"⚠️ A soma dos pesos é {int(round(w_vol+w_tipo+w_perf+w_log+w_carb, 2)*100)}%. O ideal é 100%.")

st.sidebar.subheader("Previsão")
forecast_days = st.sidebar.number_input("Dias de Previsão", min_value=7, max_value=365, value=30)

st.sidebar.subheader("Simulação ROI")
mc_iterations = st.sidebar.select_slider("Iterações Monte Carlo", options=[1000, 10000, 100000], value=10000)

st.sidebar.subheader("💰 Gestão Financeira de Impressão")
p_preto = st.sidebar.number_input("Preço Preto (R$)", value=0.02, step=0.01)
p_color = st.sidebar.number_input("Preço Color (R$)", value=0.10, step=0.01)
mix_color_pct = st.sidebar.slider("Mix Colorido (%)", 0, 100, 15) / 100

# --- FUNÇÕES DE DADOS (Adaptadas dos scripts originais) ---
@st.cache_data
def load_historical_data():
    arquivo_hist = 'historico_impressoes.csv'
    if os.path.exists(arquivo_hist):
        df = pd.read_csv(arquivo_hist)
        df['ds'] = pd.to_datetime(df['ds'])
        return df
        
    # Fallback para simulação
    np.random.seed(42)
    datas = pd.date_range(end=pd.Timestamp.now().floor('D'), periods=365)
    y = 1200 + np.linspace(0, 500, 365) + np.sin(np.arange(365) * (2 * np.pi / 7)) * 300 + np.random.normal(0, 100, 365)
    return pd.DataFrame({'ds': datas, 'y': y.clip(0)})

@st.cache_data
def run_forecast(df, periods):
    logging.getLogger('prophet').setLevel(logging.ERROR)
    logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
    m = Prophet(yearly_seasonality=True, weekly_seasonality=True)
    m.add_country_holidays(country_name='BR')
    m.fit(df)
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    return m, forecast

@st.cache_data
def calculate_ipl(w_v, w_t, w_p, w_l, w_c, p_preto, p_color, mix_color):
    arquivo_vol = 'volumetria_preenchida.csv'
    
    def normalizar(serie, inverter=False):
        s_min, s_max = serie.min(), serie.max()
        if s_max == s_min: return serie * 0 + 0.5
        norm = (serie - s_min) / (s_max - s_min)
        return 1 - norm if inverter else norm

    if os.path.exists(arquivo_vol):
        df = pd.read_csv(arquivo_vol, sep=';', encoding='utf-8')
        df['Cidade'] = df['Cidade'].astype(str).str.upper().str.strip()
    else:
        cidades = ['SÃO PAULO', 'RIO DE JANEIRO', 'BELO HORIZONTE', 'CURITIBA', 'PORTO ALEGRE']
        df = pd.DataFrame({
            'Cidade': cidades,
            'Volume': np.random.randint(400, 1600, len(cidades)),
            'Tipo': np.random.choice(['PERICIA', 'SEA'], len(cidades))
        })
    
    # Normalizações
    df['Vol_Norm'] = normalizar(df['Volume'])
    df['Perf_Norm'] = normalizar(df['Performance'], inverter=True)
    df['Log_Norm'] = normalizar(df['Logistica'])
    # Garante colunas mínimas para simulação de score se não existirem
    if 'Performance' not in df.columns: df['Performance'] = np.random.uniform(0.6, 0.95, len(df))
    if 'Logistica' not in df.columns: df['Logistica'] = np.random.uniform(50, 300, len(df))
    if 'Carbono' not in df.columns: df['Carbono'] = df['Logistica'] * np.random.uniform(0.12, 0.18, len(df))

    df['Carb_Norm'] = normalizar(df['Carbono'])
    df['Peso_Tipo'] = df['Tipo'].apply(lambda x: 1.5 if x == 'PERICIA' else 1.0)
    
    # Gestão de Consumo no Dashboard
    unit_cost = (1 - mix_color) * p_preto + mix_color * p_color
    df['Custo_Pagina'] = unit_cost
    df['Custo_Estimado'] = df['Volume'] * unit_cost
    df['Vol_PB'] = (df['Volume'] * (1 - mix_color)).astype(int)
    df['Vol_Color'] = (df['Volume'] * mix_color).astype(int)
    df['Tipo_Norm'] = normalizar(df['Peso_Tipo'])
    
    # Cálculo IPL
    df['IPL'] = (df['Vol_Norm'] * w_v) + (df['Tipo_Norm'] * w_t) + (df['Perf_Norm'] * w_p) + (df['Log_Norm'] * w_l) + (df['Carb_Norm'] * w_c)
    return df.sort_values('IPL', ascending=False)

# --- EXECUÇÃO E LAYOUT ---

tab1, tab2, tab3 = st.tabs(["📈 Previsão de Demanda", "🎯 Priorização (IPL)", "💰 Simulação de Custos"])

with tab1:
    st.subheader("Análise Preditiva de Volumetria")
    df_hist = load_historical_data()
    model, forecast = run_forecast(df_hist, forecast_days)
    
    # Gráfico Plotly para Interatividade
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=df_hist['ds'], y=df_hist['y'], name="Histórico", mode='markers', marker=dict(color='black', size=4)))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Previsão", line=dict(color='#3498db')))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='rgba(0,176,246,0)', showlegend=False))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(0,176,246,0)', fillcolor='rgba(0,176,246,0.2)', name="Confiança"))
    
    st.plotly_chart(fig_forecast, width='stretch')
    
    col1, col2, col3 = st.columns(3)
    total_v = forecast.tail(forecast_days)['yhat'].sum()
    with col1:
        st.metric("Total Previsto (Período)", f"{int(total_v):,}")
    with col2:
        st.metric("Média Diária", f"{forecast.tail(forecast_days)['yhat'].mean():.2f}")
    with col3:
        st.metric("🌳 Árvores Consumidas", f"{total_v / 7500:.2f}")

with tab2:
    st.subheader("Ranking de Prioridade por Cidade")
    df_ipl = calculate_ipl(w_vol, w_tipo, w_perf, w_log, w_carb, p_preto, p_color, mix_color_pct)
    
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        fig_ipl = px.bar(df_ipl, x='IPL', y='Cidade', orientation='h', 
                         color='IPL', color_continuous_scale='Viridis',
                         title="Top Cidades por Índice de Prioridade Logística")
        fig_ipl.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_ipl, width='stretch')
        
    with col_data:
        st.write("Dados de Priorização")
        # Exibição da Tabela Comparativa de Custos
        cols_financeiras = ['Cidade', 'Volume', 'Custo_Pagina', 'Custo_Estimado']
        st.dataframe(
            df_ipl[cols_financeiras]
            .style.format({'Custo_Pagina': 'R$ {:.3f}', 'Custo_Estimado': 'R$ {:.2f}'})
            .background_gradient(subset=['Custo_Estimado'], cmap='YlOrRd')
        )

    # Decomposição do IPL
    st.subheader("Contribuição por Fator")
    df_ipl_long = df_ipl.head(5).melt(id_vars='Cidade', value_vars=['Vol_Norm', 'Tipo_Norm', 'Perf_Norm', 'Log_Norm', 'Carb_Norm'], 
                                     var_name='Fator', value_name='Score')
    fig_stack = px.bar(df_ipl_long, x='Cidade', y='Score', color='Fator', barmode='stack')
    st.plotly_chart(fig_stack, width='stretch')

with tab3:
    st.subheader("Simulação de Economia (Monte Carlo)")
    
    progress_bar_mc = st.progress(0)
    status_mc = st.empty()
    
    # Simulando processamento em blocos para mostrar a barra de progresso
    chunk_size = mc_iterations // 10
    custo_atual_list = []
    custo_modelo_list = []
    
    for i in range(10):
        status_mc.text(f"Calculando iterações: {((i+1)*chunk_size):,} / {mc_iterations:,}")
        c_atual = np.random.uniform(500, 800, chunk_size)
        e_rota = np.random.uniform(0.20, 0.35, chunk_size)
        
        custo_atual_list.append(c_atual)
        custo_modelo_list.append(c_atual * (14/18) * (1 - e_rota))
        progress_bar_mc.progress((i + 1) * 10)

    custo_atual = np.concatenate(custo_atual_list)
    custo_modelo = np.concatenate(custo_modelo_list)
    
    progress_bar_mc.empty()
    status_mc.empty()
    
    fig_mc = go.Figure()
    fig_mc.add_trace(go.Histogram(x=custo_atual, name='Cenário Atual', marker_color='#e74c3c', opacity=0.6))
    fig_mc.add_trace(go.Histogram(x=custo_modelo, name='Cenário Otimizado', marker_color='#2ecc71', opacity=0.6))
    
    fig_mc.update_layout(barmode='overlay', title="Distribuição Probabilística de Custos",
                         xaxis_title="Custo Estimado (R$)", yaxis_title="Frequência")
    
    st.plotly_chart(fig_mc, width='stretch')
    
    avg_economia = (1 - custo_modelo.mean() / custo_atual.mean()) * 100
    
    st.success(f"### 💰 Economia Média Estimada: {avg_economia:.2f}%")
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Custo Médio Atual", f"R$ {custo_atual.mean():.2f}")
    col_res2.metric("Custo Médio Otimizado", f"R$ {custo_modelo.mean():.2f}")

# Rodapé
st.markdown("---")
st.caption(f"Dashboard gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Eduardo Lopes Jonker")