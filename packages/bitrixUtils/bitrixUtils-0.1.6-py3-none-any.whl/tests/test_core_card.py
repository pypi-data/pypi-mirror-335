import sys
import os
import json

# Adiciona o diretório do bitrix.py ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bitrixUtils')))
import core
BITRIX_WEBHOOK_URL = "https://setup.bitrix24.com.br/rest/629/c0q6gqm7og1bs91k/"

test_id = 11363
test_card = core.getSpaCardFields(187, test_id, BITRIX_WEBHOOK_URL, LOG=True)
print(json.dumps(test_card, indent=4, ensure_ascii=False))
