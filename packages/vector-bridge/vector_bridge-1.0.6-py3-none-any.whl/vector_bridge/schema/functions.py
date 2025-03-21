from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from vector_bridge.schema.helpers.enums import AIProviders, GPTActions


class FunctionsSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"


class FunctionPropertyStorageStructure(BaseModel):
    name: str
    description: str
    type: str = Field(default="string")
    items: Dict[str, str] = Field(default_factory=dict)
    enum: List[str] = []
    required: bool = Field(default=False)


class FunctionParametersStorageStructure(BaseModel):
    properties: List[FunctionPropertyStorageStructure]

    def to_dynamodb_raw(self):
        return {
            "properties": {"L": [{"M": _property.to_dynamodb_raw()} for _property in self.properties]},
        }


class Overrides(BaseModel):
    ai_provider: Optional[AIProviders] = Field(default=None)
    model: str = Field(default="")
    system_prompt: str = Field(default="")
    message_prompt: str = Field(default="")
    knowledge_prompt: str = Field(default="")
    max_tokens: str = Field(default="")
    frequency_penalty: str = Field(default="")
    presence_penalty: str = Field(default="")
    temperature: str = Field(default="")


class Function(BaseModel):
    function_id: str
    function_name: str
    integration_id: str
    description: str
    function_action: GPTActions
    code: str = Field(default="")
    vector_schema: str = Field(default="")
    accessible_by_ai: bool = Field(default=True)
    function_parameters: FunctionParametersStorageStructure
    overrides: Overrides = Field(default=Overrides())
    system_required: bool = Field(default=False)
    created_at: str = Field(default="")
    created_by: str = Field(default="")
    updated_at: str = Field(default="")
    updated_by: str = Field(default="")

    @property
    def uuid(self):
        return self.function_id


class FunctionCreate(BaseModel):
    function_name: str
    description: str
    function_action: GPTActions
    code: str = Field(default="")
    vector_schema: str = Field(default="")
    accessible_by_ai: bool = Field(default=True)
    function_parameters: FunctionParametersStorageStructure
    overrides: Overrides = Field(default=Overrides())


class FunctionUpdate(BaseModel):
    description: str
    function_action: GPTActions
    code: str = Field(default="")
    vector_schema: str = Field(default="")
    accessible_by_ai: bool = Field(default=True)
    function_parameters: FunctionParametersStorageStructure
    overrides: Overrides = Field(default=Overrides())


class PaginatedFunctions(BaseModel):
    functions: List[Function] = Field(default_factory=list)
    limit: int
    last_evaluated_key: Optional[str] = None
    has_more: bool = False


class StreamingResponse:
    """
    Processes a binary stream, filtering out <ignore> messages and
    capturing everything inside <response>...</response>.
    """

    RESPONSE_START = b"<response>\n"
    RESPONSE_END = b"</response>"

    def __init__(self, stream):
        """
        Initializes the processor with a binary stream (generator).
        :param stream: An iterable or generator that yields binary messages.
        """
        self.stream = stream
        self.in_response_block = False  # Tracks if we're inside <response>...</response>
        self.buffer = []  # Stores accumulated response lines

    def response(self) -> Union[str, None]:
        """
        Processes the stream, returning the full data inside <response>...</response>.
        """
        for message in self.stream:
            if not isinstance(message, bytes):
                continue  # Ensure it's binary (shouldn't happen but for safety)

            if message == b"<ignore>\n":
                continue  # Ignore <ignore> messages

            if message == self.RESPONSE_START:
                self.in_response_block = True
                self.buffer = []  # Clear buffer for new response
                continue

            if message == self.RESPONSE_END:
                self.in_response_block = False
                break

            if self.in_response_block:
                self.buffer.append(message)  # Store response lines

        if self.buffer:
            return b"".join(self.buffer).decode("utf-8")  # Decode and return full response
        return None
