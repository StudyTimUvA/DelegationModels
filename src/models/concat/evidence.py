from ..base import evidence


class ConcatEvidence(evidence.Evidence):
    # This model is simmilar to the prev_delegation model, but stores the actual previous evidence, rather than an ID.
    def __init__(self, identifier, issuer, receiver, rules, valid_from, valid_untill, db_name, prev_evidence: evidence.Evidence = None):
        super().__init__(identifier, issuer, receiver, rules, valid_from, valid_untill, db_name)
        self.prev_evidence = prev_evidence