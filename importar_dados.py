import csv
import os


def importar_dados(caminho_arquivo):
    """
    Importa os dados de distâncias entre cidades a partir de um arquivo CSV.

    O arquivo deve ter as colunas:
        cidade_origem, cidade_destino, distancia_km

    Retorna um dicionário onde:
        distancias[(origem, destino)] = distancia_km
    """
    distancias = {}

    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            origem = linha['cidade_origem'].strip()
            destino = linha['cidade_destino'].strip()
            distancia = float(linha['distancia_km'].strip())
            distancias[(origem, destino)] = distancia
            distancias[(destino, origem)] = distancia  # grafo não-direcionado

    return distancias


if __name__ == '__main__':
    caminho = os.path.join(os.path.dirname(__file__), 'dados', 'cidades.csv')
    distancias = importar_dados(caminho)

    print("Dados importados com sucesso!")
    print("\nDistâncias entre cidades:")
    cidades_vistas = set()
    for (origem, destino), dist in distancias.items():
        if (destino, origem) not in cidades_vistas:
            print(f"  {origem} -> {destino}: {dist} km")
            cidades_vistas.add((origem, destino))
