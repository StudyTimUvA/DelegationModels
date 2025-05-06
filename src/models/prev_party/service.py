from ..base import database
from ..base import service


class PrevPartyService(service.BaseService):
    def has_recursive_access(
        self,
        database: database.Database,
        current_party: str,
        data_owner: str,
        object_id: str,
        action: str,
        visited=None,
    ) -> bool:
        """
        Recursively check if a party has access to an object by finding a path from the receiver to the data owner.

        Params:
            database: the database instance containing evidence.
            current_party: the current party being checked.
            data_owner: the identifier of the data owner.
            object_id: the identifier of the object.
            action: the action to be performed on the object.
            visited: a set of visited parties to avoid cycles.

        Returns:
            True if a path exists from the receiver to the data owner with the required access, False otherwise.
        """
        if visited is None:
            visited = set()

        # Avoid cycles
        if current_party in visited:
            return False

        visited.add(current_party)

        # Check if the current party has direct access to the object
        for evidence in database.get_evidence_by_party(current_party):
            for rule in evidence.rules:
                if rule.object_id == object_id and rule.permit and rule.action == action:
                    if evidence.data_owner == data_owner:
                        return True

                    # Recursively check if the issuer has access
                    if self.has_recursive_access(
                        database, evidence.issuer, data_owner, object_id, action, visited
                    ):
                        return True

        return False
