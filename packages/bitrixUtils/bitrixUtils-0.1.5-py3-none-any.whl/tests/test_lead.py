import sys
import os
import unittest
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bitrixUtils')))
import core

BITRIX_WEBHOOK_URL = "https://setup.bitrix24.com.br/rest/629/c0q6gqm7og1bs91k/"

custom_fields_dict = {
    "cpfContact": "UF_CRM_CPF",  # Campo CPF conforme configurado no ambiente Bitrix que funcionou nos testes isolados
    "leadEmpresa": "UF_CRM_1741809329811",
    "leadCargo": "UF_CRM_1741809370635",
    "leadNumFunc": "UF_CRM_1741809387923",
    "leadContact": "CONTACT_ID"
}

lead_data = {
    custom_fields_dict["leadCargo"] : "Cargo",
    custom_fields_dict["leadEmpresa"] : "Empresa",
    custom_fields_dict["leadNumFunc"] : "Funcs",
    custom_fields_dict["leadContact"] : 3975
}

lead = core.createLead(BITRIX_WEBHOOK_URL,
                       lead_data,
                       LOG=False)

print(json.dumps(lead, indent=2, ensure_ascii=False))