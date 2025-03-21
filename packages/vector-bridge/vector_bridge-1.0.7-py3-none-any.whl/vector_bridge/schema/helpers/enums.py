from enum import Enum


class GPTActions(str, Enum):
    SEARCH = "SEARCH"
    SIMILAR = "SIMILAR"
    SUMMARY = "SUMMARY"
    CODE_EXEC = "CODE_EXEC"
    RUN_WORKFLOW = "RUN_WORKFLOW"
    FORWARD_TO_AGENT = "FORWARD_TO_AGENT"
    OTHER = "OTHER"


class UserType(str, Enum):
    OWNER = "OWNER"
    AGENT = "AGENT"
    CUSTOMER = "CUSTOMER"
    AI = "AI"


class ResponseFormat(str, Enum):
    TEXT = "TEXT"
    JSON = "JSON"


class FunctionCallChainExecutionOrder(str, Enum):
    BEGINNING = "BEGINNING"
    END = "END"


class CreateUserType(str, Enum):
    OWNER = "OWNER"
    AGENT = "AGENT"


class UserStatus(str, Enum):
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    DISABLED = "DISABLED"


class PolicyType(Enum):
    CHAT = "CHAT"
    MESSAGE = "MESSAGE"
    ORGANIZATION = "ORGANIZATION"
    USER = "USER"


class MessageType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    FILE = "FILE"
    LINK = "LINK"
    EMOJI = "EMOJI"
    STICKER = "STICKER"
    SYSTEM = "SYSTEM"
    EVENT = "EVENT"
    LOCATION = "LOCATION"
    CONTACT = "CONTACT"
    POLL = "POLL"


class WebsocketMessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class PromptKey(Enum):
    SYSTEM = "system_prompt"
    MESSAGE = "message_prompt"
    KNOWLEDGE = "knowledge_prompt"


class OpenAIKey(Enum):
    API_KEY = "api_key"
    MODEL = "model"
    MAX_TOKENS = "max_tokens"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    TEMPERATURE = "temperature"


class OverridesKey(Enum):
    AI_PROVIDER = "ai_provider"
    API_KEY = "api_key"
    MODEL = "model"
    MAX_TOKENS = "max_tokens"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    TEMPERATURE = "temperature"


class AzureOpenAIKey(Enum):
    API_KEY = "api_key"
    MODEL = "model"
    ENDPOINT = "endpoint"
    MAX_TOKENS = "max_tokens"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    TEMPERATURE = "temperature"


class AnthropicKey(Enum):
    API_KEY = "api_key"
    MODEL = "model"
    MAX_TOKENS = "max_tokens"
    TEMPERATURE = "temperature"


class WeaviateKey(Enum):
    API_KEY = "api_key"
    URL = "url"
    MAX_SIMILARITY_DISTANCE = "max_similarity_distance"


class AIProviders(Enum):
    OPEN_AI = "open_ai"
    AZURE_OPEN_AI = "azure_open_ai"
    ANTHROPIC = "anthropic"
    DEEP_SEEK = "deepseek"


class SchemaDiffState(Enum):
    IMMUTABLE = "immutable"
    REQUIRED = "required"
    DEFAULT = "default"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class ProtectedSchemaNames(Enum):
    Documents = "Documents"
    DocumentsChunks = "DocumentsChunks"
    Messages = "Messages"
    Chats = "Chats"

    @staticmethod
    def to_list():
        return [
            ProtectedSchemaNames.Documents.value,
            ProtectedSchemaNames.DocumentsChunks.value,
            ProtectedSchemaNames.Messages.value,
            ProtectedSchemaNames.Chats.value,
        ]


class ProtectedPropertyNames(Enum):
    UniqueIdentifier = "unique_identifier"
    Content = "content"
    ContentHash = "content_hash"
    Chunks = "chunks"
    ItemId = "item_id"
    Document = "document"
    Index = "index"
    SourceDocuments = "source_documents"
    DerivedDocuments = "derived_documents"

    @staticmethod
    def to_list():
        return [
            ProtectedPropertyNames.UniqueIdentifier.value,
            ProtectedPropertyNames.Content.value,
            ProtectedPropertyNames.ContentHash.value,
            ProtectedPropertyNames.Chunks.value,
            ProtectedPropertyNames.ItemId.value,
            ProtectedPropertyNames.Document.value,
            ProtectedPropertyNames.Index.value,
            ProtectedPropertyNames.SourceDocuments.value,
            ProtectedPropertyNames.DerivedDocuments.value,
        ]


class Cases(Enum):
    upper = "upper"
    lower = "lower"

    @staticmethod
    def get(item: str):
        for case in Cases:
            if item == case.value:
                return case


class Patterns(Enum):
    pattern_star = "pattern*"
    star_pattern = "pattern*"
    star_pattern_star = "*pattern*"
    lower = "lower"

    @staticmethod
    def get(item: str):
        for pattern in Patterns:
            if item == pattern.value:
                return pattern


class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class FilterOperator(Enum):
    EQUAL = "Equal"
    NOT_EQUAL = "NotEqual"
    GREATER_THAN = "GreaterThan"
    GREATER_THAN_EQUAL = "GreaterThanEqual"
    LESS_THAN = "LessThan"
    LESS_THAN_EQUAL = "LessThanEqual"
    LIKE = "Like"
    WITHIN_GEORANGE = "WithinGeoRange"
    IS_NULL = "IsNull"
    CONTAINS_ANY = "ContainsAny"  # Only for array and text properties
    CONTAINS_ALL = "ContainsAll"  # Only for array and text properties


class DataTypeInput(Enum):
    TEXT = "text"
    TEXT_ARRAY = "text_array"
    INT = "int"
    INT_ARRAY = "int_array"
    BOOL = "bool"
    BOOL_ARRAY = "bool_array"
    NUMBER = "number"
    NUMBER_ARRAY = "number_array"
    DATE = "date"
    DATE_ARRAY = "date_array"
    UUID = "uuid"
    UUID_ARRAY = "uuid_array"
    GEO_COORDINATES = "geoCoordinates"
    PHONE_NUMBER = "phoneNumber"


class ValueTypes(Enum):
    INT = "valueInt"
    BOOL = "valueBoolean"
    TEXT = "valueText"
    NUMBER = "valueNumber"
    DATE = "valueDate"
    GEO_COORDINATES = "valueGeoRange"


class ChangeEntityType(Enum):
    SCHEMA = "schema"
    PROPERTY = "property"
    FILTER = "filter"


class FileSystemType(Enum):
    FOLDER = "folder"
    FILE = "file"


class BaseFunctionNames(Enum):
    GET_MESSAGES = "vector_bridge__get_messages"
    GET_DOCUMENTS_DATA = "vector_bridge__get_documents_data"
    ADD_TO_CORE_KNOWLEDGE = "vector_bridge__add_to_core_knowledge"
    REMOVE_FROM_CORE_KNOWLEDGE = "vector_bridge__remove_from_core_knowledge"


class PropertyKey(Enum):
    DESCRIPTION = "property_description"
    SORTING_SUPPORTED = "sorting_supported"
    RETURNED = "returned"


class FilterKey(Enum):
    DESCRIPTION = "filter_description"
    FILTERING_SUPPORTED = "filtering_supported"
    FILTER_SETTINGS = "filter_settings"


class MessageStorageMode(str, Enum):
    VECTOR_DB = "VECTOR_DB"
    DYNAMO_DB = "DYNAMO_DB"


class IntegrationEndpointsAccessibility(str, Enum):
    OPEN = "OPEN"
    AUTH_PROTECTED = "AUTH_PROTECTED"


class LogsFilter(str, Enum):
    USER = "USER"
    API_KEY_HASH = "API_KEY_HASH"


class UsageFilter(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    INTEGRATION = "INTEGRATION"
    API_KEY_HASH = "API_KEY_HASH"


class OpenAIModels(str, Enum):
    GPT_4_o_mini = "gpt-4o-mini"
    GPT_4_o = "gpt-4o"
    GPT_o_1 = "o1"
    GPT_o_1_mini = "o1-mini"


class AnthropicModels(str, Enum):
    CLAUDE_V3_7_SONNET = "claude-3-7-sonnet-latest"
    CLAUDE_V3_5_SONNET = "claude-3-5-sonnet-latest"
    CLAUDE_V3_5_HAIKU = "claude-3-5-haiku-latest"
    CLAUDE_V3_OPUS = "claude-3-opus-latest"


class DeepSeekModels(str, Enum):
    CHAT = "deepseek-chat"
    REASONER = "deepseek-reasoner"


class FileAccessType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
