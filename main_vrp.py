#!/usr/bin/env python3
"""
Script Principal para Resolução do VRP (Vehicle Routing Problem)

Este script integra o `vrp_solver` para resolver um problema de roteamento
de múltiplos veículos com restrição de capacidade.

Cenário:
- Uma frota de veículos parte de um depósito (Florianópolis).
- Cada veículo tem uma capacidade máxima (ex: 100 unidades de demanda).
- As cidades têm demandas variadas (usando o IPL como proxy de demanda).
- O objetivo é encontrar as rotas que minimizam a distância total percorrida
  por todos os veículos, respeitando a capacidade de cada um.
"""

import pandas as pd
from tsp_solver import calcular_matriz_distancias, CIDADES_COORDENADAS
from vrp_solver import create_data_model, solve_vrp

def main():
    print("\n" + "="*70)
    print(" 🚚 VRP SOLVER - ROTEAMENTO DE MÚLTIPLOS VEÍCULOS ".center(70, "="))
    print("="*70 + "\n")

    # 1. Carregar dados e calcular matriz de distâncias
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    print(f"📍 Matriz de distâncias calculada para {len(cidades)} cidades.")

    # 2. Carregar ou simular as demandas das cidades
    try:
        df_pesos = pd.read_csv('pesos_prioridade_sea.csv')
        # Mapeia o IPL para uma demanda inteira para o VRP
        demandas_dict = pd.Series(df_pesos.IPL.values, index=df_pesos.Cidade.str.upper()).to_dict()
        demandas = [int(demandas_dict.get(cidade, 0) * 100) for cidade in cidades]
        print("📈 Demandas carregadas a partir do IPL (Índice de Prioridade Logística).")
    except FileNotFoundError:
        print("⚠️  Arquivo 'pesos_prioridade_sea.csv' não encontrado. Usando demandas aleatórias.")
        demandas = [0] + [15, 18, 22, 10, 13, 16, 25, 8, 12, 19, 11, 14, 20, 9, 17, 21, 7] # Demanda 0 para o depósito

    # Garante que o depósito (Florianópolis, índice 0) tenha demanda 0
    depot_index = cidades.index('FLORIANÓPOLIS')
    demandas[depot_index] = 0

    # 3. Configurar e criar o modelo de dados para o OR-Tools
    CAPACIDADE_VEICULO = 100  # Capacidade máxima de cada veículo
    print(f"🚛 Capacidade definida por veículo: {CAPACIDADE_VEICULO} unidades.\n")

    data = create_data_model(matriz_dist.tolist(), demandas, CAPACIDADE_VEICULO)

    # 4. Resolver o VRP
    print("🧠 Resolvendo o Problema de Roteamento de Veículos (VRP)...")
    rotas, distancia_total = solve_vrp(data)

    # 5. Exibir a solução
    if rotas:
        print("\n" + "="*70)
        print(" ✅ SOLUÇÃO VRP ENCONTRADA ".center(70, "="))
        print(f"\nDistância total de todas as rotas: {distancia_total:.2f} km\n")
        for rota in rotas:
            cidades_rota = ' -> '.join([cidades[i] for i in rota['route']])
            print(f"Veículo {rota['vehicle_id']}: {cidades_rota}")
            print(f"   Distância da rota: {rota['distance_km']:.2f} km\n")
    else:
        print("❌ Nenhuma solução encontrada para o VRP.")

if __name__ == "__main__":
    main()