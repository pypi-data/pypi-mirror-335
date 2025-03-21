from typing import Any, Dict, TypeVar

import requests
from pydantic import BaseModel

from vector_bridge.schema.error import HTTPException

# Type definitions from OpenAPI spec
T = TypeVar("T")


# Models based on OpenAPI schema
class Token(BaseModel):
    access_token: str
    token_type: str


class VectorBridgeClient:
    """
    Python client for the VectorBridge.ai API.

    Provides access to all functionality of the VectorBridge platform including
    authentication, user management, AI processing, vector operations, and more.
    """

    def __init__(
        self,
        base_url: str = "https://api.vectorbridge.ai",
        api_key: str = None,
        integration_name: str = "default",
    ):
        """
        Initialize the VectorBridge client.

        Args:
            base_url: The base URL of the VectorBridge API. Defaults to the development server.
        """
        from vector_bridge.admin import AdminClient
        from vector_bridge.customer.ai import AIClient
        from vector_bridge.customer.ai_message import AIMessageClient
        from vector_bridge.customer.function import FunctionClient
        from vector_bridge.customer.query import QueryClient

        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.api_key = api_key
        self.integration_name = integration_name

        # Initialize admin client
        self.admin = AdminClient(self)

        # Initialize user client
        self.ai = AIClient(self)
        self.ai_message = AIMessageClient(self)
        self.functions = FunctionClient(self)
        self.queries = QueryClient(self)

    def login(self, username: str, password: str) -> Token:
        """
        Log in to obtain an access token.

        Args:
            username: User's email
            password: User's password

        Returns:
            Token object containing access_token and token_type
        """
        url = f"{self.base_url}/token"
        data = {
            "username": username,
            "password": password,
        }
        response = self.session.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        result = self._handle_response(response)
        self.access_token = result["access_token"]

        print(
            """

        ██╗   ██╗███████╗ ██████╗████████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██████╗  ██████╗ ███████╗    █████╗ ██╗
        ██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝   ██╔══██╗██║
        ██║   ██║█████╗  ██║        ██║   ██║   ██║██████╔╝██████╔╝██████╔╝██║██║  ██║██║  ███╗█████╗     ███████║██║
        ╚██╗ ██╔╝██╔══╝  ██║        ██║   ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██║  ██║██║   ██║██╔══╝     ██╔══██║██║
         ╚████╔╝ ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║██████╔╝██║  ██║██║██████╔╝╚██████╔╝███████╗██╗██║  ██║██║
          ╚═══╝  ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝╚═╝

                """
        )

        return Token(**result)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with bearer token authentication."""
        if not self.access_token:
            raise ValueError("Authentication required. Call login() first.")

        return {"Authorization": f"Bearer {self.access_token}"}

    def _get_api_key_headers(self, api_key: str) -> Dict[str, str]:
        """Get headers with API key authentication."""
        return {"Api-Key": api_key}

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and errors."""
        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                return None
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            try:
                error_data = response.json()
                exc = HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail"),
                )
            except ValueError:
                exc = HTTPException(
                    status_code=response.status_code,
                    detail=response.text,
                )
            raise exc

    def ping(self) -> str:
        """
        Ping the API to check if it's available.

        Returns:
            Response string
        """
        url = f"{self.base_url}/v1/ping"
        response = self.session.get(url)
        return self._handle_response(response)

    def generate_crypto_key(self) -> str:
        """
        Generate a crypto key.

        Returns:
            Generated crypto key
        """
        url = f"{self.base_url}/v1/secrets/generate-crypto-key"
        response = self.session.get(url)
        return self._handle_response(response)


# class DatabaseAdmin:
#     """Admin client for vector database management endpoints."""
#
#     def __init__(self, client: VectorBridgeClient):
#         self.client = client
#         self.state = DatabaseStateAdmin(client)
#         self.changeset = DatabaseChangesetAdmin(client)
#
#
# class DatabaseStateAdmin:
#     """Admin client for vector database state management."""
#
#     def __init__(self, client: VectorBridgeClient):
#         self.client = client
#
#     def apply_schemas_changes(
#             self,
#             integration_name: str = "default"
#     ) -> List[Dict[str, Any]]:
#         """
#         Apply VectorDB schemas changes.
#
#         Args:
#             integration_name: The name of the Integration
#
#         Returns:
#             List of schema states
#         """
#         url = f"{self.client.base_url}/v1/admin/vector-db/schemas/apply-changes"
#         params = {"integration_name": integration_name}
#
#         headers = self.client._get_auth_headers()
#         response = self.client.session.post(url, headers=headers, params=params)
#         return self.client._handle_response(response)
#
#     def discard_schemas_changes(
#             self,
#             integration_name: str = "default"
#     ) -> List[Dict[str, Any]]:
#         """
#         Discard VectorDB schemas changes.
#
#         Args:
#             integration_name: The name of the Integration
#
#         Returns:
#             List of schema states
#         """
#         url = f"{self.client.base_url}/v1/admin/vector-db/schemas/discard-changes"
#         params = {"integration_name": integration_name}
#
#         headers = self.client._get_auth_headers()
#         response = self.client.session.post(url, headers=headers, params=params)
#         return self.client._handle_response(response)
#
#
# class DatabaseChangesetAdmin:
#     """Admin client for vector database changeset management."""
#
#     def __init__(self, client: VectorBridgeClient):
#         self.client = client
#
#     def get_changeset_diff(
#             self,
#             integration_name: str = "default"
#     ) -> List[Dict[str, Any]]:
#         """
#         Get the changeset diff.
#
#         Args:
#             integration_name: The name of the Integration
#
#         Returns:
#             List of schema states with diffs
#         """
#         url = f"{self.client.base_url}/v1/admin/vector-db/changeset/diff"
#         params = {"integration_name": integration_name}
#
#         headers = self.client._get_auth_headers()
#         response = self.client.session.get(url, headers=headers, params=params)
#         return self.client._handle_response(response)
#
#     def add_schema(
#             self,
#             schema_data: Dict[str, str],
#             integration_name: str = "default"
#     ) -> List[Dict[str, Any]]:
#         """
#         Add creation of a new Schema to the changeset.
#
#         Args:
#             schema_data: Schema details
#             integration_name: The name of the Integration
#
#         Returns:
#             List of schema states
#         """
#         url = f"{self.client.base_url}/v1/admin/vector-db/changeset/schema/add"
#         params = {"integration_name": integration_name}
#
#         headers = self.client._get_auth_headers()
#         response = self.client.session.post(
#             url,
#             headers=headers,
#             params=params,
#             json=schema_data
#         )
#         return self.client._handle_response(response)
