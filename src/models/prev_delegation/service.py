from ..base import service as base_service


class PrevDelegationService(base_service.BaseService):
    def has_recursive_access(
        self,
        db,
        party: str,
        data_owner: str,
        object: str,
        action: str,
        evidence_id: int,
    ) -> bool:
        """
        Check if a party has recursive access to an object.
        """
        # TODO: add support such that the evidence_id is optional

        # Get the evidence from the database
        evidence = db.get_evidence(evidence_id)
        if not evidence:
            return False

        # Check if the party has access to the object
        if self.party_has_access_to_object(db, party, object, action):
            return True

        # Check if the party has access to the previous delegation
        prev_delegation = evidence.prev_delegation
        if prev_delegation:
            prev_delegation = db.get_evidence(prev_delegation)
            if not prev_delegation:
                return False

            return self.has_recursive_access(db, prev_delegation, object, action)

        return False
