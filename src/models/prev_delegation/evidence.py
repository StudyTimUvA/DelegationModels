from ..base import service as base_service
from ..base import evidence as base_evidence


class Evidence(base_evidence.Evidence):
    """
    Evidence class for the previous party model.
    Inherits from the base evidence class, adds a new prev_delegation attribute.
    """

    def __init__(
        self,
        identifier: int,
        data_owner: str,
        valid_from: int,
        valid_untill: int,
        issuer: str,
        receiver: str,
        rules: list,
        prev_delegation: int = None,
    ):
        super().__init__(identifier, data_owner, valid_from, valid_untill, issuer, receiver, rules)
        self.prev_delegation = prev_delegation
