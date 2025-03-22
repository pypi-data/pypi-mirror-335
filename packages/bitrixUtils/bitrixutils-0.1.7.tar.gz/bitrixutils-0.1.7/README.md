# BitrixUtils

A comprehensive Python library for seamless integration with Bitrix24's API, providing utilities for managing contacts, addresses, and Smart Process Automation (SPA) cards.

## 👨‍💻 Author
[@RafaelZelak](https://github.com/RafaelZelak)

## 📦 Installation

```bash
pip install bitrixUtils
```

## 🚀 Quick Start

### Import Methods
**Method 1: Direct Function Import**

Import specific functions directly from the library. This is recommended when you only need certain functions:

```python
from bitrixUtils import createContact, updateSpaCardFields, listEmployees

# Usage example
createContact(contact_data, cpf_field, webhook_url)
updateSpaCardFields(deal_id, fields_to_update, webhook_url)
```
**Method 2: Namespace Import**

Import the entire library with a shorter alias. This helps maintain clean namespace while accessing all functionality:

```python
import bitrixUtils as bx

# Usage example
bx.createContact(contact_data, cpf_field, webhook_url)
bx.updateSpaCardFields(deal_id, fields_to_update, webhook_url)
```

**Method 3: Import All**

Import all functions directly into the current namespace. Use with caution as it might lead to naming conflicts:
```python
from bitrixUtils import *

# Usage example
createContact(contact_data, cpf_field, webhook_url)
updateSpaCardFields(deal_id, fields_to_update, webhook_url)
```

## 🔑 Understanding Bitrix24 API

### Webhook Structure
The Bitrix24 REST API uses webhooks for authentication. A webhook URL has this format:
```
https://your-domain.bitrix24.com/rest/USER_ID/WEBHOOK_TOKEN/
```
- `your-domain`: Your Bitrix24 domain
- `USER_ID`: The ID of the user who created the webhook
- `WEBHOOK_TOKEN`: A unique token for authentication

### API Methods
Bitrix24 API methods follow this pattern:
```
METHOD_CATEGORY.ACTION
```
Common examples:
- `crm.contact.add` - Create contact
- `crm.item.add` - Create SPA card
- `crm.item.update` - Update SPA card
- `crm.contact.get` - Get contact details

### Request Structure
```python
{
    "method": "crm.item.add",
    "params": {
        "entityTypeId": 128,
        "fields": {
            "title": "Card Title",
            "stageId": "DT123",
            # other fields...
        }
    }
}
```

## 🔍 Important Bitrix24 IDs Explained

### entity_type_id
- What: Identifies the type of entity in Bitrix24
- Common values:
  - `3`: Contacts
  - `4`: Companies
  - `2`: Deals
  - `128+`: Smart Process Automation (varies by installation)
- Example: Used in `createSpaCard(entity_type_id=128)`

### card_id
- What: Unique identifier for a SPA card
- Format: Integer (e.g., 42789)
- Where to find: In card URL or via API response
- Example: Used in `updateSpaCardFields(card_id=42789)`

### category_id
- What: Identifies the pipeline category
- Format: Integer (e.g., 42)
- Where to find: In pipeline settings
- Example: Used in `listSpaCards(category_id=42)`

### stage_id
- What: Identifies the stage in a pipeline
- Format: String (e.g., "DT123")
- Structure: Usually starts with "DT" followed by numbers
- Example: Used in `moveSpaCardStage(stage_id="DT123")`

### assigned_by_id
- What: ID of the Bitrix24 user responsible for the card
- Format: Integer (e.g., 789)
- Where to find: In user profile or via API
- Example: Used in `createSpaCard(assigned_by_id=789)`

### contact_id
- What: Unique identifier for a contact
- Format: Integer (e.g., 456)
- Where to find: In contact URL or via API
- Example: Used in `createSpaCard(contact_id=456)`

## 📚 Detailed Function Documentation

### Contact Management

#### Create Contact
```python
contact_data = {
    "cpf": "123.456.789-00",
    "name": "John Doe",
    "email": "john@example.com",
    "celular": "(11) 98765-4321"
}

contact_id = core.createContact(
    contact_data=contact_data,
    cpf_field="UF_CRM_XXXXX",
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    extra_fields={"FIELD_ID": "value"},
    LOG=True
)
```

### SPA Card Management

#### Create SPA Card
```python
card_id = core.createSpaCard(
    title="New Project",
    stage_id="DT123",
    category_id=42,
    assigned_by_id=789,
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    contact_id=456,
    extra_fields={"UF_CRM_FIELD": "value"},
    LOG=True
)
```

[Continue previous examples...]

## 🔧 API Technical Details

### Headers
```python
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
```

### Common Response Structure
```python
{
    "result": {
        "item": {
            "id": 42789,
            "title": "Card Title",
            # other fields...
        }
    },
    "time": {
        "start": 1582117322.125375,
        "finish": 1582117322.256984,
        "duration": 0.131609,
        "processing": 0.131371,
        "date_start": "2024-02-19T12:55:22+03:00",
        "date_finish": "2024-02-19T12:55:22+03:00"
    }
}
```

### Error Handling
```python
{
    "error": "ERROR_CODE",
    "error_description": "Error description"
}
```

Common error codes:
- `PORTAL_DELETED`: Portal was deleted
- `ERROR_METHOD_NOT_FOUND`: Invalid method
- `ERROR_INTERNAL`: Internal server error

## 🔄 Pagination
Bitrix24 uses cursor-based pagination:
```python
{
    "next": 50,  # Next page cursor
    "total": 156,  # Total items
    "result": {
        "items": [...]
    }
}
```

## 📝 Custom Fields
Custom fields in Bitrix24 follow this naming pattern:
```
UF_CRM_FIELD_ID
```
Example: `UF_CRM_1737980095947`

## 🔒 Security Considerations
- Store webhook URLs securely
- Use environment variables
- Implement rate limiting
- Handle token expiration

## 🐛 Debug Mode
Enable detailed logging:
```python
LOG=True  # Enables detailed logging
```

## 📝 Function Examples

### Contact Functions

#### Get Contact Type IDs
```python
# Get all possible contact types
type_ids = core.getTypeId(
    bitrixWebhookUrl=BITRIX_WEBHOOK_URL,
    LOG=True
)
print(type_ids)  # {'CLIENT': 'Client', 'SUPPLIER': 'Supplier', ...}
```

### SPA Card Functions

#### List SPA Cards
```python
# List all cards in a specific category
cards = core.listSpaCards(
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    entity_type_id=128,
    category_id=42,
    stage_id="DT123",  # Optional
    returnFilter=["id", "title", "contactId"],  # Optional
    LOG=True
)
print(f"Found {len(cards)} cards")
```

#### Delete SPA Card
```python
# Delete a card and its related data
success = core.deleteSpaCard(
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    entity_type_id=128,
    card_id=42789,
    excludeAll=True,  # Will also delete linked contact and company
    LOG=True
)
print("Card deleted successfully" if success else "Failed to delete card")
```

#### Clear SPA Card Fields
```python
# Clear specific fields in a card
fields_to_clear = ["ufCrm41_1737980095947", "ufCrm41_173798041242"]
success = core.clearSpaCardFields(
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    entity_type_id=128,
    card_id=42789,
    campos=fields_to_clear,
    LOG=True
)
print("Fields cleared successfully" if success else "Failed to clear fields")
```

#### Update SPA Card Fields
```python
# Update specific fields with new values
fields = ["ufCrm41_1737980095947", "ufCrm41_173798041242"]
values = ["New Value 1", "New Value 2"]
success = core.updateSpaCardFields(
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    entity_type_id=128,
    card_id=42789,
    campos=fields,
    data=values,
    LOG=True
)
print("Fields updated successfully" if success else "Failed to update fields")
```

#### Move SPA Card Stage
```python
# Move card to a different pipeline stage
success = core.moveSpaCardStage(
    stage_id="DT456",
    card_id=42789,
    entity_type_id=128,
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    LOG=True
)
print("Card moved successfully" if success else "Failed to move card")
```

#### List SPA Entities
```python
# Get all available SPA entities
entities = core.listSpaEntities(
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    LOG=True
)
print("Available entities:", entities)
```

#### Get SPA Card by Contact ID
```python
# Find cards linked to a specific contact
cards = core.getSpaCardByContactId(
    contact_id=456,
    entity_type_id=128,
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    LOG=True
)
print("Found cards:", cards)
```

#### Get SPA Card Fields
```python
# Get all fields from a specific card with value translation
fields = core.getSpaCardFields(
    entity_type_id=128,
    item_id=42789,
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    LOG=True
)
print("Card fields:", fields)
```

### Complete Flow Example
```python
# Example of a complete workflow
from bitrixUtils import core

# Setup
BITRIX_WEBHOOK_URL = "https://your-domain.bitrix24.com/rest/XXX/YYYYY/"

# 1. Create a contact
contact_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "cpf": "123.456.789-00"
}
contact_id = core.createContact(contact_data, "UF_CRM_CPF", BITRIX_WEBHOOK_URL)

# 2. Create a SPA card linked to the contact
card_id = core.createSpaCard(
    title="New Project",
    stage_id="DT123",
    category_id=42,
    assigned_by_id=789,
    contact_id=contact_id,
    bitrix_webhook_url=BITRIX_WEBHOOK_URL
)

# 3. Update card fields
core.updateSpaCardFields(
    bitrix_webhook_url=BITRIX_WEBHOOK_URL,
    entity_type_id=128,
    card_id=card_id,
    campos=["ufCrm41_status"],
    data=["In Progress"]
)

# 4. Move card to next stage
core.moveSpaCardStage(
    stage_id="DT456",
    card_id=card_id,
    entity_type_id=128,
    bitrix_webhook_url=BITRIX_WEBHOOK_URL
)
```

## 📄 License
MIT

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
