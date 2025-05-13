from ..base import service as BaseService
import networkx as nx
import time

class OracleService(BaseService.BaseService):
    """
    Service class for managing evidence and revocations.
    Inherits from the base Service class.
    """

    def __init__(self):
        super().__init__()

    def has_recursive_access(self, db, party_id: str, owner_id: str, resource: str, action: str) -> bool:
        """
        Check if a party has recursive access to a resource.

        Params:
            party_id: the ID of the party.
            resource: the resource to check access for.
        Returns:
            True if the party has recursive access, False otherwise.
        """
        # if not nx.has_path(db.graph, party_id, owner_id):
        #     return False
        if not nx.has_path(db.graph, owner_id, party_id):
            return False
        
        paths = list(nx.all_simple_paths(db.graph, source=owner_id, target=party_id))

        for path in paths:
            valid_path = True
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = db.graph[u][v]
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
