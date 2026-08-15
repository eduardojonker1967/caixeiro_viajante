import sys
import os
import pandas as pd
import time
from datetime import datetime

# Auto-load .env from project root if present (so scripts work without `source .env`)
try:
    from pathlib import Path
    env_path = Path(__file__).resolve().parent / '.env'
    if env_path.exists():
        with env_path.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # don't override existing environment variables
                if k not in os.environ:
                    os.environ[k] = v
except Exception:
    pass

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except (ImportError, ModuleNotFoundError):
    print("❌ ERRO: A biblioteca 'pymongo' não está instalada.")
    print("👉 Solução: No terminal do ambiente (stats_env), execute: pip install pymongo")
    # Encerra a execução de forma limpa, já que o DB é essencial para o pipeline
    sys.exit(1)

class MongoHandler:
    def __init__(self):
        # Prefer explicit MONGO_URI, otherwise build one from credentials if available
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            mongo_user = os.getenv("MONGO_ROOT_USER")
            mongo_pass = os.getenv("MONGO_ROOT_PASSWORD")
            mongo_host = os.getenv("MONGO_HOST", "localhost")
            mongo_port = os.getenv("MONGO_PORT", "27017")
            if mongo_user and mongo_pass:
                mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/?authSource=admin"
            else:
                mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"

        print(f"🔌 Conectando ao MongoDB em: {mongo_uri}")

        # Try to connect with retries/backoff before falling back to mongomock
        max_retries = int(os.getenv("MONGO_CONNECT_RETRIES", "5"))
        base_backoff = float(os.getenv("MONGO_CONNECT_BACKOFF", "2"))
        connected = False
        last_exc = None

        for attempt in range(1, max_retries + 1):
            print(f"   Tentativa {attempt}/{max_retries}...")
            try:
                # Reduzido o timeout para falhar mais rápido em cada tentativa
                self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
                self.client.server_info()  # force immediate validation
                connected = True
                print("✅ Conexão com MongoDB estabelecida com sucesso.")
                break
            except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
                last_exc = exc
                print(f"   ⚠️  Falha na conexão: {exc}")
                if attempt < max_retries:
                    sleep_time = base_backoff * (2 ** (attempt - 1))
                    print(f"   Aguardando {sleep_time}s antes da próxima tentativa...")
                    time.sleep(sleep_time)
        
        if not connected:
            print("❌ Não foi possível conectar ao MongoDB após várias tentativas.")
            print("👉 Tentando fallback: usar um Mongo em memória (mongomock) para desenvolvimento.")
            try:
                import mongomock
                print("⚠️  Usando mongomock (em memória). Dados não serão persistidos entre execuções.")
                self.client = mongomock.MongoClient()
            except Exception as mm_exc:
                print("❌ Falha ao carregar o fallback 'mongomock'.")
                print("👉 Verifique se o MongoDB está rodando ou instale Docker/compose conforme o README.")
                print(f"Detalhes da última falha de conexão: {last_exc}")
                print(f"Detalhes do erro ao tentar o fallback: {mm_exc}")
                sys.exit(1)

        self.db = self.client["roteirizador_db"]

    def save_dataframe(self, df, collection_name):
        """Converte DataFrame para dicionário e salva no Mongo"""
        collection = self.db[collection_name]
        data = df.to_dict(orient="records")
        if data:
            collection.delete_many({}) # Limpa para nova previsão ou faz append dependendo da lógica
            collection.insert_many(data)

    def load_as_dataframe(self, collection_name, query={}):
        """Carrega dados de uma coleção diretamente para um DataFrame"""
        collection = self.db[collection_name]
        data = list(collection.find(query, {"_id": 0}))
        return pd.DataFrame(data)

    def log_anomaly(self, anomaly_data):
        """Registra anomalias detectadas pelo Isolation Forest"""
        self.db["anomalias"].insert_one(anomaly_data)

    def log_pipeline_step(self, run_id, script_name, status, error_msg=None, return_code=None):
        """
        Registra o estado de um passo do pipeline.
        Status: 'STARTED', 'SUCCESS', 'FAILED'
        """
        log_entry = {
            "run_id": run_id,
            "script": script_name,
            "status": status,
            "return_code": return_code,
            "timestamp": datetime.now()
        }
        if error_msg:
            log_entry["error_details"] = error_msg
            
        self.db["pipeline_history"].insert_one(log_entry)

db_handler = MongoHandler()