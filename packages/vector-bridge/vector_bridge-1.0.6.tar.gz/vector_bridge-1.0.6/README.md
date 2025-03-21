# VectorBridge Python Client

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python client for interacting with the [VectorBridge.ai](https://vectorbridge.ai) API. This client provides complete access to all aspects of the VectorBridge platform including authentication, user management, AI processing, vector operations, and more.

## Installation

```bash
pip install vector-bridge
```

## Quick Start

### Initialize the Client

For user authentication (admin access):

```python
from vector_bridge import VectorBridgeClient

# Initialize the client
client = VectorBridgeClient(integration_name="default")

# Login with credentials
client.login(username="your_email@example.com", password="your_password")

# Check if API is accessible
status = client.ping()  # Should return "OK"
```

For API key authentication (application access):

```python
from vector_bridge import VectorBridgeClient

# Initialize with API key
client = VectorBridgeClient(
    integration_name="default", 
    api_key="your_api_key"
)
```

## Authentication Methods

### Username/Password Authentication (Admin Access)

```python
from vector_bridge import VectorBridgeClient

client = VectorBridgeClient(integration_name="default")
token = client.login(username="your_email@example.com", password="your_password")

# Now you can access admin functionality
me = client.admin.user.get_me()
print(f"Logged in as: {me.email}")
```

### API Key Authentication (Application Access)

```python
from vector_bridge import VectorBridgeClient, SortOrder

client = VectorBridgeClient(
    integration_name="default", 
    api_key="your_api_key"
)

# Process a message with AI
response = client.ai_message.process_message_stream(
    content="What can you tell me about vector databases?",
    user_id="user123"
)

# Print the streaming response
for chunk in response.chunks:
    print(chunk, end="")

# Get the complete message after streaming
complete_message = response.message
```

## Core Features

### AI Message Processing

Process messages and get AI responses with streaming support:

```python
# Process a message and get streaming AI response
message_stream = client.ai_message.process_message_stream(
    content="Tell me about artificial intelligence",
    user_id="user123"
)

# Print the streaming response chunks
for chunk in message_stream.chunks:
    print(chunk, end="")

# Access the complete message
whole_message = message_stream.message
```

Process messages and get a Pydantic model as a response:

```python
# Define Pydantic models
class Crew(BaseModel):
    name: str

class MoonLandingDetails(BaseModel):
    landing_year: int
    landing_month: int
    landing_day: int
    crew: List[Crew]

# Process a message and get Pydantic model response
message_model = user_client.ai_message.process_message_json(
    response_model=MoonLandingDetails,
    content="Details about moon landing",
    user_id="user123"
)
```

Retrieve conversation history:

```python
# From DynamoDB
messages = client.ai_message.fetch_messages_from_dynamo_db(
    user_id="user123",
    sort_order=SortOrder.DESCENDING,
    limit=50
)

# From Vector Database with semantic search capability
messages = client.ai_message.fetch_messages_from_vector_db(
    user_id="user123",
    near_text="machine learning"
)
```

### AI Agents

```python
# Set a specific agent for a user conversation
chat = client.ai.set_current_agent(
    user_id="user123",
    agent_name="sales_manager"
)

# Provide core knowledge for an agent
chat = client.ai.set_core_knowledge(
    user_id="user123",
    core_knowledge={
        "product_line": ["widgets", "gadgets"],
        "company_info": "Founded in 2020"
    }
)
```

### Function Execution

```python
# Execute a previously defined function
result = client.functions.run_function(
    function_name="calculator",
    function_args={
        "a": 10,
        "b": 5,
        "operation": "multiply"
    }
)

print(f"Result: {result}")
```

### Vector Database Queries

```python
# Run a semantic search query
results = client.queries.run_search_query(
    vector_schema="Documents",
    query_args={
        "content": "artificial intelligence applications",
        "full_document": False
    }
)

# Find similar documents based on a reference document
similar_docs = client.queries.run_find_similar_query(
    vector_schema="Documents",
    query_args={
        "uuid": "8c03ff2f-36f9-45f7-9918-48766c968f45"
    }
)
```

## Admin Functionality

### User Management

```python
# Get current user info
me = client.admin.user.get_me()

# Update user details
updated_me = client.admin.user.update_me(
    user_data=UserUpdate(
        full_name="John Doe",
        phone_number="+1234567890",
        country="US",
        city="New York"
    )
)

# Change password
client.admin.user.change_password(
    old_password="current_password", 
    new_password="new_secure_password"
)

# Add an agent user
new_agent = client.admin.user.add_agent(
    email="agent@example.com",
    first_name="Agent",
    last_name="User",
    password="secure_password"
)

# List users in your organization
users = client.admin.user.get_users_in_my_organization()

# Get user by ID or email
user = client.admin.user.get_user_by_id("user_id")
user = client.admin.user.get_user_by_email("user@example.com")
```

### Security Groups

```python
# Create a security group
sg = client.admin.security_groups.create_security_group(
    security_group_data=SecurityGroupCreate(
        group_name="Content Creators",
        description="Users who can create and edit content"
    )
)

# List security groups
security_groups = client.admin.security_groups.list_security_groups()

# Update security group permissions
permissions = security_groups.security_groups[0].group_permissions
permissions.logs.read = True
updated_sg = client.admin.security_groups.update_security_group(
    group_id=security_groups.security_groups[0].uuid,
    security_group_data=SecurityGroupUpdate(permissions=permissions)
)

# Get security group details
sg = client.admin.security_groups.get_security_group(group_id="group_id")

# Delete security group
client.admin.security_groups.delete_security_group(group_id="group_id")
```

### Integration Management

```python
# List all integrations
integrations = client.admin.integrations.get_integrations_list()

# Get integration by name
integration = client.admin.integrations.get_integration_by_name("default")

# Get integration by ID
integration = client.admin.integrations.get_integration_by_id("integration_id")

# Create a new integration
new_integration = client.admin.integrations.add_integration(
    integration_data=IntegrationCreate(
        integration_name="API Integration",
        integration_description="Integration for API access",
        openai_api_key="sk-your-openai-key",
        weaviate_url="https://your-weaviate-instance.cloud",
        weaviate_api_key="your-weaviate-key"
    )
)

# Update integration settings
updated = client.admin.integrations.update_integration_weaviate(
    weaviate_key=WeaviateKey.MAX_SIMILARITY_DISTANCE,
    weaviate_value=0.7
)

# Update AI provider API key
updated = client.admin.integrations.update_integration_ai_api_key(
    api_key="your-api-key",
    ai_provider=AIProviders.DEEP_SEEK
)

# Update message storage mode
updated = client.admin.integrations.update_message_storage_mode(
    message_storage_mode=MessageStorageMode.DYNAMO_DB
)

# Update environment variables
updated = client.admin.integrations.update_environment_variables(
    env_variables={
        "API_KEY": "value1",
        "SECRET": "value2"
    }
)

# Delete an integration
client.admin.integrations.delete_integration("integration_name")
```

### User Access Management

```python
# Add user to integration
users_in_integration = client.admin.integrations.add_user_to_integration(
    user_id="user_id",
    security_group_id="security_group_id"
)

# Remove user from integration
users_in_integration = client.admin.integrations.remove_user_from_integration(
    user_id="user_id"
)

# Update user's security group
users = client.admin.integrations.update_users_security_group(
    security_group_id="new_group_id",
    user_id="user_id"
)

# Get users in an integration
users = client.admin.integrations.get_users_from_integration()
```

### Instructions Management

```python
# Create an instruction
instruction = client.admin.instructions.add_instruction(
    instruction_data=InstructionCreate(
        instruction_name="Sales Assistant",
        description="Instruction for sales assistance",
        open_ai_api_key="sk-your-openai-key"
    )
)

# Get instruction by name
instruction = client.admin.instructions.get_instruction_by_name("Sales Assistant")

# Get instruction by ID
instruction = client.admin.instructions.get_instruction_by_id("instruction_id")

# List instructions
instructions = client.admin.instructions.list_instructions()

# Delete instruction
client.admin.instructions.delete_instruction("instruction_id")
```

### Function Management

```python
# Create a function
function = client.admin.functions.add_function(
    function_data=FunctionCreate(
        function_name="calculator",
        description="Perform math operations",
        function_action=GPTActions.CODE_EXEC,
        code="import math, os\nresult = math.pow(float(os.getenv(base)), float(os.getenv(exponent)))\nprint(f'Result: {result}')",
        function_parameters=FunctionParametersStorageStructure(
            properties=[
                FunctionPropertyStorageStructure(
                    name="base",
                    description="Base number"
                ),
                FunctionPropertyStorageStructure(
                    name="exponent",
                    description="Exponent"
                )
            ]
        )
    )
)

# Get function by name
function = client.admin.functions.get_function_by_name("calculator")

# Get function by ID
function = client.admin.functions.get_function_by_id("function_id")

# Update a function
updated_function = client.admin.functions.update_function(
    function_id="function_id",
    function_data=FunctionUpdate(
        description="Updated function description",
        code="print('Updated function code')"
    )
)

# List functions
functions = client.admin.functions.list_functions()

# List default functions
default_functions = client.admin.functions.list_default_functions()

# Execute a function
result = client.admin.functions.run_function(
    function_name="calculator",
    function_args={
        "base": 2,
        "exponent": 8
    }
)

# Delete a function
client.admin.functions.delete_function("function_id")
```

### API Key Management

```python
# Create an API key
api_key = client.admin.api_keys.create_api_key(
    api_key_data=APIKeyCreate(
        key_name="Client API Key",
        user_id="user_id",
        expire_days=30,
        monthly_request_limit=10000
    )
)

# Get API key details
api_key = client.admin.api_keys.get_api_key("api_key")

# List all API keys
api_keys = client.admin.api_keys.list_api_keys()

# Delete an API key
client.admin.api_keys.delete_api_key("api_key")
```

### Chat Management

```python
# Get all chats in my organization
chats = client.admin.chat.fetch_chats_for_my_organization(
    integration_name="default"
)

# Get my chats
my_chats = client.admin.chat.fetch_my_chats(
    integration_name="default"
)

# Delete a chat
client.admin.chat.delete_chat(
    user_id="user_id"
)
```

### Internal Message Processing

```python
# Process an internal message with AI
message_stream = client.admin.message.process_internal_message(
    content="Write a product description for our new AI-powered toaster",
    suffix="marketing_team",
    integration_name="default"
)

for chunk in message_stream.chunks:
    print(chunk)

full_message = message_stream.message
```

### AI Knowledge Management

#### File Storage

```python
# Create a folder
folder = client.admin.ai_knowledge.file_storage.create_folder(
    folder_name="Project Documents",
    folder_description="Documentation for our project",
    private=True
)

# Upload a file
file_upload = client.admin.ai_knowledge.file_storage.upload_file(
    file_path="document.pdf",
    file_name="project-specs.pdf",
    parent_id=folder.uuid,
    private=True,
    tags=["project", "documentation"]
)

for progress in file_upload.progress_updates:
    print(progress)

result = file.item

# Rename a file
renamed_file = client.admin.ai_knowledge.file_storage.rename_file_or_folder(
    item_id=file.uuid,
    new_name="updated-specs.pdf"
)

# Update file properties
client.admin.ai_knowledge.file_storage.update_file_or_folder_tags(
    item_id=file.uuid,
    tags=["important", "reference"]
)

client.admin.ai_knowledge.file_storage.update_file_or_folder_starred(
    item_id=file.uuid,
    is_starred=True,
)

# Get file details
file = client.admin.ai_knowledge.file_storage.get_file_or_folder(
    item_id="file_id"
)

# Get file path
path = client.admin.ai_knowledge.file_storage.get_file_or_folder_path(
    item_id="file_id"
)

# List files and folders
items = client.admin.ai_knowledge.file_storage.list_files_and_folders(
    filters=AIKnowledgeFileSystemFilters(
        parent_id=folder.uuid
    )
)

# Count files and folders
count = client.admin.ai_knowledge.file_storage.count_files_and_folders(
    parents=[folder.uuid]
)

# Get download link
download_link = client.admin.ai_knowledge.file_storage.get_download_link_for_document(
    item_id="file_id"
)

# Grant user access to a file
client.admin.ai_knowledge.file_storage.grant_or_revoke_user_access(
    item_id="file_id",
    user_id="user_id",
    has_access=True,
    access_type=FileAccessType.READ
)

# Grant security group access
client.admin.ai_knowledge.file_storage.grant_or_revoke_security_group_access(
    item_id="file_id",
    group_id="group_id",
    has_access=True,
    access_type=FileAccessType.READ
)

# Delete a file or folder
client.admin.ai_knowledge.file_storage.delete_file_or_folder(
    item_id="item_id"
)
```

#### Database Operations

```python
# Process content for database
content = client.admin.ai_knowledge.database.process_content(
    content_data=AIKnowledgeCreate(
        content="Sample content for vectorization",
        other={
            "price": 123,
            "category": "electronics"
        }
    ),
    schema_name="Products",
    unique_identifier="prod123"
)

# Update an item
updated_item = client.admin.ai_knowledge.database.update_item(
    item_data={"price": 149.99},
    schema_name="Products",
    item_id="item_id"
)

# Get content by identifier
item = client.admin.ai_knowledge.database.get_content(
    schema_name="Products",
    unique_identifier="prod123"
)

# List content with filters
items = client.admin.ai_knowledge.database.get_content_list(
    filters={"category": "electronics"},
    schema_name="Products"
)

# Delete content
client.admin.ai_knowledge.database.delete_content(
    schema_name="Products",
    unique_identifier="prod123"
)
```

### Vector Queries

```python
# Run a search query
results = client.admin.queries.run_search_query(
    vector_schema="Documents",
    query_args={
        "content": "machine learning algorithms",
        "full_document": False
    }
)

# Find similar items
similar = client.admin.queries.run_find_similar_query(
    vector_schema="Documents",
    query_args={
        "uuid": "document_uuid"
    }
)
```

### System Information

```python
# Get settings
settings = client.admin.settings.get_settings()

# Get logs
logs = client.admin.logs.list_logs(
    integration_name="default",
    limit=25
)

# Get notifications
notifications = client.admin.notifications.list_notifications(
    integration_name="default"
)

# Get usage statistics
usage = client.admin.usage.list_usage(
    primary_key="integration_id"
)

# Get organization info
org = client.admin.organization.get_my_organization()
```

## Complete Workflow Examples

### Document Processing and Query Workflow

```python
from vector_bridge import VectorBridgeClient, FileAccessType, AIKnowledgeFileSystemFilters

# Initialize client and authenticate
client = VectorBridgeClient(integration_name="Knowledge Base")
client.login(username="admin@example.com", password="secure_password")

# 1. Create a folder structure
main_folder = client.admin.ai_knowledge.file_storage.create_folder(
    folder_name="Research Papers",
    folder_description="Academic papers on machine learning",
    private=False
)

# 2. Upload documents
paper_upload = client.admin.ai_knowledge.file_storage.upload_file(
    file_path="papers/transformer_models.pdf",
    parent_id=main_folder.uuid,
    tags=["nlp", "transformers", "research"],
    vectorized=True  # Ensure the document is vectorized for search
)

print(f"Uploaded paper with ID: {paper_upload.result.uuid}")

# 3. Make the document accessible to a specific user
user = client.admin.user.get_user_by_email("researcher@example.com")
client.admin.ai_knowledge.file_storage.grant_or_revoke_user_access(
    item_id=paper.uuid,
    user_id=user.uuid,
    has_access=True,
    access_type=FileAccessType.READ
)

# 4. Query the document
results = client.admin.queries.run_search_query(
    vector_schema="Documents",
    query_args={
        "content": "attention mechanism in transformer models",
        "limit": 5,
        "full_document": False
    }
)

# 5. Process the results
for i, result in enumerate(results):
    print(f"Result {i+1}:")
    print(f"Document: {result['document'][0]['name']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Similarity score: {result['metadata']['certainty']}")
    print("---")
```

### AI Assistant with Function Calls

```python
from vector_bridge import VectorBridgeClient, FunctionCreate, GPTActions, FunctionParametersStorageStructure, FunctionPropertyStorageStructure

# Initialize client with API key
client = VectorBridgeClient(
    integration_name="Virtual Assistant", 
    api_key="your_api_key"
)

# 1. Create a currency conversion function
currency_function = client.admin.functions.add_function(
    function_data=FunctionCreate(
        function_name="currency_converter",
        description="Convert an amount from one currency to another",
        function_action=GPTActions.CODE_EXEC,
        code="""
import os
import requests

def convert_currency(amount, from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()
    
    if to_currency not in data['rates']:
        return {"error": f"Currency {to_currency} not found"}
    
    conversion_rate = data['rates'][to_currency]
    converted_amount = amount * conversion_rate
    
    return {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "converted_amount": converted_amount,
        "rate": conversion_rate
    }

result = convert_currency(float(os.getenv("amount")), os.getenv("from_currency"), os.getenv("to_currency"))
print(result)
""",
        function_parameters=FunctionParametersStorageStructure(
            properties=[
                FunctionPropertyStorageStructure(
                    name="amount",
                    description="Amount to convert"
                ),
                FunctionPropertyStorageStructure(
                    name="from_currency",
                    description="Source currency code (e.g., USD)"
                ),
                FunctionPropertyStorageStructure(
                    name="to_currency",
                    description="Target currency code (e.g., EUR)"
                )
            ]
        )
    )
)

# 2. Use the AI to interact with a user and call the function when needed
conversation_id = "user_1234"

# User asks about currency conversion
message_stream = client.ai_message.process_message_stream(
    content="How much is 100 US dollars in euros today?",
    user_id=conversation_id
)

# Print the AI's response
print("AI Response:")
for chunk in message_stream.chunks:
    print(chunk, end="")

# The AI will automatically call the currency_converter function when needed

# User can then continue the conversation
follow_up_stream = client.ai_message.process_message_stream(
    content="And how much would that be in Japanese yen?",
    user_id=conversation_id
)

print("\n\nFollow-up response:")
for chunk in follow_up_stream.chunks:
    print(chunk, end="")
```

### User Management and Permissions

```python
from vector_bridge import VectorBridgeClient, SecurityGroupCreate, SecurityGroupUpdate, APIKeyCreate, UserUpdate

# Initialize client and authenticate
client = VectorBridgeClient(integration_name="Admin Portal")
client.login(username="admin@example.com", password="secure_password")

# 1. Create security groups with different permission levels
editors_group = client.admin.security_groups.create_security_group(
    security_group_data=SecurityGroupCreate(
        group_name="Content Editors",
        description="Can edit and upload content"
    )
)

viewers_group = client.admin.security_groups.create_security_group(
    security_group_data=SecurityGroupCreate(
        group_name="Content Viewers",
        description="Can only view content"
    )
)

# 2. Update permissions for viewers group
permissions = viewers_group.group_permissions
permissions.ai_knowledge.read = True
permissions.ai_knowledge.write = False
client.admin.security_groups.update_security_group(
    group_id=viewers_group.uuid,
    security_group_data=SecurityGroupUpdate(permissions=permissions)
)

# 3. Add new users
editor = client.admin.user.add_agent(
    email="editor@example.com",
    first_name="Editor",
    last_name="User",
    password="editor_password"
)

viewer = client.admin.user.add_agent(
    email="viewer@example.com",
    first_name="Viewer",
    last_name="User",
    password="viewer_password"
)

# 4. Assign users to security groups
client.admin.integrations.add_user_to_integration(
    user_id=editor.uuid,
    security_group_id=editors_group.uuid
)

client.admin.integrations.add_user_to_integration(
    user_id=viewer.uuid,
    security_group_id=viewers_group.uuid
)

# 5. Create API keys for users
editor_key = client.admin.api_keys.create_api_key(
    api_key_data=APIKeyCreate(
        key_name="Editor API Key",
        user_id=editor.uuid,
        expire_days=90,
        monthly_request_limit=5000,
        integration_name=client.integration_name
    )
)

viewer_key = client.admin.api_keys.create_api_key(
    api_key_data=APIKeyCreate(
        key_name="Viewer API Key",
        user_id=viewer.uuid,
        expire_days=90,
        monthly_request_limit=3000,
        integration_name=client.integration_name
    )
)

print(f"Editor API Key: {editor_key.key}")
print(f"Viewer API Key: {viewer_key.key}")
```

## Error Handling

The client raises `HTTPException` when API requests fail:

```python
from vector_bridge import VectorBridgeClient, HTTPException

client = VectorBridgeClient(integration_name="default")

try:
    client.login(username="user@example.com", password="wrong_password")
except HTTPException as e:
    print(f"Authentication failed: {e.status_code} - {e.detail}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.