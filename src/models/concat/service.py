from ..base import service as base_service
from typing import List
from .evidence import ConcatEvidence
from ..base.evidence import Rule


class ConcatService(base_service.BaseService):
    def add_delegation(
        self,
        party1: str,
        party2: str,
        objects: List[str],
        actions: List[str],
        expiry: float,
        database_key: str,
        evidence: ConcatEvidence = None,
    ) -> ConcatEvidence:
        """
        Add a delegation from party1 to party2 in the database.

        Params:
            party1: the ID of the delegator.
            party2: the ID of the delegatee.
            objects: a list of objects being delegated.
            actions: a list of actions that can be performed on the objects.
            expiry: the expiration time of the delegation.
            database_key: the name of the database to add the delegation to.
            evidence: an optional Evidence object containing informaion about the delegation the new one is based on.

        Returns:
            The ID of the newly added delegation.
        """
        rule = Rule(
            object_ids=objects,
            actions=actions,
        )

        evid = ConcatEvidence(
            identifier=self.db_broker.get_database(database_key).get_next_identifier(),
            issuer=party1,
            receiver=party2,
            rules=[rule],
            valid_from=0,
            valid_untill=expiry,
            db_name=database_key,
            prev_evidence=evidence,
        )

        # Does not need to be added to the database, as this evidence can be standalone.

        return evid

    def revoke_delegation(self, delegation_id: int, database_key: str):
        """
        Revoke a delegation in the database.

        Params:
            delegation_id: the ID of the delegation to be revoked.
        """
        self.db_broker.get_database(database_key).revocations.append(delegation_id)

    def evidence_is_revoked(self, evidence: ConcatEvidence, db_name: str) -> bool:
        """
        Check if the evidence is revoked in the database.

        Params:
            evidence: the ConcatEvidence object to check.
            db_name: the name of the database to check in.

        Returns:
            True if the evidence is revoked, False otherwise.
        """
        return evidence.identifier in self.db_broker.get_database(db_name).revocations

    def has_access(self, delegatee, data_owner, object, action, db_name, evidence):
        def is_relevant_evidence(evidence):
            return any(
                object in rule.object_ids and action in rule.actions for rule in evidence.rules
            )

        if not is_relevant_evidence(evidence):
            return False

        if evidence.receiver != delegatee:
            return False

        if self.evidence_is_revoked(evidence, db_name):
            return False

        new_evidence = evidence
        while new_evidence.prev_evidence is not None:
            new_evidence = new_evidence.prev_evidence

            if not is_relevant_evidence(new_evidence):
                return False

            if self.evidence_is_revoked(new_evidence, db_name):
                return False

        if new_evidence.issuer != data_owner:
            return False

        return True
