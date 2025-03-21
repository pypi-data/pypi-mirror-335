from typing import Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.instruction import (Instruction, InstructionCreate,
                                              PaginatedInstructions)


class InstructionsAdmin:
    """Admin client for instructions management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def add_instruction(self, instruction_data: InstructionCreate, integration_name: str = None) -> Instruction:
        """
        Add new Instruction to the integration.

        Args:
            instruction_data: Instruction details
            integration_name: The name of the Integration

        Returns:
            Created instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=instruction_data.model_dump())
        result = self.client._handle_response(response)
        return Instruction.model_validate(result)

    def get_instruction_by_name(self, instruction_name: str, integration_name: str = None) -> Optional[Instruction]:
        """
        Get the Instruction by name.

        Args:
            instruction_name: The name of the Instruction
            integration_name: The name of the Integration

        Returns:
            Instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response)
        return Instruction.model_validate(result) if result else None

    def get_instruction_by_id(self, instruction_id: str, integration_name: str = None) -> Optional[Instruction]:
        """
        Get the Instruction by ID.

        Args:
            instruction_id: The ID of the Instruction
            integration_name: The name of the Integration

        Returns:
            Instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response)
        return Instruction.model_validate(result) if result else None

    def list_instructions(
        self,
        integration_name: str = None,
        limit: int = 10,
        last_evaluated_key: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> PaginatedInstructions:
        """
        List Instructions for an Integration, sorted by created_at or updated_at.

        Args:
            integration_name: The name of the Integration
            limit: The number of Instructions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: The sort field (created_at or updated_at)

        Returns:
            PaginatedInstructions with instructions and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instructions/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "sort_by": sort_by,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response)
        return PaginatedInstructions.model_validate(result)

    def delete_instruction(self, instruction_id: str, integration_name: str = None) -> None:
        """
        Delete Instruction from the integration.

        Args:
            instruction_id: The instruction ID
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response)
