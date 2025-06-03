from ..base import database
from ..base import service
from ..base import evidence as base_evidence

# TODO: remove the base main database, instead only use the broker
# TODO: update the has_access method to work using the broker


class PrevPartyService(service.BaseService):
    def add_delegation(
        self, party1, party2, objects, actions, expiry, database_name, evidence=None
    ):
        db = self.db_broker.get_database(database_name)

        rule = base_evidence.Rule(
            object_ids=objects,
            actions=actions,
        )

        evid = base_evidence.Evidence(
            identifier=db.get_next_identifier(),
            issuer=party1,
            receiver=party2,
            rules=[rule],
            valid_from=0,
            valid_untill=expiry,
            db_name=database_name,
        )
        db.add_evidence(evid)
        return evid

    def revoke_delegation(self, delegation_id, database_name):
        """
        Revoke a delegation by its ID.

        Params:
            delegation_id: the ID of the delegation to be revoked.

        Returns:
            True if the revocation was successful, False otherwise.
        """
        db = self.db_broker.get_database(database_name)

        evidence = db.get_evidence(delegation_id)
        if evidence:
            db.revoke(delegation_id)
            return True
        return False

    def has_access(
        self,
        current_party: str,
        data_owner: str,
        object_id: str,
        action: str,
        db_name: str,
        evidence: base_evidence.Evidence,
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

        if evidence and evidence.identifier in self.db_broker.get_database(db_name).revocations:
            # If the evidence is revoked, no need to check further
            return False

        # Avoid cycles
        if current_party in visited:
            return False

        visited.add(current_party)

        # Check if the current party has direct access to the object
        # for db_name, evidence in self.db_broker.get_all_evidence_by_party(current_party):
        for evidence in self.db_broker.get_database(evidence.db_name).get_evidence_by_party(current_party):
            for rule in evidence.rules:
                if evidence.identifier in self.db_broker.get_database(db_name).revocations:
                    continue

                if object_id in rule.object_ids and action in rule.actions:
                    if evidence.issuer == data_owner:
                        return True

                    # Recursively check if the issuer has access
                    if self.has_access(
                        evidence.issuer, data_owner, object_id, action, db_name, evidence, visited
                    ):
                        return True

        return False
