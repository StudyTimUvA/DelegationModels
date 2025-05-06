from . import database


class BaseService:
    def party_has_access_to_object(
        self, database: database.Database, party_id: str, object_id: str, action: str
    ) -> bool:
        """
        Check if a party has access to an object based on the evidence in the database.

        Params:
            database: the database instance containing evidence.
            party_id: the identifier of the party.
            object_id: the identifier of the object.
            action: the action to be performed on the object.

        Returns:
            True if the party has access to the object, False otherwise.
        """
        for evidence in database.get_evidence_by_party(party_id):
            for rule in evidence.rules:
                if rule.object_id == object_id and rule.permit and rule.action == action:
                    return True

        return False
