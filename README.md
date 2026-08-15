# Caixeiro Viajante

Projeto da Disciplina de Sistemas Inteligentes na UD.

## Estrutura do Projeto

```
caixeiro_viajante/
├── dados/
│   └── cidades.csv        # Arquivo CSV com as distâncias entre cidades
├── .vscode/
│   └── settings.json      # Configurações do VS Code
├── importar_dados.py       # Script para importar os dados do CSV
└── README.md
```

## Como usar no VS Code

1. Abra a pasta do projeto no VS Code:
   - Menu **Arquivo > Abrir Pasta** e selecione a pasta `caixeiro_viajante`

2. Execute o script de importação de dados:
   - Abra o terminal no VS Code (**Terminal > Novo Terminal**)
   - Execute:
     ```bash
     python3 importar_dados.py
     ```

## Formato do arquivo de dados (`dados/cidades.csv`)

O arquivo CSV deve conter as seguintes colunas:

| cidade_origem | cidade_destino | distancia_km |
|---------------|----------------|-------------|
| A             | B              | 10          |
| A             | C              | 15          |
| ...           | ...            | ...         |

Para adicionar novas cidades, basta editar o arquivo `dados/cidades.csv` com um editor de texto ou diretamente no VS Code.

## Importando os dados em outro script Python

```python
from importar_dados import importar_dados

distancias = importar_dados('dados/cidades.csv')
print(distancias[('A', 'B')])  # 10.0
```
