import sys
import os
import json

# Adiciona o diretório do bitrix.py ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bitrixUtils')))
import core
BITRIX_WEBHOOK_URL = "https://setup.bitrix24.com.br/rest/"
