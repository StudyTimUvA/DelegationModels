from ..base import service as base_service
from typing import List
from . import evidence as all_prev_delegation_evidence
from ..base import evidence as base_evidence


class AllPrevDelegationsService(base_service.BaseService):
    def _get_prev_delegation(
        self, party_id: str, object_ids: List[str], actions: List[str]
    ) -> all_prev_delegation_evidence.Evidence:
        """
        Get the previous delegation for a party and object.
        """
        for prev_db_name, evidence in self.db_broker.get_all_evidence_by_party(party_id):
            # Build a mapping from object_id to a list of actions
            object_actions = {}
            for rule in evidence.rules:
                for object_id in rule.object_ids:
                    if object_id not in object_actions:
                        object_actions[object_id] = list(rule.actions)
                    else:
                        object_actions[object_id].extend(rule.actions)

            # Check if all object_ids are present and all actions are allowed for each object
            if all(obj in object_actions for obj in object_ids) and all(
                act in object_actions[obj] for obj in object_ids for act in actions
            ):
                return prev_db_name, evidence

        return None, None

    def _is_evidence_for_search(
        self,
        evidence: base_evidence.Evidence,
        object_id: str,
        action: str,
    ):
        """
        Check if the evidence is for the search.
        """
        for rule in evidence.rules:
            if object_id in rule.object_ids and action in rule.actions:
                return True

        return False

    def has_access(
        self, delegatee: str, data_owner: str, object: str, action: str, db_name: str, evidence
    ) -> bool:
        """
        Check if a delegatee has access to an object based on the evidence in the database.

        Params:
            delegatee: the identifier of the delegatee.
            data_owner: the identifier of the data owner.
            object: the identifier of the object.
            action: the action to be performed on the object.

        Returns:
            True if the delegatee has access to the object, False otherwise.
        """
        if evidence.identifier in self.db_broker.get_database(db_name).revocations:
            return False

        if evidence.receiver != delegatee:  # Current evidence can not be used by the current party
            return False

        last_authorizes = None
        if self._is_evidence_for_search(evidence, object, action):
            if evidence.issuer == data_owner and evidence.receiver == delegatee:
                return True

            found_revocation = False
            for prev_db_name, prev_delegation in zip(
                evidence.prev_db_names, evidence.prev_delegations
            ):
                if (
                    prev_delegation.identifier
                    in self.db_broker.get_database(prev_db_name).revocations
                ):
                    found_revocation = True
                    break

                if self._is_evidence_for_search(prev_delegation, object, action):
                    if prev_delegation.issuer == data_owner:
                        last_authorizes = prev_delegation.receiver

                    elif prev_delegation.issuer == last_authorizes:
                        last_authorizes = prev_delegation.receiver
                    else:
                        break  # Found invalid delegation link

            if prev_delegation.receiver == evidence.issuer and not found_revocation:
                return True

        return False

    def add_delegation(
        self,
        party1: str,
        party2: str,
        objects: List[str],
        actions: List[str],
        expiry: float,
        database_name: str = None,
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
        prev_db_name = evidence.db_name if evidence else database_name
        prev_delegation = evidence

        rule = base_evidence.Rule(
            object_ids=objects,
            actions=actions,
        )
        evid = all_prev_delegation_evidence.Evidence(
            identifier=self.db_broker.get_database(database_name).get_next_identifier(),
            issuer=party1,
            receiver=party2,
            rules=[rule],
            valid_from=0,
            valid_untill=expiry,
            db_name=database_name,
            prev_delegations=(
                prev_delegation.prev_delegations + [prev_delegation] if prev_delegation else []
            ),
            prev_db_names=(
                prev_delegation.prev_db_names + [prev_db_name] if prev_delegation else []
            ),
        )
        self.db_broker.get_database(database_name).add_evidence(evid)
        return evid

    def revoke_delegation(self, delegation_id: int, database_name) -> bool:
        """
        Revoke a delegation in the database.

        Params:
            delegation_id: the ID of the delegation to be revoked.

        Returns:
            True if the revocation was successful, False otherwise.
        """
        self.db_broker.get_database(database_name).revocations.append(delegation_id)
