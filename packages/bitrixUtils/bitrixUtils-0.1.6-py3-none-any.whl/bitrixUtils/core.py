import requests
import logging
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format="\n%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Exibe logs no console
    ]
)

# General Functions

# logDetailedMessage
# EN: Logs a detailed message if the LOG flag is enabled
# PT: Registra uma mensagem detalhada se a flag LOG estiver ativada
def logDetailedMessage(mensagem, tag_log=False):
    """
    Função para gerar logs detalhados se a tag LOG estiver ativa.

    :param mensagem: Mensagem a ser logada.
    :param tag_log: Se True, exibe/loga a mensagem.
    """
    if tag_log:
        logging.info(mensagem)

# _bitrix_request
# EN: Makes API requests to Bitrix24 with error handling and retry logic
# PT: Faz requisições à API do Bitrix24 com tratamento de erros e tentativas
def _bitrix_request(api_method, params, bitrix_webhook_url, LOG=False, max_retries=5):
    """
    Função centralizada para requisições ao Bitrix24 com tratamento de erros e retry.

    :param api_method: Método da API do Bitrix24 (ex: "crm.contact.list").
    :param params: Dicionário com os parâmetros da requisição.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.
    :param max_retries: Número máximo de tentativas em caso de erro 503.
    :return: Resposta JSON da API ou None em caso de falha.
    """
    endpoint = f"{bitrix_webhook_url}{api_method}"
    delay = 2  # Tempo inicial de espera em segundos

    for tentativa in range(max_retries):
        try:
            if LOG:
                logDetailedMessage(f"[BITRIX REQUEST] Tentativa {tentativa + 1}/{max_retries} para {api_method}", LOG)
                logDetailedMessage(f"[BITRIX REQUEST] Payload: {json.dumps(params, indent=2, ensure_ascii=False)}", LOG)

            response = requests.post(endpoint, json=params, timeout=10)

            if LOG:
                logDetailedMessage(f"[BITRIX REQUEST] Resposta: {response.status_code} - {response.text}", LOG)

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 503:  # Too Many Requests
                logDetailedMessage(f"[BITRIX REQUEST] Erro 503: Too Many Requests. Retentando em {delay} segundos...", LOG)
                time.sleep(delay)
                delay *= 2  # Aumenta o tempo de espera exponencialmente

            else:
                logDetailedMessage(f"[BITRIX REQUEST] Erro na requisição: {response.status_code} - {response.text}", LOG)
                return None

        except requests.Timeout:
            logDetailedMessage(f"[BITRIX REQUEST] Timeout na requisição. Tentativa {tentativa + 1}/{max_retries}. Retentando em {delay} segundos...", LOG)
            time.sleep(delay)
            delay *= 2  # Backoff exponencial
        except requests.RequestException as e:
            logDetailedMessage(f"[BITRIX REQUEST] Erro ao conectar com Bitrix24: {str(e)}", LOG)
            return None

    logDetailedMessage("[BITRIX REQUEST] Número máximo de tentativas atingido. Requisição falhou.", LOG)
    return None

# getTypeId
# EN: Gets all possible contact type IDs and their descriptions
# PT: Obtém todos os tipos de contato possíveis e suas descrições
def getTypeId(bitrixWebhookUrl, LOG=False):
    """
    Obtém todos os valores distintos do campo TYPE_ID dos contatos no Bitrix24 e seus significados.

    Essa função consulta a API `crm.status.list` para mapear os IDs dos TYPE_IDs aos seus respectivos valores.

    :param bitrixWebhookUrl: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados para depuração.

    :return: Dicionário { ID: "Descrição" } contendo todos os valores possíveis do TYPE_ID.
    """
    params = {"FILTER": {"ENTITY_ID": "CONTACT_TYPE"}}

    response = _bitrix_request("crm.status.list", params, bitrixWebhookUrl, LOG)

    if response and "result" in response:
        typeIdMap = {item["STATUS_ID"]: item["NAME"] for item in response["result"]}
        logDetailedMessage(f"[OBTER TYPE_ID] Mapeamento obtido: {typeIdMap}", LOG)
        return typeIdMap

    logDetailedMessage("[OBTER TYPE_ID] Erro ao buscar os metadados do campo TYPE_ID via crm.status.list.", LOG)
    return {}

# listSpaEntities
# EN: Lists all available SPA entities in Bitrix24
# PT: Lista todas as entidades SPA disponíveis no Bitrix24
def listSpaEntities(bitrix_webhook_url, LOG=False):
    """
    Obtém a lista de entidades do CRM do Bitrix24.

    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Lista de dicionários contendo 'title' e 'entityTypeId' das entidades.
    """
    method = "crm.type.list"  # Método para listar os tipos de entidades
    response = _bitrix_request(method, {}, bitrix_webhook_url, LOG)

    # Verificando se a resposta é válida e contém os dados esperados
    if response and "result" in response and "types" in response["result"]:
        entidades = []

        for entity in response["result"]["types"]:
            entidade_info = {
                "title": entity.get("title"),
                "entityTypeId": entity.get("entityTypeId")
            }
            entidades.append(entidade_info)

        logDetailedMessage(f"[FIND ENTERPRISE] {len(entidades)} entidades encontradas.", LOG)
        return entidades  # Retorna a lista formatada

    logDetailedMessage("[FIND ENTERPRISE] Nenhuma entidade encontrada ou formato inesperado da resposta.", LOG)
    return None  # Retorna None em caso de erro

# Contact Functions

# getContactAddressById
# EN: Retrieves a contact's address using their ID, checking both address API and contact data
# PT: Obtém o endereço de um contato usando seu ID, verificando tanto a API de endereços quanto os dados do contato
def getContactAddressById(contact_id, bitrix_webhook_url, LOG=False):
    """
    Obtém o endereço vinculado a um contato no Bitrix24.

    Primeiro, verifica se o endereço está cadastrado na API crm.address.list.
    Caso não esteja, retorna os dados de endereço armazenados diretamente no contato.

    :param contact_id: ID do contato no Bitrix24.
    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.
    :return: Dicionário contendo os dados do endereço ou None caso não exista.
    """

    # Tentar obter endereço via crm.address.list
    params = {
        "filter": {"ENTITY_ID": contact_id},
        "select": ["*"]
    }
    response = _bitrix_request("crm.address.list", params, bitrix_webhook_url, LOG)

    if response and "result" in response and response["result"]:
        endereco = response["result"][0]
        logDetailedMessage(f"[OBTER ENDEREÇO] Endereço encontrado na API crm.address.list para contato ID: {contact_id}", LOG)
        return endereco

    # Se não encontrar na crm.address.list, buscar diretamente no contato
    contato = _bitrix_request("crm.contact.get", {"ID": contact_id}, bitrix_webhook_url, LOG)

    if contato and "result" in contato:
        endereco = {
            "ADDRESS_1": contato["result"].get("ADDRESS"),
            "ADDRESS_2": contato["result"].get("ADDRESS_2"),
            "CITY": contato["result"].get("ADDRESS_CITY"),
            "POSTAL_CODE": contato["result"].get("ADDRESS_POSTAL_CODE"),
            "REGION": contato["result"].get("ADDRESS_REGION"),
            "PROVINCE": contato["result"].get("ADDRESS_PROVINCE"),
            "COUNTRY": contato["result"].get("ADDRESS_COUNTRY"),
        }
        logDetailedMessage(f"[OBTER ENDEREÇO] Endereço extraído diretamente do contato ID: {contact_id}", LOG)
        return endereco if any(endereco.values()) else None

    logDetailedMessage(f"[OBTER ENDEREÇO] Nenhum endereço encontrado para contato ID: {contact_id}", LOG)
    return None

# checkContactExists
# EN: Checks if a contact exists using a unique field (like CPF or email)
# PT: Verifica se um contato existe usando um campo único (como CPF ou email)
def checkContactExists(key, keyField, bitrix_webhook_url, LOG=False):
    """
    Verifica se um contato com um campo único (ex: CPF, e-mail) já existe no Bitrix24.

    :param key: Valor único que será usado para buscar o contato.
    :param keyField: Nome do campo no Bitrix24 que contém esse valor.
    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.
    :return: ID do contato se existir, None caso contrário.
    """
    params = {
        "filter": {keyField: key},
        "select": ["ID"]
    }

    response = _bitrix_request("crm.contact.list", params, bitrix_webhook_url, LOG)

    if response and "result" in response and response["result"]:
        contact_id = response["result"][0]["ID"]
        logDetailedMessage(f"[VERIFICAR CONTATO] Contato encontrado. ID: {contact_id}", LOG)
        return contact_id

    logDetailedMessage("[VERIFICAR CONTATO] Nenhum contato encontrado.", LOG)
    return None

#createContact
# EN: Creates a new contact with required and optional custom fields
# PT: Cria um novo contato com campos obrigatórios e personalizados opcionais
def createContact(contact_data, cpf_field, bitrix_webhook_url, extra_fields=None, LOG=False):
    """
    Cria um novo contato no Bitrix24.

    Esta função cria um contato no Bitrix24 utilizando os dados fornecidos e pode incluir
    campos personalizados, se necessário.

    :param contact_data: Dicionário contendo as informações do contato, com as seguintes chaves:
        - cpf (str): CPF do contato no formato "123.456.789-00".
        - name (str): Nome do contato.
        - email (str): Endereço de e-mail do contato.
        - celular (str): Número de telefone no formato "(11) 98765-4321".
    :param cpf_field: Nome do campo personalizado no Bitrix24 que armazena o CPF.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param extra_fields: (Opcional) Dicionário contendo campos adicionais para o contato.
    :param LOG: Se True, ativa logs detalhados para depuração.

    :return: ID do contato criado em caso de sucesso, ou None se falhar.
    """

    # Construindo payload com os dados obrigatórios do contato
    params = {
        "fields": {
            cpf_field: contact_data.get("cpf"),
            "NAME": contact_data.get("name"),
            "EMAIL": [{"VALUE": contact_data.get("email"), "VALUE_TYPE": "WORK"}],
            "PHONE": [{"VALUE": contact_data.get("celular"), "VALUE_TYPE": "WORK"}]
        }
    }

    # Se houver campos extras, adicioná-los ao payload
    if extra_fields and isinstance(extra_fields, dict):
        params["fields"].update(extra_fields)

    # Chamada à API centralizada usando `_bitrix_request`
    response = _bitrix_request("crm.contact.add", params, bitrix_webhook_url, LOG)

    # Verifica resposta e retorna o ID do contato criado
    if response and "result" in response:
        contact_id = response["result"]
        logDetailedMessage(f"[CRIAR CONTATO] Contato criado com sucesso. ID: {contact_id}", LOG)
        return contact_id

    logDetailedMessage("[CRIAR CONTATO] Falha ao obter o ID do contato criado.", LOG)
    return None

#createContactAddress
# EN: Creates and links a new address to an existing contact
# PT: Cria e vincula um novo endereço a um contato existente
def createContactAddress(contact_id, address_data, bitrix_webhook_url, extra_fields=None, LOG=False):
    """
    Cria um endereço no Bitrix24 e vincula ao contato especificado.

    Esta função cria um novo endereço para um contato existente no Bitrix24.

    :param contact_id: ID do contato ao qual o endereço será vinculado (int ou string).
    :param address_data: Dicionário contendo os dados do endereço:
        - rua (str): Nome da rua.
        - numero (str): Número do endereço.
        - cidade (str): Nome da cidade.
        - cep (str): CEP do endereço no formato "01234-567".
        - estado (str): Sigla do estado (ex: "SP").
        - bairro (str): Nome do bairro.
        - complemento (str): Complemento do endereço.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param extra_fields: (Opcional) Dicionário contendo campos adicionais do endereço.
    :param LOG: Se True, ativa logs detalhados.

    :return: ID do endereço criado em caso de sucesso, ou None se falhar.
    """

    # Construção do payload com os campos obrigatórios
    params = {
        "fields": {
            "ENTITY_ID": contact_id,  # ID do contato vinculado
            "ENTITY_TYPE_ID": 3,  # Tipo de entidade para contatos
            "TYPE_ID": 1,  # Tipo de endereço (Padrão: Comercial)
            "ADDRESS_1": f"{address_data.get('rua', '')}, {address_data.get('numero', '')}",
            "CITY": address_data.get("cidade", ""),
            "POSTAL_CODE": address_data.get("cep", ""),
            "COUNTRY": "Brasil",
            "PROVINCE": address_data.get("estado", ""),
            "ADDRESS_2": f"{address_data.get('bairro', '')}, {address_data.get('complemento', '')}"
        }
    }

    # Se houver campos extras, adicioná-los ao payload
    if extra_fields and isinstance(extra_fields, dict):
        params["fields"].update(extra_fields)

    # Chamada à API centralizada usando `_bitrix_request`
    response = _bitrix_request("crm.address.add", params, bitrix_webhook_url, LOG)

    # Verifica resposta e retorna o ID do endereço criado
    if response and "result" in response:
        address_id = response["result"]
        logDetailedMessage(f"[CRIAR ENDEREÇO] Endereço criado com sucesso. ID: {address_id}", LOG)
        return address_id

    logDetailedMessage("[CRIAR ENDEREÇO] Falha ao obter o ID do endereço criado.", LOG)
    return None

# getContactAddress
# EN: Gets the first address associated with a contact
# PT: Obtém o primeiro endereço associado a um contato
def getContactAddress(contact_id, bitrix_webhook_url, LOG=False):
    """
    Obtém o endereço vinculado a um contato no Bitrix24.

    Essa função retorna o primeiro endereço encontrado associado a um contato no Bitrix24.

    :param contact_id: ID do contato no Bitrix24.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados para depuração.

    :return: Dicionário com os dados do endereço ou None se não existir.
    """

    params = {
        "filter": {
            "ENTITY_ID": contact_id,
            "ENTITY_TYPE_ID": 3  # Tipo de entidade para contatos no Bitrix24
        }
    }

    response = _bitrix_request("crm.address.list", params, bitrix_webhook_url, LOG)

    if response and "result" in response and response["result"]:
        endereco = response["result"][0]  # Retorna o primeiro endereço encontrado
        logDetailedMessage(f"[OBTER ENDEREÇO] Endereço encontrado para contato ID {contact_id}: {endereco}", LOG)
        return endereco

    logDetailedMessage(f"[OBTER ENDEREÇO] Nenhum endereço encontrado para contato ID {contact_id}.", LOG)
    return None

#getContactFields
# EN: Retrieves all fields from a specific contact
# PT: Obtém todos os campos de um contato específico
def getContactFields(contact_id, bitrix_webhook_url, LOG=False):
    """
    Obtém todos os campos de um contato específico no Bitrix24.

    :param contact_id: ID do contato a ser consultado.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Dicionário com os campos do contato ou None em caso de erro.
    """
    params = {"id": contact_id}
    response = _bitrix_request("crm.contact.get", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        contato = response["result"]
        logDetailedMessage(f"[OBTER CAMPOS CONTATO] Campos obtidos com sucesso para contato ID {contact_id}.", LOG)
        return contato

    logDetailedMessage(f"[OBTER CAMPOS CONTATO] Nenhum contato encontrado para ID {contact_id}.", LOG)
    return None

# getSpecificContactField
# EN: Gets metadata for a specific contact custom field
# PT: Obtém metadados de um campo personalizado específico do contato
def getSpecificContactField(campo_personalizado, bitrix_webhook_url, LOG=False):
    """
    Obtém os metadados de um campo personalizado específico de um contato no Bitrix24 e,
    se presente, retorna a propriedade "items" desse campo.

    :param campo_personalizado: Nome exato do campo personalizado (ex: ufCrm41_1737980514688).
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Lista com os itens do campo, ou o dicionário do campo se não possuir "items".
    """
    # Faz a requisição para obter todos os campos dos contatos
    response = _bitrix_request("crm.contact.fields", {}, bitrix_webhook_url, LOG)

    if response and "result" in response:
        campos = response["result"]

        # Debug: log das chaves encontradas para ajudar na depuração
        for key in campos:
            logDetailedMessage(f"[DEBUG] Chave encontrada: {repr(key)}", LOG)

        # Normaliza a comparação removendo espaços e convertendo para minúsculas
        campo_procura = campo_personalizado.strip().lower()

        for key in campos:
            if key.strip().lower() == campo_procura:
                logDetailedMessage(f"[OBTER CAMPO ESPECÍFICO CONTATO] Campo encontrado: {key}", LOG)
                field_data = campos[key]
                if "items" in field_data:
                    return field_data["items"]
                else:
                    logDetailedMessage(f"[OBTER CAMPO ESPECÍFICO CONTATO] O campo {key} não possui a propriedade 'items'.", LOG)
                    return field_data

    logDetailedMessage(f"[OBTER CAMPO ESPECÍFICO CONTATO] Campo {campo_personalizado} não encontrado nos contatos.", LOG)
    return None

# updateContactFields
# EN: Updates specific fields in a contact with new values
# PT: Atualiza campos específicos em um contato com novos valores
def updateContactFields(bitrix_webhook_url, contact_id, campos=None, data=None, LOG=False):
    """
    Atualiza campos específicos de um contato no Bitrix24.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param contact_id: ID do contato a ser modificado.
    :param campos: Lista de campos a serem preenchidos (ex: ["EMAIL", "PHONE", "UF_CRM_123"]).
    :param data: Lista de valores a serem inseridos, na mesma ordem dos campos.
    :param LOG: Se True, ativa logs detalhados.
    :return: True se a atualização for bem-sucedida, False caso contrário.
    """
    if not campos or not data or len(campos) != len(data):
        logDetailedMessage("[ATUALIZAR CAMPOS CONTATO] Erro: campos e dados devem ter o mesmo tamanho.", LOG)
        return False

    # Cria um dicionário combinando campos com seus respectivos valores
    fields_to_update = {}
    for campo, valor in zip(campos, data):
        fields_to_update[campo] = valor

    # Prepara os parâmetros para a requisição
    params = {
        "id": contact_id,
        "fields": fields_to_update
    }

    # Faz a requisição para atualizar os campos
    response = _bitrix_request("crm.contact.update", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[ATUALIZAR CAMPOS CONTATO] Dados atualizados com sucesso no contato ID {contact_id}", LOG)
        logDetailedMessage(f"[ATUALIZAR CAMPOS CONTATO] Campos atualizados: {fields_to_update}", LOG)
        return True

    logDetailedMessage(f"[ATUALIZAR CAMPOS CONTATO] Falha ao atualizar dados no contato ID {contact_id}", LOG)
    return False

# SPA Functions

# createSpaCard
# EN: Creates a new SPA card with basic and optional fields
# PT: Cria um novo card SPA com campos básicos e opcionais
def createSpaCard(title, stage_id, category_id, assigned_by_id, bitrix_webhook_url, contact_id=None, extra_fields=None, LOG=False):
    """
    Cria um novo card no pipeline do Bitrix24.

    Essa função adiciona um novo card dentro de um Smart Process Automation (SPA) no Bitrix24.

    :param title: Título do card (string).
    :param stage_id: ID do estágio inicial do card (string).
    :param category_id: ID da categoria do card (int ou string).
    :param assigned_by_id: ID do responsável pelo card (int ou string).
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param contact_id: (Opcional) ID do contato a ser vinculado ao card.
    :param extra_fields: (Opcional) Dicionário contendo campos extras para o card.
    :param LOG: Se True, ativa logs detalhados para depuração.

    :return: ID do card criado em caso de sucesso, ou None se falhar.
    """

    # Construção do payload com os campos obrigatórios
    params = {
        "entityTypeId": 128,  # ID padrão para SPA, pode ser ajustado conforme necessário
        "fields": {
            "title": title,
            "stageId": stage_id,
            "categoryId": category_id,
            "assignedById": assigned_by_id,
            "contactId": contact_id
        }
    }

    # Se houver campos extras, adicioná-los ao payload
    if extra_fields and isinstance(extra_fields, dict):
        params["fields"].update(extra_fields)

    # Chamada à API centralizada usando `_bitrix_request`
    response = _bitrix_request("crm.item.add", params, bitrix_webhook_url, LOG)

    # Verifica resposta e retorna o ID do card criado
    if response and "result" in response and "item" in response["result"]:
        card_id = response["result"]["item"].get("id")
        logDetailedMessage(f"[CRIAR CARD SPA] Card criado com sucesso. ID: {card_id}", LOG)
        return card_id

    logDetailedMessage("[CRIAR CARD SPA] Falha ao obter o ID do card criado.", LOG)
    return None

# getSpaCustomFields
# EN: Gets metadata for all custom fields in a SPA entity
# PT: Obtém metadados de todos os campos personalizados de uma entidade SPA
def getSpaCustomFields(entity_type_id, bitrix_webhook_url, LOG=False):
    """
    Obtém os metadados de todos os campos personalizados de uma entidade SPA no Bitrix24.

    :param entity_type_id: ID da entidade no Bitrix24.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Dicionário com os metadados de todos os campos personalizados ou None em caso de erro.
    """
    params = {"entityTypeId": entity_type_id}
    response = _bitrix_request("crm.item.fields", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[OBTER CAMPOS PERSONALIZADOS] Metadados obtidos para entityTypeId {entity_type_id}.", LOG)
        return response["result"]

    logDetailedMessage(f"[OBTER CAMPOS PERSONALIZADOS] Falha ao obter metadados para entityTypeId {entity_type_id}.", LOG)
    return None

# getSpaSpecificField
# EN: Gets metadata for a specific SPA custom field
# PT: Obtém metadados de um campo personalizado específico do SPA
def getSpaSpecificField(campo_personalizado, entity_type_id, bitrix_webhook_url, LOG=False):
    """
    Obtém os metadados de um campo personalizado específico no Bitrix24 e, se presente,
    retorna a propriedade "items" desse campo.

    :param campo_personalizado: Nome do campo personalizado (ex: ufCrm41_1737980514688).
    :param entity_type_id: ID da entidade SPA no Bitrix24.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.
    :return: Lista com os itens do campo ou o dicionário do campo se não possuir "items".
    """
    params = {"entityTypeId": entity_type_id}

    # Faz a requisição centralizada
    response = _bitrix_request("crm.item.fields", params, bitrix_webhook_url, LOG)

    if response and "result" in response and "fields" in response["result"]:
        campos = response["result"]["fields"]

        # Debug: log das chaves com repr para verificar espaços ou caracteres ocultos
        for key in campos:
            logDetailedMessage(f"[DEBUG] Chave encontrada: {repr(key)}", LOG)

        # Normaliza a comparação removendo espaços e convertendo para minúsculas
        campo_procura = campo_personalizado.strip().lower()

        for key in campos:
            if key.strip().lower() == campo_procura:
                logDetailedMessage(f"[OBTER CAMPO ESPECÍFICO] Campo encontrado: {key}", LOG)
                field_data = campos[key]
                if "items" in field_data:
                    return field_data["items"]
                else:
                    logDetailedMessage(f"[OBTER CAMPO ESPECÍFICO] O campo {key} não possui a propriedade 'items'.", LOG)
                    return field_data

    logDetailedMessage(f"[OBTER CAMPO ESPECÍFICO] Campo {campo_personalizado} não encontrado na entidade {entity_type_id}.", LOG)
    return None

#mapFieldValues
# EN: Maps numeric IDs to their corresponding text values in custom fields
# PT: Mapeia IDs numéricos para seus valores de texto correspondentes em campos personalizados
def mapFieldValues(campos, metadados):
    """
    Mapeia valores de IDs para os valores reais de campos personalizados do Bitrix24.

    Alguns campos personalizados no Bitrix24 armazenam valores como números (IDs) que representam textos.
    Essa função substitui esses IDs pelos valores reais.

    :param campos: Dicionário com os campos do item obtido do Bitrix24.
    :param metadados: Dicionário com os metadados dos campos personalizados.

    :return: Dicionário com os valores traduzidos (quando aplicável).
    """
    if not isinstance(campos, dict) or not isinstance(metadados, dict):
        return campos  # Retorna inalterado se os parâmetros não forem dicionários válidos

    for campo, valor in campos.items():
        # Verifica se o campo está nos metadados e se é do tipo "enumeration" (lista de seleção)
        if campo in metadados and metadados[campo].get("type") == "enumeration":
            opcoes = {str(item["ID"]): item["VALUE"] for item in metadados[campo].get("items", [])}

            if isinstance(valor, list):  # Se for uma seleção múltipla
                campos[campo] = [opcoes.get(str(v), v) for v in valor if v is not None]
            else:
                campos[campo] = opcoes.get(str(valor), valor) if valor is not None else valor

    return campos

# getSpaCardFields
# EN: Gets all fields from a specific SPA card with value translation
# PT: Obtém todos os campos de um card SPA específico com tradução de valores
def getSpaCardFields(entity_type_id, item_id, bitrix_webhook_url, LOG=False):
    """
    Obtém todos os campos de um item SPA específico no Bitrix24 e traduz os valores de listas de seleção.

    :param entity_type_id: ID da entidade SPA no Bitrix24 (ex: 128 para AdvEasy, 158 para Sittax, etc.).
    :param item_id: ID do item a ser consultado.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Dicionário com os campos formatados ou None em caso de erro.
    """
    params = {"entityTypeId": entity_type_id, "id": item_id}
    response = _bitrix_request("crm.item.get", params, bitrix_webhook_url, LOG)

    if response and "result" in response and "item" in response["result"]:
        campos = response["result"]["item"]
        logDetailedMessage(f"[OBTER CAMPOS] Campos obtidos com sucesso para item ID {item_id}.", LOG)

        # Obtém metadados para converter IDs para valores reais
        metadados = getSpaCustomFields(entity_type_id, bitrix_webhook_url, LOG)
        if metadados:
            campos = mapFieldValues(campos, metadados)

        return campos

    logDetailedMessage(f"[OBTER CAMPOS] Nenhum campo encontrado para item ID {item_id}.", LOG)
    return None

# getSpaCardByContactId
# EN: Finds SPA cards linked to a specific contact
# PT: Encontra cards SPA vinculados a um contato específico
def getSpaCardByContactId(contact_id, entity_type_id, bitrix_webhook_url, LOG=False):
    """
    Verifica se existe um Card SPA associado ao contato informado.

    Essa função busca um card (negócio, oportunidade, etc.) que esteja vinculado a um contato específico
    dentro de um Smart Process Automation (SPA) no Bitrix24.

    :param contact_id: ID do contato no Bitrix24.
    :param entity_type_id: Tipo da entidade no Bitrix24 (ex: 128 para AdvEasy, 158 para outra entidade).
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados para depuração.

    :return: ID do primeiro card associado ao contato ou None se não houver cards vinculados.
    """

    params = {
        "entityTypeId": entity_type_id,
        "filter": {"contactId": contact_id},
        "select": ["id"]
    }

    response = _bitrix_request("crm.item.list", params, bitrix_webhook_url, LOG)

    if response and "result" in response and "items" in response["result"]:
        items = response["result"]["items"]
        if items:
            card_id = items[0]["id"]  # Pega o primeiro card encontrado
            logDetailedMessage(f"[OBTER CARD SPA] Card encontrado para contato ID {contact_id}: {card_id}", LOG)
            return card_id

    logDetailedMessage(f"[OBTER CARD SPA] Nenhum card encontrado para contato ID {contact_id}.", LOG)
    return None

#moveSpaCardStage
# EN: Moves a card to a different stage in the pipeline
# PT: Move um card para um estágio diferente no pipeline
def moveSpaCardStage(stage_id, card_id, entity_type_id, bitrix_webhook_url, LOG=False):
    """
    Move um Card SPA para uma nova etapa no Bitrix24.

    Essa função altera o estágio de um card dentro de um Smart Process Automation (SPA) no Bitrix24.

    :param stage_id: Novo stageId para onde o card será movido.
    :param card_id: ID do card que será movido.
    :param entity_type_id: Tipo da entidade no Bitrix24 (ex: 128 para negócios).
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados para depuração.

    :return: True se a movimentação for bem-sucedida, False caso contrário.
    """

    params = {
        "entityTypeId": entity_type_id,
        "id": card_id,
        "fields": {"stageId": stage_id}
    }

    response = _bitrix_request("crm.item.update", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[MOVER ETAPA SPA] Card ID {card_id} movido com sucesso para stageId {stage_id}.", LOG)
        return True

    logDetailedMessage(f"[MOVER ETAPA SPA] Falha ao mover o Card ID {card_id} para stageId {stage_id}.", LOG)
    return False

# listSpaCards
# EN: Lists all cards in an SPA with optional filters and pagination
# PT: Lista todos os cards em um SPA com filtros opcionais e paginação
def listSpaCards(bitrix_webhook_url, entity_type_id, category_id=None, stage_id=None, returnFilter=None, LOG=False):
    """
    Lista TODOS os itens de um SPA no Bitrix24, sem limitações.
    """
    itens = []
    start = 0
    total_items = None

    # Define campos padrão caso returnFilter seja None
    default_fields = ["id", "title", "categoryId", "createdTime", "assignedById",
                     "stageId", "companyId", "contactId"]
    select_fields = returnFilter if returnFilter is not None else default_fields

    while True:
        params = {
            "entityTypeId": entity_type_id,
            "select": select_fields,
            "start": start
        }

        # Adiciona filtros se especificados
        if category_id is not None or stage_id is not None:
            params["filter"] = {}
            if category_id is not None:
                params["filter"]["categoryId"] = category_id
            if stage_id is not None:
                params["filter"]["stageId"] = stage_id

        response = _bitrix_request("crm.item.list", params, bitrix_webhook_url, LOG)

        if not response or "result" not in response:
            break

        items_page = response["result"].get("items", [])
        if not items_page:
            break

        # Atualiza o total de itens se ainda não foi definido
        if total_items is None and "total" in response["result"]:
            total_items = response["result"]["total"]

        # Adiciona itens encontrados
        if returnFilter is None:
            itens.extend(items_page)
        else:
            filtered_items = [{field: item.get(field) for field in returnFilter}
                            for item in items_page]
            itens.extend(filtered_items)

        if LOG:
            logDetailedMessage(f"[LISTAR ITENS SPA] Coletados {len(itens)} de {total_items} itens. Continuando a partir de {start}.", LOG)

        # Incrementa o start para a próxima página
        start += len(items_page)

        # Verifica se já coletamos todos os itens
        if total_items and len(itens) >= total_items:
            break

        # Pequena pausa para evitar sobrecarga na API
        time.sleep(0.1)

    if LOG:
        logDetailedMessage(f"[LISTAR ITENS SPA] Paginação finalizada. Total coletado: {len(itens)}", LOG)

    return itens

# deleteSpaCard
# EN: Deletes a card and optionally its linked contact and company
# PT: Exclui um card e opcionalmente seu contato e empresa vinculados
def deleteSpaCard(bitrix_webhook_url, entity_type_id, card_id, excludeAll=False, LOG=False):

    """
    Exclui um card SPA e opcionalmente seus dados relacionados (contato e empresa).

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param entity_type_id: ID do tipo de entidade (SPA).
    :param card_id: ID do card a ser excluído.
    :param excludeAll: Se True, exclui também o contato e empresa vinculados.
    :param LOG: Se True, ativa logs detalhados.
    :return: True se a exclusão for bem-sucedida, False caso contrário.
    """
    # Primeiro, obtém os dados do card se excludeAll=True
    if excludeAll:
        params = {
            "entityTypeId": entity_type_id,
            "id": card_id,
            "select": ["contactId", "companyId"]
        }

        card_data = _bitrix_request("crm.item.get", params, bitrix_webhook_url, LOG)

        if card_data and "result" in card_data and "item" in card_data["result"]:
            contact_id = card_data["result"]["item"].get("contactId")
            company_id = card_data["result"]["item"].get("companyId")

            logDetailedMessage(f"[EXCLUIR CARD SPA] Dados vinculados encontrados - Contato: {contact_id}, Empresa: {company_id}", LOG)

    # Exclui o card
    params = {
        "entityTypeId": entity_type_id,
        "id": card_id
    }

    response = _bitrix_request("crm.item.delete", params, bitrix_webhook_url, LOG)

    if not response or "result" not in response:
        logDetailedMessage(f"[EXCLUIR CARD SPA] Falha ao excluir card ID {card_id}", LOG)
        return False

    logDetailedMessage(f"[EXCLUIR CARD SPA] Card ID {card_id} excluído com sucesso", LOG)

    # Se excludeAll=True, exclui contato e empresa
    if excludeAll and card_data and "result" in card_data:
        if contact_id:
            contact_response = _bitrix_request("crm.contact.delete", {"id": contact_id}, bitrix_webhook_url, LOG)
            if contact_response and "result" in contact_response:
                logDetailedMessage(f"[EXCLUIR CARD SPA] Contato ID {contact_id} excluído com sucesso", LOG)
            else:
                logDetailedMessage(f"[EXCLUIR CARD SPA] Falha ao excluir contato ID {contact_id}", LOG)

        if company_id:
            company_response = _bitrix_request("crm.company.delete", {"id": company_id}, bitrix_webhook_url, LOG)
            if company_response and "result" in company_response:
                logDetailedMessage(f"[EXCLUIR CARD SPA] Empresa ID {company_id} excluída com sucesso", LOG)
            else:
                logDetailedMessage(f"[EXCLUIR CARD SPA] Falha ao excluir empresa ID {company_id}", LOG)

    return True

# clearSpaCardFields
# EN: Clears the content of specific fields in a SPA card
# PT: Limpa o conteúdo de campos específicos em um card SPA
def clearSpaCardFields(bitrix_webhook_url, entity_type_id, card_id, campos=None, LOG=False):
    """
    Limpa o conteúdo de campos específicos de um card SPA.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param entity_type_id: ID do tipo de entidade (SPA).
    :param card_id: ID do card a ser modificado.
    :param campos: Lista de campos a serem limpos (ex: ["ufCrm41_1737980095947", "ufCrm41_173798041242"]).
    :param LOG: Se True, ativa logs detalhados.
    :return: True se a limpeza for bem-sucedida, False caso contrário.
    """
    if not campos:
        logDetailedMessage("[LIMPAR CAMPOS CARD SPA] Nenhum campo especificado para limpeza.", LOG)
        return False

    # Cria um dicionário com os campos a serem limpos
    fields_to_clear = {}
    for campo in campos:
        fields_to_clear[campo] = None  # Define o valor como None para limpar o campo

    # Prepara os parâmetros para a requisição
    params = {
        "entityTypeId": entity_type_id,
        "id": card_id,
        "fields": fields_to_clear
    }

    # Faz a requisição para atualizar os campos
    response = _bitrix_request("crm.item.update", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[LIMPAR CAMPOS CARD SPA] Campos {campos} limpos com sucesso no card ID {card_id}", LOG)
        return True

    logDetailedMessage(f"[LIMPAR CAMPOS CARD SPA] Falha ao limpar campos {campos} no card ID {card_id}", LOG)
    return False

# updateSpaCardFields
# EN: Updates specific fields in a SPA card with new values
# PT: Atualiza campos específicos em um card SPA com novos valores
def updateSpaCardFields(bitrix_webhook_url, entity_type_id, card_id, campos=None, data=None, LOG=False):
    """
    Insere dados em campos específicos de um card SPA.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param entity_type_id: ID do tipo de entidade (SPA).
    :param card_id: ID do card a ser modificado.
    :param campos: Lista de campos a serem preenchidos (ex: ["ufCrm41_1737980095947", "ufCrm41_173798041242"]).
    :param data: Lista de valores a serem inseridos, na mesma ordem dos campos.
    :param LOG: Se True, ativa logs detalhados.
    :return: True se a inserção for bem-sucedida, False caso contrário.
    """
    if not campos or not data or len(campos) != len(data):
        logDetailedMessage("[INSERIR CAMPOS CARD SPA] Erro: campos e dados devem ter o mesmo tamanho.", LOG)
        return False

    # Cria um dicionário combinando campos com seus respectivos valores
    fields_to_update = {}
    for campo, valor in zip(campos, data):
        fields_to_update[campo] = valor

    # Prepara os parâmetros para a requisição
    params = {
        "entityTypeId": entity_type_id,
        "id": card_id,
        "fields": fields_to_update
    }

    # Faz a requisição para atualizar os campos
    response = _bitrix_request("crm.item.update", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[INSERIR CAMPOS CARD SPA] Dados inseridos com sucesso no card ID {card_id}", LOG)
        logDetailedMessage(f"[INSERIR CAMPOS CARD SPA] Campos atualizados: {fields_to_update}", LOG)
        return True

    logDetailedMessage(f"[INSERIR CAMPOS CARD SPA] Falha ao inserir dados no card ID {card_id}", LOG)
    return False

# Employees

# listEmployees
# EN: Lists all employees registered in Bitrix24 with their details
# PT: Lista todos os funcionários cadastrados no Bitrix24 com seus detalhes
def listEmployees(bitrix_webhook_url, returnFilter=None, LOG=False):
    """
    Obtém a lista de todos os funcionários cadastrados no Bitrix24.

    Esta função retorna informações detalhadas sobre os funcionários,
    como ID, nome, email, departamento, cargo, etc.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param returnFilter: (Opcional) Lista de campos específicos a serem retornados.
                        Se None, retorna todos os campos disponíveis.
    :param LOG: Se True, ativa logs detalhados.
    :return: Lista de dicionários contendo os dados dos funcionários.
    """
    employees = []
    start = 0
    page_size = 50

    # Define campos padrão caso returnFilter seja None
    default_fields = [
        "ID", "NAME", "LAST_NAME", "EMAIL", "WORK_POSITION",
        "PERSONAL_PHONE", "WORK_PHONE", "DEPARTMENT", "ACTIVE",
        "DATE_REGISTER", "PERSONAL_PHOTO"
    ]

    select_fields = returnFilter if returnFilter is not None else default_fields

    while True:
        params = {
            "FILTER": {"ACTIVE": True},  # Busca apenas funcionários ativos por padrão
            "SELECT": select_fields,
            "start": start
        }

        response = _bitrix_request("user.get", params, bitrix_webhook_url, LOG)

        if response and "result" in response:
            employees_page = response["result"]

            if not employees_page:
                logDetailedMessage("[LISTAR FUNCIONÁRIOS] Nenhum funcionário encontrado.", LOG)
                break

            # Se returnFilter for None, adiciona todos os campos
            # Se não, filtra apenas os campos solicitados
            if returnFilter is None:
                employees.extend(employees_page)
            else:
                filtered_items = []
                for employee in employees_page:
                    filtered_employee = {field: employee.get(field) for field in returnFilter}
                    filtered_items.append(filtered_employee)
                employees.extend(filtered_items)

            # Verifica se há mais páginas
            if len(employees_page) < page_size:
                logDetailedMessage(f"[LISTAR FUNCIONÁRIOS] Paginação finalizada. Total coletado: {len(employees)}", LOG)
                break

            start += page_size
            logDetailedMessage(f"[LISTAR FUNCIONÁRIOS] Coletados {len(employees)} funcionários. Continuando a partir de {start}.", LOG)
        else:
            logDetailedMessage("[LISTAR FUNCIONÁRIOS] Falha ao obter os funcionários ou resposta vazia.", LOG)
            break

    return employees

# Leads

# getLeadFields
# EN: Retrieves all fields from a specific lead
# PT: Obtém todos os campos de um lead específico
def getLeadFields(lead_id, bitrix_webhook_url, LOG=False):
    """
    Obtém todos os campos de um lead específico no Bitrix24.

    Esta função retorna todos os campos associados a um lead,
    incluindo campos padrão e personalizados.

    :param lead_id: ID do lead a ser consultado.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Dicionário com os campos do lead ou None em caso de erro.
    """
    params = {"id": lead_id}
    response = _bitrix_request("crm.lead.get", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        lead = response["result"]
        logDetailedMessage(f"[OBTER CAMPOS LEAD] Campos obtidos com sucesso para lead ID {lead_id}.", LOG)
        return lead

    logDetailedMessage(f"[OBTER CAMPOS LEAD] Nenhum lead encontrado para ID {lead_id}.", LOG)
    return None

# createLead
# EN: Creates a new lead with optional fields
# PT: Cria um novo lead com campos opcionais
def createLead(bitrix_webhook_url, fields=None, LOG=False):
    """
    Cria um novo lead no Bitrix24.

    Esta função permite criar um lead vazio ou com campos específicos.
    Os campos podem incluir informações como título, nome, email, telefone, etc.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param fields: (Opcional) Dicionário com campos e valores para o lead.
                  Exemplo: {
                      "NAME": "João Silva",
                      "EMAIL": [{"VALUE": "joao@email.com", "VALUE_TYPE": "WORK"}],
                      "PHONE": [{"VALUE": "11999999999", "VALUE_TYPE": "WORK"}],
                      "COMMENTS": "Observações do lead"
                  }
    :param LOG: Se True, ativa logs detalhados.
    :return: ID do lead criado em caso de sucesso, None em caso de erro.
    """
    # Prepara os parâmetros para a requisição
    params = {
        "fields": fields if fields else {}
    }

    # Remove o título se existir para usar o padrão do Bitrix
    if fields and "TITLE" in fields:
        del params["fields"]["TITLE"]

    # Faz a requisição para criar o lead
    response = _bitrix_request("crm.lead.add", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        lead_id = response["result"]
        logDetailedMessage(f"[CRIAR LEAD] Lead criado com sucesso. ID: {lead_id}", LOG)
        return lead_id

    logDetailedMessage("[CRIAR LEAD] Falha ao criar lead.", LOG)
    return None

# Company

# createCompany
# EN: Creates a new company with optional fields
# PT: Cria uma nova empresa com campos opcionais
def createCompany(bitrix_webhook_url, fields=None, LOG=False):
    """
    Cria uma nova empresa no Bitrix24.

    Esta função permite criar uma empresa vazia ou com campos específicos.
    Os campos podem incluir informações como título, telefone, email, endereço, etc.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param fields: (Opcional) Dicionário com campos e valores para a empresa.
                  Exemplo: {
                      "TITLE": "Empresa XYZ",
                      "COMPANY_TYPE": "CUSTOMER",
                      "EMAIL": [{"VALUE": "contato@empresa.com", "VALUE_TYPE": "WORK"}],
                      "PHONE": [{"VALUE": "11999999999", "VALUE_TYPE": "WORK"}],
                      "INDUSTRY": "IT",
                      "COMMENTS": "Observações da empresa"
                  }
    :param LOG: Se True, ativa logs detalhados.
    :return: ID da empresa criada em caso de sucesso, None em caso de erro.
    """
    # Prepara os parâmetros para a requisição
    params = {
        "fields": fields if fields else {}
    }

    # Faz a requisição para criar a empresa
    response = _bitrix_request("crm.company.add", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        company_id = response["result"]
        logDetailedMessage(f"[CRIAR EMPRESA] Empresa criada com sucesso. ID: {company_id}", LOG)
        return company_id

    logDetailedMessage("[CRIAR EMPRESA] Falha ao criar empresa.", LOG)
    return None

# getCompanyFields
# EN: Retrieves all fields from a specific company
# PT: Obtém todos os campos de uma empresa específica
def getCompanyFields(company_id, bitrix_webhook_url, LOG=False):
    """
    Obtém todos os campos de uma empresa específica no Bitrix24.

    Esta função retorna todos os campos associados a uma empresa,
    incluindo campos padrão e personalizados.

    :param company_id: ID da empresa a ser consultada.
    :param bitrix_webhook_url: URL base do webhook do Bitrix24.
    :param LOG: Se True, ativa logs detalhados.

    :return: Dicionário com os campos da empresa ou None em caso de erro.
    """
    params = {"id": company_id}
    response = _bitrix_request("crm.company.get", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        company = response["result"]
        logDetailedMessage(f"[OBTER CAMPOS EMPRESA] Campos obtidos com sucesso para empresa ID {company_id}.", LOG)
        return company

    logDetailedMessage(f"[OBTER CAMPOS EMPRESA] Nenhuma empresa encontrada para ID {company_id}.", LOG)
    return None

# clearCompanyFields
# EN: Clears the content of specific fields in a company
# PT: Limpa o conteúdo de campos específicos em uma empresa
def clearCompanyFields(bitrix_webhook_url, company_id, campos=None, LOG=False):
    """
    Limpa o conteúdo de campos específicos de uma empresa.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param company_id: ID da empresa a ser modificada.
    :param campos: Lista de campos a serem limpos (ex: ["ufCrm41_1737980095947", "ufCrm41_173798041242"]).
    :param LOG: Se True, ativa logs detalhados.
    :return: True se a limpeza for bem-sucedida, False caso contrário.
    """
    if not campos:
        logDetailedMessage("[LIMPAR CAMPOS EMPRESA] Nenhum campo especificado para limpeza.", LOG)
        return False

    # Cria um dicionário com os campos a serem limpos
    fields_to_clear = {}
    for campo in campos:
        fields_to_clear[campo] = None  # Define o valor como None para limpar o campo

    # Prepara os parâmetros para a requisição
    params = {
        "id": company_id,
        "fields": fields_to_clear
    }

    # Faz a requisição para atualizar os campos
    response = _bitrix_request("crm.company.update", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[LIMPAR CAMPOS EMPRESA] Campos {campos} limpos com sucesso na empresa ID {company_id}", LOG)
        return True

    logDetailedMessage(f"[LIMPAR CAMPOS EMPRESA] Falha ao limpar campos {campos} na empresa ID {company_id}", LOG)
    return False

# updateCompanyFields
# EN: Updates specific fields in a company with new values
# PT: Atualiza campos específicos em uma empresa com novos valores
def updateCompanyFields(bitrix_webhook_url, company_id, campos=None, data=None, LOG=False):
    """
    Insere dados em campos específicos de uma empresa.

    :param bitrix_webhook_url: URL do webhook do Bitrix24.
    :param company_id: ID da empresa a ser modificada.
    :param campos: Lista de campos a serem preenchidos (ex: ["ufCrm41_1737980095947", "ufCrm41_173798041242"]).
    :param data: Lista de valores a serem inseridos, na mesma ordem dos campos.
    :param LOG: Se True, ativa logs detalhados.
    :return: True se a inserção for bem-sucedida, False caso contrário.
    """
    if not campos or not data or len(campos) != len(data):
        logDetailedMessage("[INSERIR CAMPOS EMPRESA] Erro: campos e dados devem ter o mesmo tamanho.", LOG)
        return False

    # Cria um dicionário combinando campos com seus respectivos valores
    fields_to_update = {}
    for campo, valor in zip(campos, data):
        fields_to_update[campo] = valor

    # Prepara os parâmetros para a requisição
    params = {
        "id": company_id,
        "fields": fields_to_update
    }

    # Faz a requisição para atualizar os campos
    response = _bitrix_request("crm.company.update", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[INSERIR CAMPOS EMPRESA] Dados inseridos com sucesso na empresa ID {company_id}", LOG)
        logDetailedMessage(f"[INSERIR CAMPOS EMPRESA] Campos atualizados: {fields_to_update}", LOG)
        return True

    logDetailedMessage(f"[INSERIR CAMPOS EMPRESA] Falha ao inserir dados na empresa ID {company_id}", LOG)
    return False

# searchCompanyByField
# EN: Searches for companies that have a specified value in a given field and returns selected fields
# PT: Busca empresas que possuam um valor especificado em um campo informado e retorna os campos selecionados
def searchCompanyByField(bitrix_webhook_url, search_field, value, select_fields=None, LOG=False):
    """
    Searches for companies that have the specified value in the given field.
    If select_fields is None, returns all available fields including custom fields.

    :param bitrix_webhook_url: URL of the Bitrix24 webhook.
    :param search_field: The field name to use for the search (e.g., "ID" or "ufCrm5_1737545372279").
    :param value: The value to search for in the specified field.
    :param select_fields: List of field names to return. If None, returns all fields.
    :param LOG: If True, detailed logs are enabled.
    :return: A list of companies matching the search criteria with the selected fields, or None if the search fails.
    """
    if select_fields is None:
        select_fields = ["*", "UF_*"]

    params = {
        "filter": {
            search_field: value
        },
        "select": select_fields
    }

    logDetailedMessage(f"[SEARCH COMPANY] Searching for companies where {search_field} equals {value}.", LOG)

    # Make the request to fetch the companies
    response = _bitrix_request("crm.company.list", params, bitrix_webhook_url, LOG)

    if response and "result" in response:
        logDetailedMessage(f"[SEARCH COMPANY] Successfully found companies for {search_field} = {value}.", LOG)
        return response["result"]

    logDetailedMessage(f"[SEARCH COMPANY] Failed to find companies for {search_field} = {value}.", LOG)
    return None
