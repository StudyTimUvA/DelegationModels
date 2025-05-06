from ..base import service as base_service
from typing import List


class AllPrevDelegationsService(base_service.BaseService):
    def has_recursive_access(
        self,
        db,
        party: str,
        data_owner: str,
        object: str,
        action: str,
        final_evidence_id: int,
    ) -> bool:
        """
        Check if a party has access by iteratively checking each piece of evidence.
        """
        last_evidence = db.get_evidence(final_evidence_id)
        if not last_evidence:
            return False

        # Start with the final evidence and iterate through the chain of delegations
        current_evidence = last_evidence
        while current_evidence:
            # Check if the current evidence permits the action on the object
            if not any(
                rule.object_id == object and rule.action == action and rule.permit
                for rule in current_evidence.rules
            ):
                return False

            # If the current evidence's issuer is the data owner, access is valid
            if current_evidence.issuer == data_owner:
                return True

            # Move to the previous delegation if it exists
            if hasattr(current_evidence, 'prev_delegations') and current_evidence.prev_delegations:
                prev_evidence_ids = current_evidence.prev_delegations
                next_evidence = None

                for evidence_id in prev_evidence_ids:
                    evidence = db.get_evidence(evidence_id)
                    if evidence and evidence.receiver == current_evidence.issuer:
                        next_evidence = evidence
                        break

                if not next_evidence:
                    return False

                current_evidence = next_evidence
            else:
                return False

        return False



