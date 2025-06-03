from ..base import service as base_service
from ..base import evidence as base_evidence


class OnDelegateCheckService(base_service.BaseService):
    """
    Service class for the OnDelegateCheck model.
    This class provides methods to interact with the OnDelegateCheck model.
    """

    def add_delegation(
        self, party1, party2, objects, actions, expiry, database_name: str, evidence=None
    ):
        rule = base_evidence.Rule(
            object_ids=objects,
            actions=actions,
        )

        evid = base_evidence.Evidence(
            identifier=self.db_broker.get_database(database_name).get_next_identifier(),
            issuer=party1,
            receiver=party2,
            rules=[rule],
            valid_from=0,
            valid_untill=expiry,
            db_name=database_name,
        )
        self.db_broker.get_database(database_name).add_evidence(evid)
        return evid

    def has_access(self, delegatee, data_owner, object, action, db_name, evidence):
        # Note: the data_owner parameter is not used, as no traversal is done

        if evidence.identifier in self.db_broker.get_database(db_name).revocations:
            return False
        if evidence.receiver != delegatee:
            return False

        for rule in evidence.rules:
            if object in rule.object_ids and action in rule.actions:
                return True

        return False

    def revoke_delegation(self, delegation_id: int, db_name: str):
        self.db_broker.get_database(db_name).revocations.append(delegation_id)
