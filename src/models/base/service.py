from . import database
from . import evidence
from typing import List


class BaseService:
    def __init__(self, db_class, database_broker: database.DatabaseBroker = None):
        """
        Initialize the BaseService with a database instance.

        Params:
            database: an instance of the Database class.
            database_broker: an optional instance of the DatabaseBroker class for additional functionality.
        """
        self.db_class = db_class
        self.db_broker = database_broker

    def has_access(
        self, delegatee: str, data_owner: str, object: str, action: str, db_name: str
    ) -> bool:
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
        self,
        party1: str,
        party2: str,
        objects: List[str],
        actions: List[str],
        expiry: float,
        database_key: str,
        evidence: evidence.Evidence = None,
    ) -> evidence.Evidence:
        """
        Add a delegation from party1 to party2 in the database.

        Params:
            party1: the ID of the delegator.
            party2: the ID of the delegatee.
            objects: a list of objects being delegated.
            actions: a list of actions that can be performed on the objects.
            expiry: the expiration time of the delegation.
            database_key: the name of the database to add the delegation to.
            evidence: an optional Evidence object containing informaion about the delegation the new one is based on.

        Returns:
            The ID of the newly added delegation.
        """
        raise NotImplementedError()

    def revoke_delegation(self, delegation_id: int, database_key: str):
        """
        Revoke a delegation in the database.

        Params:
            delegation_id: the ID of the delegation to be revoked.
        """
        raise NotImplementedError()

    def add_parties(self, party_ids: List[str], database_key: str):
        """
        Add multiple parties to the database.

        Note: This method might not be required in all implementations, but is included for completeness.

        Params:
            party_ids: a list of party IDs to be added.
            database_key: the name of the database to add parties to.
        """
        ...
