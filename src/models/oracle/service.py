from ..base import service as BaseService
from typing import List


class OracleService(BaseService.BaseService):
    """
    Service class for managing evidence and revocations.
    Inherits from the base Service class.
    """

    def add_delegation(
        self,
        party1: str,
        party2: str,
        objects: List[str],
        actions: List[str],
        expiry: float,
        db_name: str,
        evidence=None,
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
        return self.db_broker.add_link(
            from_db=db_name,
            from_node=party1,
            to_node=party2,
            objects=objects,
            actions=actions,
            evidence=evidence,
        )

    def add_parties(self, party_ids: List[str], db_name: str):
        """
        Add multiple parties to the database.

        Params:
            party_ids: a list of party IDs to be added.
            db_name: the name of the database to add parties to.
        """
        self.db_broker.get_database(db_name).add_parties(party_ids)

    def has_access(
        self, party_id: str, owner_id: str, resource: str, action: str, db_name: str, evidence
    ) -> bool:
        """Check if a party has access to a resource with a specific action."""
        return self.db_broker.has_access(party_id, owner_id, resource, action, db_name, evidence)

    def revoke_delegation(self, edge_id: int, database_name) -> bool:
        """
        Revoke a delegation by edge ID.

        Params:
            edge_id: the ID of the edge to revoke.

        Returns:
            True if the revocation was successful, False otherwise.
        """
        db = self.db_broker.get_database(database_name)

        for u, v, data in db.graph.edges(data=True):
            if data["id"] == edge_id:
                db.graph.remove_edge(u, v)
                return True

        # If we reach here, the edge was not found, look in outgoing bridges
        for bridge in db.outgoing_bridges.get(edge_id, []):
            if bridge.id == edge_id:
                db.outgoing_bridges[bridge.from_node].remove(bridge)
                return True

        return False
