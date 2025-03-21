from typing import Any, Dict, Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.messages import (MessagesListDynamoDB,
                                           MessagesListVectorDB,
                                           StreamingResponse)


class MessageAdmin:
    """Admin client for message management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def process_internal_message(
        self,
        content: str,
        suffix: str,
        integration_name: str = None,
        instruction_name: str = "default",
        function_to_call: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        crypto_key: Optional[str] = None,
    ) -> StreamingResponse:
        """
        Process an internal message and get AI response.

        Args:
            content: Message content
            suffix: Suffix for the user_id
            integration_name: The name of the integration
            instruction_name: The name of the instruction
            function_to_call: Function to call (optional)
            data: Additional data (optional)
            crypto_key: Crypto key for encrypted storage (optional)

        Returns:
            Stream of message objects including AI response
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/stream/admin/ai/process-internal-message/response-text"
        params = {
            "suffix": suffix,
            "integration_name": integration_name,
            "instruction_name": instruction_name,
        }

        if function_to_call:
            params["function_to_call"] = function_to_call

        headers = self.client._get_auth_headers()
        if crypto_key:
            headers["Crypto-Key"] = crypto_key

        message_data = {"content": content}
        if data:
            message_data["data"] = data

        response = self.client.session.post(
            url,
            headers=headers,
            params=params,
            json=message_data,
            stream=True,  # Enables streaming response
        )
        if response.status_code >= 400:
            self.client._handle_response(response)

        return StreamingResponse(response)

    def fetch_internal_messages_from_vector_db(
        self,
        suffix: str,
        integration_name: str = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: str = "asc",
        near_text: Optional[str] = None,
    ) -> MessagesListVectorDB:
        """
        Retrieve internal messages from vector database.

        Args:
            suffix: Suffix for the user_id
            integration_name: The name of the integration
            limit: Number of messages to return
            offset: Starting point for fetching records
            sort_order: Order to sort results (asc/desc)
            near_text: Text to search for semantically similar messages

        Returns:
            MessagesListVectorDB with messages and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai/internal-messages/weaviate"
        params = {
            "suffix": suffix,
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order,
        }
        if near_text:
            params["near_text"] = near_text

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response)
        return MessagesListVectorDB.model_validate(result)

    def fetch_internal_messages_from_dynamo_db(
        self,
        suffix: str,
        integration_name: str = None,
        limit: int = 50,
        last_evaluated_key: Optional[str] = None,
        sort_order: str = "asc",
        crypto_key: Optional[str] = None,
    ) -> MessagesListDynamoDB:
        """
        Retrieve internal messages from DynamoDB.

        Args:
            suffix: Suffix for the user_id
            integration_name: The name of the integration
            limit: Number of messages to return
            last_evaluated_key: Key for pagination
            sort_order: Order to sort results (asc/desc)
            crypto_key: Crypto key for decryption

        Returns:
            MessagesListDynamoDB with messages and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai/internal-messages/dynamo-db"
        params = {
            "suffix": suffix,
            "integration_name": integration_name,
            "limit": limit,
            "sort_order": sort_order,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        if crypto_key:
            headers["Crypto-Key"] = crypto_key

        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response)
        return MessagesListDynamoDB.model_validate(result)
