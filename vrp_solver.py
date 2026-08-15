#!/usr/bin/env python3
"""
Solucionador de Vehicle Routing Problem (VRP) com Capacidade
Utiliza a biblioteca Google OR-Tools para otimização.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np

def create_data_model(matriz_distancias, demandas, capacidade_veiculo, janelas_tempo):
    """Prepara os dados para o modelo OR-Tools."""
    data = {}
    data['distance_matrix'] = matriz_distancias
    data['demands'] = demandas
    data['vehicle_capacities'] = [capacidade_veiculo] * len(matriz_distancias) # Assumindo frota homogênea
    data['time_windows'] = janelas_tempo
    data['num_vehicles'] = len(matriz_distancias) # Pior caso: um veículo por cidade
    data['depot'] = 0 # Define o depósito como o nó de índice 0
    return data

def solve_vrp(data):
    """Resolve o problema de VRP com capacidade."""
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    # Callback para a distância
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Callback para a demanda (capacidade)
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # Slack (folga) da capacidade
        data['vehicle_capacities'],
        True,  # Começar com capacidade zero
        'Capacity'
    )

    # Callback para o tempo de viagem + serviço
    def time_callback(from_index, to_index):
        """Retorna o tempo de viagem entre dois nós."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Tempo de viagem = distância / velocidade média (ex: 60 km/h)
        # Adiciona tempo de serviço (ex: 30 minutos = 0.5 horas)
        travel_time = data['distance_matrix'][from_node][to_node] / 60 
        service_time = 0.5 # 30 minutos de serviço
        return int((travel_time + service_time) * 100) # Convertido para inteiros

    time_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.AddDimension(
        time_callback_index,
        3000,  # Slack máximo (folga de tempo) em cada veículo
        3000,  # Tempo máximo total por veículo
        False, # Não começar com tempo acumulado zero
        'Time'
    )
    time_dimension = routing.GetDimensionOrDie('Time')
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']: continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0] * 100, time_window[1] * 100)

    # Configurações da busca
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(5)

    # Resolve o problema
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        return format_solution(data, manager, routing, solution)
    else:
        return None, None

def format_solution(data, manager, routing, solution):
    """Formata e imprime a solução do VRP."""
    total_distance = 0
    rotas = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_distance = 0
        route_nodes = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_nodes.append(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        # Adiciona o último nó (retorno ao depósito)
        route_nodes.append(manager.IndexToNode(index))
        
        if len(route_nodes) > 2: # Rota não vazia
            rotas.append({
                'vehicle_id': vehicle_id,
                'route': route_nodes,
                'distance_km': route_distance
            })
            total_distance += route_distance
            
    return rotas, total_distance

# Exemplo de uso (seria integrado ao seu pipeline)
# if __name__ == '__main__':
#     # Carregue sua matriz de distâncias e demandas (IPL ou volume)
#     # matriz = ...; demandas = ...
#     # data = create_data_model(matriz, demandas, capacidade_veiculo=100)
#     # rotas, dist_total = solve_vrp(data)