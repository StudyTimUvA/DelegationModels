class Rule:
    """A rule object representing a permission or restriction on an object."""

    def __init__(self, object_id: str, action: str, permit: bool):
        """
        Initialize the Rule object.

        Params:
            object_id: the identifier of the object to which the rule applies.
            action: the action that is allowed or denied by the rule.
            permit: a boolean indicating whether the action is permitted (True) or denied (False).
        """
        self.object_id = object_id
        self.action = action
        self.permit = permit


class Evidence:
    """
    Evidence class representing a piece of evidence in the system.
    This is based on the JWT used by the iSHARE foundation, but limited to the minimum
    fields required for the delegation implementation.
    """

    def __init__(
        self,
        identifier: int,
        data_owner: str,
        valid_from: int,
        valid_untill: int,
        issuer: str,
        receiver: str,
        rules: list[Rule],
    ):
        """
        Initialize the Evidence object.

        Params:
            identifier: the unique identifier of the evidence.
            valid_from: the start time of the evidence validity period in seconds.
            valid_untill: the end time of the evidence validity period in seconds.
            issuer: the identifier of the entity that issued the evidence.
            receiver: the identifier of the entity that received the evidence.
            rules: a list of Rule objects that define the conditions of the evidence.
        """
        self.identifier = identifier
        self.data_owner = data_owner
        self.valid_from = valid_from
        self.valid_untill = valid_untill
        self.issuer = issuer
        self.receiver = receiver
        self.rules = rules
