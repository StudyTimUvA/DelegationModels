from ..base import database


class Database(database.Database):
    """
    Database class for managing macaroons and delegations.
    Inherits from the base Database class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.keys = {}

    def get_key(self, identifier: str) -> str:
        """
        Get the key for a given identifier.

        Params:
            identifier: the identifier for which to get the key.

        Returns:
            The key associated with the identifier.
        """
        if identifier not in self.keys:
            raise ValueError(f"Key for identifier '{identifier}' not found.")
        return self.keys[identifier]

    def set_key(self, identifier: str, key: str) -> None:
        """
        Set the key for a given identifier.

        Params:
            identifier: the identifier for which to set the key.
            key: the key to set for the identifier.
        """
        self.keys[identifier] = key
