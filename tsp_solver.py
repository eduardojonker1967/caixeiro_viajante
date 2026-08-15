#!/usr/bin/env python3
"""
TSP Solver - Traveling Salesman Problem com dados reais de Santa Catarina
Implementa: Nearest Neighbor, 2-opt, Simulated Annealing, Tabu Search e Algoritmo Genético.
"""

import numpy as np
from collections import deque
import time
import random # Adicionado para o simulated_annealing
from math import radians, sin, cos, sqrt, asin

# ============================================================================
# 1. COORDENADAS REAIS DAS CIDADES DE SANTA CATARINA
# ============================================================================
CIDADES_COORDENADAS = {
    'FLORIANÓPOLIS': (-27.5945, -48.5477),
    'BLUMENAU': (-26.8795, -49.0510),
    'ITAJAÍ': (-26.9147, -48.6622),
    'CHAPECÓ': (-27.0929, -49.7632),
    'CRICIÚMA': (-28.6816, -49.3736),
    'JARAGUÁ DO SUL': (-26.4845, -49.0648),
    'LAGES': (-27.8162, -50.3267),
    'BRUSQUE': (-26.7909, -49.0147),
    'TUBARÃO': (-28.4866, -49.0026),
    'CONCÓRDIA': (-27.2269, -51.9754),
    'RIO DO SUL': (-27.1953, -49.6325),
    'VIDEIRA': (-27.0053, -51.1552),
    'MAFRA': (-26.2461, -49.7898),
    'IMBITUBA': (-28.2405, -48.6722),
    'SÃO MIGUEL DO OESTE': (-27.3594, -53.5260),
    'CURITIBANOS': (-27.3014, -49.3199),
    'JOINVILLE': (-26.3044, -48.8456),
    'JOAÇABA': (-27.1775, -51.5030),
}

# ============================================================================
# 2. FUNÇÕES AUXILIARES
# ============================================================================

def calcular_matriz_distancias(cidades_dict):
    """Calcula matriz de distâncias entre todas as cidades"""
    cidades = list(cidades_dict.keys())
    n = len(cidades)
    matriz = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = cidades_dict[cidades[i]]
                lat2, lon2 = cidades_dict[cidades[j]]
                
                # Fórmula de Haversine
                R = 6371  # Raio da Terra em km
                lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
                dlon = lon2_rad - lon1_rad
                dlat = lat2_rad - lat1_rad
                a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                distancia = R * c
                
                matriz[i][j] = distancia
    
    return matriz, cidades

def nearest_neighbor(matriz_dist, start=0):
    """Algoritmo Nearest Neighbor para TSP"""
    n = len(matriz_dist)
    unvisited = set(range(n))
    current = start
    rota = [current]
    unvisited.remove(current)
    
    total_dist = 0
    while unvisited:
        nearest = min(unvisited, key=lambda x: matriz_dist[current][x])
        total_dist += matriz_dist[current][nearest]
        current = nearest
        rota.append(current)
        unvisited.remove(current)
    
    # Retorna ao ponto inicial
    total_dist += matriz_dist[current][start]
    rota.append(start)
    
    return rota, total_dist

def two_opt(rota, matriz_dist, max_iterations=10000, return_log=False):
    """
    Otimização 2-opt para melhorar a rota.
    Iterativamente remove dois arcos e os reconecta de outra forma
    para verificar se a distância total diminui.
    """
    best_rota = rota[:]
    best_dist = calcular_distancia_rota(best_rota, matriz_dist)
    log_distancias = []
    start_time = time.time()
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        for i in range(1, len(best_rota) - 2):
            for j in range(i + 1, len(best_rota)):
                if j - i == 1:
                    continue
                
                # Cria nova rota invertendo segmento entre i e j
                nova_rota = best_rota[:i] + best_rota[i:j][::-1] + best_rota[j:]
                nova_dist = calcular_distancia_rota(nova_rota, matriz_dist)
                
                if nova_dist < best_dist:
                    best_rota = nova_rota[:]
                    best_dist = nova_dist
                    log_distancias.append(best_dist)
                    improved = True
                    break
            
            if improved:
                break
    
    tempo_execucao = time.time() - start_time
    if return_log:
        return best_rota, best_dist, log_distancias, tempo_execucao
    else:
        return best_rota, best_dist

def tabu_search(rota_inicial, matriz_dist, max_iteracoes=10000, tamanho_tabu=30):
    """
    Algoritmo de Busca Tabu (Tabu Search) para TSP.
    Usa uma lista tabu para evitar movimentos recentes e escapar de ótimos locais.
    """
    melhor_rota = rota_inicial[:]
    melhor_dist = calcular_distancia_rota(melhor_rota, matriz_dist)
    
    rota_atual = melhor_rota[:]
    dist_atual = melhor_dist
    
    lista_tabu = deque(maxlen=tamanho_tabu)
    
    for _ in range(max_iteracoes):
        melhor_vizinho = None
        melhor_vizinho_dist = float('inf')
        movimento_candidato = None

        # Explora a vizinhança (movimentos 2-opt)
        for i in range(1, len(rota_atual) - 2):
            for j in range(i + 1, len(rota_atual) - 1):
                movimento = tuple(sorted((rota_atual[i-1], rota_atual[i], rota_atual[j-1], rota_atual[j])))
                
                if movimento in lista_tabu:
                    continue # Pula movimento tabu

                vizinho = rota_atual[:i] + rota_atual[i:j][::-1] + rota_atual[j:]
                dist_vizinho = calcular_distancia_rota(vizinho, matriz_dist)

                if dist_vizinho < melhor_vizinho_dist:
                    melhor_vizinho = vizinho
                    melhor_vizinho_dist = dist_vizinho
                    movimento_candidato = movimento

        if melhor_vizinho is None:
            break # Sem movimentos válidos

        rota_atual = melhor_vizinho
        dist_atual = melhor_vizinho_dist
        lista_tabu.append(movimento_candidato)

        if dist_atual < melhor_dist:
            melhor_rota = rota_atual[:]
            melhor_dist = dist_atual
            
    return melhor_rota, melhor_dist

def genetic_algorithm(matriz_dist, pop_size=100, elite_size=20, mutation_rate=0.01, generations=500):
    """Algoritmo Genético para TSP."""
    n_cidades = len(matriz_dist)
    
    def criar_rota():
        rota = list(range(n_cidades))
        np.random.shuffle(rota)
        return rota

    populacao = [criar_rota() for _ in range(pop_size)]

    for _ in range(generations):
        # Ordena a população pela distância (fitness)
        populacao = sorted(populacao, key=lambda r: calcular_distancia_rota(r + [r[0]], matriz_dist))
        nova_populacao = populacao[:elite_size] # Elitismo

        for _ in range(pop_size - elite_size):
            pai1, pai2 = np.random.choice(elite_size, 2, replace=False)
            pai1, pai2 = populacao[pai1], populacao[pai2]
            
            # Crossover Ordenado (OX1)
            start, end = sorted(np.random.choice(n_cidades, 2, replace=False))
            filho = [-1] * n_cidades
            filho[start:end+1] = pai1[start:end+1]
            
            p2_idx = 0
            for i in range(n_cidades):
                if filho[i] == -1:
                    while pai2[p2_idx] in filho:
                        p2_idx += 1
                    filho[i] = pai2[p2_idx]
            
            # Mutação (Swap)
            if np.random.rand() < mutation_rate:
                idx1, idx2 = np.random.choice(n_cidades, 2, replace=False)
                filho[idx1], filho[idx2] = filho[idx2], filho[idx1]
            
            nova_populacao.append(filho)
        
        populacao = nova_populacao

    melhor_rota_ga = populacao[0]
    melhor_rota_ga.append(melhor_rota_ga[0]) # Fechar o ciclo
    melhor_dist_ga = calcular_distancia_rota(melhor_rota_ga, matriz_dist)
    
    return melhor_rota_ga, melhor_dist_ga

def simulated_annealing(rota_inicial, matriz_dist, temp_inicial=1000, taxa_resfriamento=0.995, max_iter=10000):
    """
    Algoritmo Simulated Annealing para TSP.
    Usa uma perturbação baseada em 2-opt para gerar vizinhos.
    """
    rota_atual = rota_inicial[:-1] # Remove o ponto de volta para manipular
    dist_atual = calcular_distancia_rota(rota_atual + [rota_atual[0]], matriz_dist)
    
    melhor_rota = rota_atual[:]
    melhor_dist = dist_atual
    
    temp = temp_inicial
    
    for _ in range(max_iter):
        # Gera um vizinho usando uma perturbação 2-opt
        i, j = sorted(random.sample(range(len(rota_atual)), 2))
        
        nova_rota = rota_atual[:i] + rota_atual[i:j+1][::-1] + rota_atual[j+1:]
        nova_dist = calcular_distancia_rota(nova_rota + [nova_rota[0]], matriz_dist)
        
        # Decide se aceita o vizinho
        if nova_dist < dist_atual or random.random() < np.exp((dist_atual - nova_dist) / temp):
            rota_atual, dist_atual = nova_rota, nova_dist
            
            if nova_dist < melhor_dist:
                melhor_rota = rota_atual[:]
                melhor_dist = dist_atual
        
        temp *= taxa_resfriamento
    return melhor_rota + [melhor_rota[0]], melhor_dist

def calcular_distancia_rota(rota, matriz_dist):
    """Calcula distância total de uma rota"""
    dist = 0
    for i in range(len(rota) - 1):
        dist += matriz_dist[rota[i]][rota[i+1]]
    return dist

def gerar_rota_aleatoria(matriz_dist, seed=42):
    """Gera uma rota aleatória para comparação"""
    np.random.seed(seed)
    rota = list(range(len(matriz_dist)))
    np.random.shuffle(rota)
    rota.append(rota[0])  # Fecha a rota
    dist = calcular_distancia_rota(rota, matriz_dist)
    return rota, dist
