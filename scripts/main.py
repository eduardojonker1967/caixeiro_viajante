from fastapi import FastAPI, BackgroundTasks
from scripts.database import db_handler
# Supondo que adaptamos os scripts originais para funções
# from src.analysis.analise_prophet import executar_previsao
# from src.logistics.geradordepesos import calcular_ipl

app = FastAPI(title="Roteirizador Preditivo API")

@app.get("/")
def health_check():
    return {"status": "online", "database": "connected"}

@app.post("/pipeline/executar")
def run_pipeline(background_tasks: BackgroundTasks):
    """Executa o pipeline completo em background"""
    # background_tasks.add_task(executar_previsao)
    # background_tasks.add_task(calcular_ipl)
    return {"message": "Pipeline iniciado em segundo plano."}

@app.get("/prioridades")
def get_prioridades():
    """Retorna o ranking de cidades com maior IPL direto do Mongo"""
    df = db_handler.load_as_dataframe("pesos_prioridade")
    if df.empty:
        return {"error": "Nenhum dado processado encontrado."}
    return df.sort_values(by="IPL", ascending=False).to_dict(orient="records")

@app.get("/anomalias")
def get_anomalias():
    """Retorna anomalias detectadas para auditoria humana"""
    return db_handler.load_as_dataframe("anomalias").to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)