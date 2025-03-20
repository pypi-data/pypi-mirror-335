from typing import Optional

from src.pipefysdk.base_service import BaseService
from src.pipefysdk.queries.query_cards import GraphQLQueries
from src.pipefysdk.utils.binary_tree import BinarySearchTree
from src.pipefysdk.errors.card_move_pipefy_error import CardMovePipefyError
from src.pipefysdk.errors.search_field_pipefy_error import SearchFieldPipefyError


class PipefySDK(BaseService):
    def __init__(self, token: str, url: str) -> None:
        super().__init__(pipefy_token=token, url=url)
        self.queries = GraphQLQueries()

    def get_card_info(self, card_id: int) -> dict:
        """
        Get card information by card id.

        args:
            card_id: Define the card id to get the information.

        return: Return the card information.
        """
        query = self.queries.search_fields_in_card(card_id=card_id)
        response = self.request(query)
        return response.get("data").get("card")

    def update_single_card_field(self, card_id: str, field_id: str, new_value: str) -> dict:
        """
        Update a single card field.

        args:
            card_id: Define the card id to update the field.
            field_id: Define the field id to update.
            new_value: Define the new value to be updated.

        return: Return the response of the API.
        """
        mutation = self.mutations.mutation_update_card_field(card_id, field_id, new_value)
        return self.request(mutation).get("data", {}).get("updateFieldsValues", {})

    def update_multiple_card_fields(self, card_id: str, fields: list) -> dict:
        """
        Update multiple card fields.

        args:
            card_id: Define the card id to update the fields.
            fields: Define the fields to be updated.

        return: Return the response of the API.
        """
        mutation = self.mutations.mutation_update_card_field(card_id, fields=fields)
        return self.request(mutation).get("data", {}).get("updateFieldsValues", {})

    def search_value_in_field(self, card_id: int, field_id: str) -> Optional[str]:
        """
        Search a value in a card field.

        args:
            card_id: Define the card id to search for the value.
            field_id: Define the field id to search for the value.

        return: Return the value of the field or None if not found.
        """
        query = self.queries.search_fields_in_card(card_id)
        response = self.request(query)
        try:
            fields = response.get("data", {}).get("card", {}).get("fields", [])
        except:
            raise SearchFieldPipefyError("Field not found")
        bst = BinarySearchTree()
        for field in fields:
            field_key = field.get("field", {}).get("id")
            field_value = field.get("value")
            bst.insert(field_key, field_value)

        result_node = bst.search(field_id)
        return result_node.value if result_node else None

    def search_multiple_values_in_fields(self, card_id: int, field_ids: list) -> dict:
        """
        Search multiple values in card fields.

        args:
            card_id: Define the card id to search for the values.
            field_ids: Define the fields ids to search for the values.

        return: Return the values of the fields.
        """
        query = self.queries.search_fields_in_card(card_id)
        response = self.request(query)
        try:
            fields = response.get("data", {}).get("card", {}).get("fields", [])
        except:
            raise SearchFieldPipefyError("Field not found")

        bst = BinarySearchTree()
        for field in fields:
            field_key = field.get("field", {}).get("id")
            field_value = field.get("value")
            bst.insert(field_key, field_value)

        result = {}
        for field_id in field_ids:
            result_node = bst.search(field_id)
            result[field_id] = result_node.value if result_node else None
        return result

    def move_card_to_phase(self, new_phase_id: int, card_id: int) -> dict:
        """
            Move a card to a new phase.

            Args:
                new_phase_id (int): The ID of the new phase.
                card_id (int): The ID of the card to move.

            Returns:
                dict: The response from the API.
        """
        mutation = self.mutations.mutation_move_card_to_phase(card_id=card_id, phase_id=new_phase_id)
        response = self.request(mutation)
        if 'errors' in response:
            raise CardMovePipefyError(f"{response['errors']}. Probably, you have required fields empty in your card.")
        return response

    def get_attachments_from_card(self, card_id: int) -> list:
        """
        Get attachments from a card.

        Args:
            card_id (int): The ID of the card.

        Returns:
            list: The response from the API.
        """
        query = self.queries.get_attachments_from_card(card_id)
        response = self.request(query)
        return response.get("data", {}).get("card", {}).get("attachments", {})

    def set_assignee_in_card(self, card_id: int, assignee_ids: list) -> dict:
        """
        Search users in a pipe.

        Args:
            card_id (int): The ID of the card.
            assignee_ids (list): The list of assignee IDs.

        Returns:
            dict: The response from the API.
        """
        query = self.mutations.update_card_assignee(card_id, assignee_ids)
        response = self.request(query)
        return response.get("data", {}).get("pipe", {}).get("users", {})

