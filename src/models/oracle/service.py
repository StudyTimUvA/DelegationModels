from ..base import service as BaseService
import networkx as nx
import time
from typing import List


class OracleService(BaseService.BaseService):
    """
    Service class for managing evidence and revocations.
    Inherits from the base Service class.
    """

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
        if not self.db.graph.has_node(party1):
            raise ValueError(f"Delegator with ID {party1} does not exist.")
        if not self.db.graph.has_node(party2):
            raise ValueError(f"Delegatee with ID {party2} does not exist.")

        edge_id = self.db.get_next_identifier()
        self.db.graph.add_edge(
            party1, party2, id=edge_id, resources=objects, expires=expiry, actions=actions
        )

        return edge_id

    def has_access(self, party_id: str, owner_id: str, resource: str, action: str) -> bool:
        """
        Check if a party has recursive access to a resource.

        Params:
            party_id: the ID of the party.
            resource: the resource to check access for.
        Returns:
            True if the party has recursive access, False otherwise.
        """
        # Check if there is any path from the owner to the party
        if not nx.has_path(self.db.graph, owner_id, party_id):
            return False

        # There is a path, now check if any of the paths contain the resource and action
        paths = list(nx.all_simple_paths(self.db.graph, source=owner_id, target=party_id))
        for path in paths:
            valid_path = True
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.db.graph[u][v]
                now = time.time()

                if edge_data.get("expires") and edge_data["expires"] < now:
                    valid_path = False
                    break
                if resource not in edge_data.get("resources", []):
                    valid_path = False
                    break
                if action not in edge_data.get("actions", []):
                    valid_path = False
                    break

            if valid_path:
                return True

        return False

    def revoke_delegation(self, edge_id: int) -> bool:
        """
        Revoke a delegation by edge ID.

        Params:
            edge_id: the ID of the edge to revoke.

        Returns:
            True if the revocation was successful, False otherwise.
        """
        for u, v, data in self.db.graph.edges(data=True):
            if data["id"] == edge_id:
                self.db.graph.remove_edge(u, v)
                return True
        return False
