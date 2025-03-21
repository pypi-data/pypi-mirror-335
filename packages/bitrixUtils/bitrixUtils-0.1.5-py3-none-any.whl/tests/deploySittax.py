import sys
import os
import json

url = "https://setup.bitrix24.com.br/rest/629/c0q6gqm7og1bs91k/"

# Adiciona o diretório do bitrix.py ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bitrixUtils')))
import core

# Define o caminho do arquivo JSON
input_file = "cardsSittax.json"

# Define os campos que serão limpos
campos = [
    "ufCrm5_1737545372279",
    "ufCrm5_1737545379350",
    "ufCrm5_1710961669613",
    "ufCrm5_1736438430958"
]

# Lê o arquivo JSON
try:
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Processa cada registro do JSON
    for record in data:
        lead_id = record['id']
        # Chama a função para limpar os campos
        core.clearSpaCardFields(url, 187, lead_id, campos)
        print(f"Campos limpos para o ID: {lead_id}")

except FileNotFoundError:
    print(f"Erro: Arquivo {input_file} não encontrado")
except json.JSONDecodeError:
    print("Erro: Arquivo JSON inválido")
except Exception as e:
    print(f"Erro inesperado: {str(e)}")