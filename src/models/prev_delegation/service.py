from ..base import service as base_service
from . import evidence as prev_delegation_evidence
from ..base import evidence
from typing import List


class PrevDelegationService(base_service.BaseService):
    def _get_prev_delegation(self, party_id: str, object_ids: List[str], actions: List[str]) -> str:
        """
        Get the previous delegation for a party and object.
        """
        # TODO: format this horrible code
        for evidence in self.db.get_evidence_by_party(party_id):
            rule_objects = [
                {object_id: rule.actions}
                for rule in evidence.rules
                for object_id in rule.object_ids
            ]
            new = {}
            for r in rule_objects:
                for k, v in r.items():
                    if k not in new:
                        new[k] = v
                    else:
                        new[k].extend(v)

            # check if the object_ids and actions are in the evidence
            if all(obj in new for obj in object_ids) and all(
                act in new[obj] for obj in object_ids for act in actions
            ):
                return evidence.identifier

        return None

    def add_delegation(self, party1, party2, objects, actions, expiry):
        prev_delegation = self._get_prev_delegation(party1, objects, actions)

        rule = evidence.Rule(
            object_ids=objects,
            actions=actions,
        )
        evid = prev_delegation_evidence.Evidence(
            identifier=self.db.get_next_identifier(),
            issuer=party1,
            receiver=party2,
            rules=[rule],
            valid_from=0,
            valid_untill=expiry,
            prev_delegation=prev_delegation,
        )
        self.db.add_evidence(evid)
        return evid.identifier

    def party_has_access_to_object(self, party_id: str, object_id: str, action: str) -> bool:
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
        for evidence in self.db.get_evidence_by_party(party_id):
            for rule in evidence.rules:
                if rule.object_id == object_id and rule.permit and rule.action == action:
                    return True

        return False

    def _is_evidence_for_search(
        self,
        evidence: evidence.Evidence,
        party_id: str,
        object_id: str,
        action: str,
    ):
        """
        Check if the evidence is for the search.
        """
        for rule in evidence.rules:
            if (
                object_id in rule.object_ids
                and action in rule.actions
                and evidence.receiver == party_id
            ):
                return True

        return False

    def has_recursive_access(
        self,
        evidence_identifier: int,
        evidence: evidence.Evidence,
        data_owner: str,
        object_id: str,
        action: str,
    ) -> bool:
        """
        Check if the evidence has recursive access to an object.
        """
        if evidence_identifier in self.db.revocations:
            return False

        if evidence.issuer == data_owner:
            return True

        if self._is_evidence_for_search(evidence, evidence.receiver, object_id, action):
            # Recursively check if the issuer has access
            return self.has_recursive_access(
                evidence.identifier,
                self.db.get_evidence(evidence.issuer),
                data_owner,
                object_id,
                action,
            )

        return False

    def has_access(
        self,
        current_party: str,
        data_owner: str,
        object: str,
        action: str,
    ) -> bool:
        """
        Check if a party has recursive access to an object.
        """
        evidences = self.db.get_evidence_by_party(current_party)

        for evidence in evidences:
            if evidence.identifier in self.db.revocations:
                continue

            if self._is_evidence_for_search(evidence, current_party, object, action):
                if evidence.issuer == data_owner:
                    return True

                # Recursively check if the issuer has access
                if self.has_access(evidence.issuer, data_owner, object, action):
                    return True

        return False

    def revoke_delegation(self, delegation_id: int) -> bool:
        """
        Revoke a delegation in the database.

        Params:
            delegation_id: the ID of the delegation to be revoked.

        Returns:
            True if the revocation was successful, False otherwise.
        """
        evidence = self.db.get_evidence(delegation_id)
        if evidence:
            self.db.revoke(delegation_id)
            return True
        return False
