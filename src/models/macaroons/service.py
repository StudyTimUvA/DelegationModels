from ..base import service
from pymacaroons import Macaroon, Verifier
import uuid
import copy

# TODO: fix the revocation mechanism

class Evidence:
    def __init__(self, receiver: str, macaroon: Macaroon):
        self.receiver = receiver
        self.macaroon = macaroon
        self.identifier = macaroon.identifier


class Service(service.BaseService):
    def has_access(
        self,
        delegatee: str,
        data_owner: str,
        object: str,
        action: str,
        db_name: str,
        evidence: Evidence=None,
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
        if not evidence:
            return False
        
        receiver = evidence.receiver
        evidence = evidence.macaroon
        
        db = self.db_broker.get_database(db_name)
        if not db:
            return False
        
        if evidence.identifier in db.revocations:
            return False
        
        if receiver != delegatee:
            return False

        verifier = Verifier()
        
        def check_caveat(x):
            objects, actions = x.split(":")
            allowed_objects = objects.split(",")
            allowed_actions = actions.split(",")

            if object not in allowed_objects or action not in allowed_actions:
                return False
            return True

        # Check that all caveats are satisfied
        verifier.satisfy_general(check_caveat)
        
        db_source = self.db_broker.get_database(evidence.location)
        key = db_source.get_key(evidence.identifier)

        # Check if the evidence satisfies the caveat
        try:
            verifier.verify(evidence, key)
        except Exception as e:
            return False
        
        return True

    def add_delegation(
        self,
        party1: str,
        party2: str,
        objects: list,
        actions: list,
        expiry: float,
        database_key: str,
        evidence=None,
    ) -> Macaroon:
        """
        Add a delegation from party1 to party2 in the database.

        Params:
            party1: the ID of the delegator.
            party2: the ID of the delegatee.
            objects: a list of objects being delegated.
            actions: a list of actions that can be performed on the objects.
            expiry: the expiration time of the delegation.
            database_key: the name of the database to add the delegation to.
            evidence: optional evidence related to the delegation.

        Returns:
            Macaroon: The evidence object representing the delegation.
        """

        if not evidence:
            key = str(uuid.uuid4())
            evidence = Macaroon(
                identifier=str(uuid.uuid4()),
                location=database_key,
                key=key,
            )
            self.db_broker.get_database(database_key).set_key(evidence.identifier, key)
        else:
            evidence = evidence.macaroon

            # Need to make a copy of the evidence to avoid modifying the original
            evidence = copy.deepcopy(evidence)

        object_string = ",".join(objects)
        action_string = ",".join(actions)
        evidence.add_first_party_caveat(f'{object_string}:{action_string}')

        return Evidence(receiver=party2, macaroon=evidence)

    def revoke_delegation(self, delegation_id: int, database_key: str):
        """
        Revoke a delegation in the database.

        Params:
            delegation_id: the ID of the delegation to be revoked.
        """
        db = self.db_broker.get_database(database_key)
        if not db:
            raise ValueError(f"Database {database_key} not found.")

        db.revocations.append(delegation_id)