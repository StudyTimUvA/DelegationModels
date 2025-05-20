from ..base import service as base_service
from ..base import evidence

class OnDelegateCheckService(base_service.BaseService):
    """
    Service class for the OnDelegateCheck model.
    This class provides methods to interact with the OnDelegateCheck model.
    """

    def __init__(self, database):
        super().__init__(database)

    def add_delegation(self, party1, party2, objects, actions, expiry):
        rule = evidence.Rule(
            object_ids=objects,
            actions=actions,
        )

        evid = evidence.Evidence(
            identifier=self.db.get_next_identifier(),
            issuer=party1,
            receiver=party2,
            rules=[rule],
            valid_from=0,
            valid_untill=expiry,
        )
        self.db.add_evidence(evid)
        return evid.identifier

    def has_access(self, delegatee, data_owner, object, action):
        evidences = self.db.get_evidence_by_party(delegatee)

        for evidence in evidences:
            if evidence.identifier in self.db.revocations:
                continue

            for rule in evidence.rules:
                if (
                    object in rule.object_ids
                    and action in rule.actions
                ):
                    return True
                
        return False

    def revoke_delegation(self, delegation_id):
        self.db.revocations.append(delegation_id)