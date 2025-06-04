from ..base import evidence as base_evidence


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
        db_name: str,
        prev_db_name: str = None,
    ):
        super().__init__(
            identifier=identifier,
            issuer=issuer,
            receiver=receiver,
            rules=rules,
            valid_from=valid_from,
            valid_untill=valid_untill,
            db_name=db_name,
        )
        self.prev_db_name = prev_db_name
