import time
from typing import List


class Database:
    def __init__(self):
        self.evidence = {
            # id: Evidence object
        }
        self.revocations = [
            # the ids
        ]

        # TODO: integrate revocations

    def get_next_identifier(self):
        """
        Get the next available identifier for evidence.

        Returns:
            An integer representing the next identifier.
        """
        if not self.evidence:
            return 1
        return max(self.evidence.keys()) + 1

    def add_evidence(self, evidence):
        """
        Add evidence to the database.

        Params:
            evidence: the evidence object to be added.
        """
        identifier = evidence.identifier
        if identifier in self.evidence:
            raise ValueError(f"Evidence with ID {identifier} already exists.")

        self.evidence[identifier] = evidence

    def get_evidence(self, identifier: int):
        """
        Retrieve evidence from the database.

        Params:
            identifier: the ID of the evidence to be retrieved.

        Returns:
            The evidence object if found, otherwise None.
        """
        return self.evidence.get(identifier, None)
    
    def get_evidences(self, ids: List[int]):
        """
        Retrieve multiple evidence objects from the database.

        Params:
            ids: a list of IDs of the evidence to be retrieved.

        Returns:
            A list of evidence objects.
        """
        return [self.evidence.get(identifier) for identifier in ids if identifier in self.evidence]

    def get_evidence_by_party(self, party_id: str):
        """
        Retrieve all currently relevant evidence for a specific party.
        Relevant evidence is defined as evidence that is valid at the current time.

        Params:
            party_id: the ID of the party whose evidence is to be retrieved.

        Returns:
            A list of evidence objects for the specified party.
        """
        return [
            evidence
            for evidence in self.evidence.values()
            if evidence.receiver == party_id
            and evidence.valid_from <= time.time() <= evidence.valid_untill
        ]
    
    def revoke(self, evidence_id: int):
        """
        Revoke evidence by its ID.

        Params:
            evidence_id: the ID of the evidence to be revoked.
        """
        self.revocations.append(evidence_id)
