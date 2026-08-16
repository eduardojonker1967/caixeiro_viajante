#!/usr/bin/env python3
"""
Reorganiza o projeto Caixeiro Viajante seguindo estrutura profissional.
CUIDADO: Este script move arquivos. Execute com o projeto commitado no git.
"""

import os
import shutil
from pathlib import Path

BASE = Path('.')

# Estrutura alvo
FOLDERS = [
    'src/analysis',
    'src/optimization',
    'src/logistics',
    'src/simulation',
    'src/visualization',
    'src/reporting',
    'src/infra',
    'tests',
    'docs',
    'data/raw',
    'data/processed',
    'scripts',
    'relatorios',
    'imagens',
]

for folder in FOLDERS:
    (BASE / folder).mkdir(parents=True, exist_ok=True)

# Mapeamento de arquivos -> destino
MOVES = {
    # Análise
    'analise_prophet.py': 'src/analysis/',
    'analise_anomalias.py': 'src/analysis/',
    'analise_paralelismo_detallhada.py': 'src/analysis/',
    'benchmark_preditivo.py': 'src/analysis/',
    'benchmark_completo.py': 'src/analysis/',
    'benchmark_escala.py': 'src/analysis/',
    'benchmark_pool.py': 'src/analysis/',
    'benchmark_rigoroso.py': 'src/analysis/',
    'benchmark_workers.py': 'src/analysis/',
    # Otimização
    'tsp_solver.py': 'src/optimization/',
    'tsp_solver_paralelo.py': 'src/optimization/',
    'tsp_solver_paralelo_otimizado.py': 'src/optimization/',
    'vrp_solver.py': 'src/optimization/',
    'main_vrp.py': 'src/optimization/',
    # Logística
    'geradordepesos.py': 'src/logistics/',
    'paralelismo_logistica_cidades.py': 'src/logistics/',
    # Simulação
    'testestress.py': 'src/simulation/',
    'monte_carlo_serial.py': 'src/simulation/',
    'monte_carlo_paralelo.py': 'src/simulation/',
    'resumo_executivo.py': 'src/simulation/',
    # Visualização
    'dashboard_interativo.py': 'src/visualization/',
    # Relatórios
    'gerador_relatorio.py': 'src/reporting/',
    'gerador_relatorio_tsp.py': 'src/reporting/',
    'gerar_apresentacao.py': 'src/reporting/',
    'versionar_relatorio.py': 'src/reporting/',
    # Infraestrutura
    'Dockerfile': 'src/infra/',
    'docker-compose.yml': 'src/infra/',
    'setup_mongo_env.sh': 'src/infra/',
    'run_mongod_portable.sh': 'src/infra/',
    'roteirizador_preditivo.service': 'src/infra/',
    'roteirizador_preditivo.timer': 'src/infra/',
    'rota-dash': 'src/infra/',
    # Scripts utilitários
    'executar_pipeline_completo.sh': 'scripts/',
    'executar_tudo.py': 'scripts/',
    'pipeline_completo.py': 'scripts/',
    'pipeline_simples.py': 'scripts/',
    'data_loader.py': 'scripts/',
    'database.py': 'scripts/',
    'create_system_logs_pdf.py': 'scripts/',
    'check_mongo_connection.py': 'scripts/',
    'versionar_readme.py': 'scripts/',
    'gerar_env_block.py': 'scripts/',
    'gerar_paralelismo_pdf.py': 'scripts/',
    'gerar_pdf_codigo.py': 'scripts/',
    'gerar_pdf_completo.py': 'scripts/',
    'gerar_pdf_env.py': 'scripts/',
    'gerar_pdf_simples.py': 'scripts/',
    'gerar_relatorio_final.py': 'scripts/',
    'gerar_relatorio_geral.py': 'scripts/',
    'main.py': 'scripts/',
    # Docs
    'README.md': 'docs/',
    'README_PARALELISMO.md': 'docs/',
    'explicacao_prophet.md': 'docs/',
    'slides_apresentacao.md': 'docs/',
    'apresentacao_proposta.md': 'docs/',
    # Dados
    'volumetria_preenchida.csv': 'data/raw/',
    'volumetria_sazonal_mensal.csv': 'data/raw/',
    'pesos_prioridade_sea.csv': 'data/processed/',
    'previsao_impressoes.csv': 'data/processed/',
    'previsao_impressoes_30d.csv': 'data/processed/',
    'previsao_impressoes_120d.csv': 'data/processed/',
    'previsao_impressoes_180d.csv': 'data/processed/',
    'previsao_impressoes_365d.csv': 'data/processed/',
    'economia_gerada.txt': 'data/processed/',
    'monte_carlo_iterations.txt': 'data/processed/',
    'prophet_mape.txt': 'data/processed/',
    'prophet_mae.txt': 'data/processed/',
    'esg_impacto.txt': 'data/processed/',
    'alertas_anomalias.txt': 'data/processed/',
    'alertas_anomalias_forest.txt': 'data/processed/',
    'log_2opt.txt': 'data/processed/',
    'resumo_executivo.json': 'data/processed/',
    'resumo_estatistico_monte_carlo.json': 'data/processed/',
    'prioridades_paralelas.csv': 'data/processed/',
    'lista_anomalias.csv': 'data/processed/',
    'tabela_1_detalhada.txt': 'data/processed/',
    'tabela_1_tsp_resultados.csv': 'data/processed/',
    'tabela_1_tsp_resultados.tex': 'data/processed/',
    'historico_versoes.txt': 'data/processed/',
    'Relatório-IMPRESSORAS-TecPRINTERS.csv': 'data/raw/',
    # Relatórios gerados
    'RELATORIO_TSP_CONSOLIDADO.md': 'relatorios/',
    'documento_tsp_para_overleaf.tex': 'relatorios/',
    'RELATORIO_PARALELISMO_FINAL.md': 'relatorios/',
    'relatorio_completo_tsp.pdf': 'relatorios/',
    'relatorio_geral_tsp.pdf': 'relatorios/',
    'apresentacao_proposta.pdf': 'relatorios/',
    'environment_details.pdf': 'relatorios/',
    # Imagens
    'relatorio_comparativo_roi.png': 'imagens/',
    'relatorio_comparativo_custos.png': 'imagens/',
    'relatorio_prioridade_ipl.png': 'imagens/',
    'relatorio_contribuicao_ipl.png': 'imagens/',
    'analise_anomalias.png': 'imagens/',
    'analise_previsao_geral.png': 'imagens/',
    'analise_previsao_geral_30d.png': 'imagens/',
    'analise_previsao_geral_120d.png': 'imagens/',
    'analise_previsao_geral_180d.png': 'imagens/',
    'analise_previsao_geral_365d.png': 'imagens/',
    'analise_sazonalidade_meses.png': 'imagens/',
    'mapa_master.png': 'imagens/',
    'mapa_master_paralelo.png': 'imagens/',
    'comparativo_master.png': 'imagens/',
    'comparativo_paralelo.png': 'imagens/',
    'distribuicao_impressoras.png': 'imagens/',
    'logo_empresa.png': 'imagens/',
}

# Mover arquivos
moved = []
for src_name, dest_folder in MOVES.items():
    src = BASE / src_name
    if src.exists():
        dest = BASE / dest_folder / src.name
        shutil.move(str(src), str(dest))
        moved.append(f"{src_name} -> {dest_folder}/")
        print(f"✅ {src_name} -> {dest_folder}/")

print(f"\n📦 Total movido: {len(moved)} arquivos")

# Mover diretórios específicos
if (BASE / 'Artigos').exists():
    shutil.move(str(BASE / 'Artigos'), str(BASE / 'docs/artigos'))
    print("✅ Artigos/ -> docs/artigos/")

if (BASE / 'historico_readme').exists():
    shutil.move(str(BASE / 'historico_readme'), str(BASE / 'docs/historico_readme'))
    print("✅ historico_readme/ -> docs/historico_readme/")

if (BASE / 'historico_relatorios').exists():
    shutil.move(str(BASE / 'historico_relatorios'), str(BASE / 'relatorios/historico'))
    print("✅ historico_relatorios/ -> relatorios/historico/")

if (BASE / 'logs').exists():
    shutil.move(str(BASE / 'logs'), str(BASE / 'logs'))
    print("✅ logs/ -> logs/")

print("\n✅ Reorganização concluída. Agora atualize os imports nos scripts.")
