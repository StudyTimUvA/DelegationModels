from ..base import evidence as base_evidence
from typing import List


class Evidence(base_evidence.Evidence):
    """
    Evidence class for the previous party model.
    Inherits from the base evidence class, adds a new prev_delegation attribute.
    """

    def __init__(
        self,
        identifier: int,
        issuer: str,
        receiver: str,
        rules: list[base_evidence.Rule],
        valid_from: int,
        valid_untill: int,
        prev_delegations: List[int] = None,
    ):
        super().__init__(
            identifier=identifier,
            issuer=issuer,
            receiver=receiver,
            rules=rules,
            valid_from=valid_from,
            valid_untill=valid_untill,
        )
        self.prev_delegations = prev_delegations
