from . import database
from typing import List


class BaseService:
    def __init__(self, database: database.Database):
        """
        Initialize the BaseService with a database instance.

        Params:
            database: an instance of the Database class.
        """
        self.db = database

    def has_access(self, delegatee: str, data_owner: str, object: str, action: str) -> bool:
        """
        Check if a delegatee has access to an object based on the evidence in the database.

        Params:
            delegatee: the identifier of the delegatee.
            data_owner: the identifier of the data owner.
            object: the identifier of the object.
            action: the action to be performed on the object.

        Returns:
            True if the delegatee has access to the object, False otherwise.
        """
        raise NotImplementedError("Not implemented yet!")

    def add_delegation(
        self, party1: str, party2: str, objects: List[str], actions: List[str], expiry: float
    ) -> int:
        """
        Add a delegation from party1 to party2 in the database.

        Params:
            party1: the ID of the delegator.
            party2: the ID of the delegatee.
            objects: a list of objects being delegated.
            actions: a list of actions that can be performed on the objects.
            expiry: the expiration time of the delegation.

        Returns:
            The ID of the newly added delegation.
        """
        raise NotImplementedError()

    def revoke_delegation(self, delegation_id: int) -> bool:
        """
        Revoke a delegation in the database.

        Params:
            delegation_id: the ID of the delegation to be revoked.

        Returns:
            True if the revocation was successful, False otherwise.
        """
        raise NotImplementedError("Not implemented yet!")

    def get_path(self, party1: str, party2: str, object: str) -> List[str]:
        """
        Get the path between two parties in the database.

        Params:
            party1: the ID of the first party.
            party2: the ID of the second party.
            object: the identifier of the object.

        Returns:
            A list of party IDs representing the path from party1 to party2.
        """
        raise NotImplementedError()

    # def party_has_access_to_object(
    #     self, database: database.Database, party_id: str, object_id: str, action: str
    # ) -> bool:
    #     """
    #     Check if a party has access to an object based on the evidence in the database.

    #     Params:
    #         database: the database instance containing evidence.
    #         party_id: the identifier of the party.
    #         object_id: the identifier of the object.
    #         action: the action to be performed on the object.

    #     Returns:
    #         True if the party has access to the object, False otherwise.
    #     """
    #     for evidence in database.get_evidence_by_party(party_id):
    #         for rule in evidence.rules:
    #             if rule.object_id == object_id and rule.permit and rule.action == action:
    #                 return True

    #     return False
