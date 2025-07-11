import time
from typing import List, Tuple
from . import evidence


class Database:
    def __init__(self, name: str):
        self.evidence = {
            # id: Evidence object
        }
        self.revocations = [
            # the ids
        ]

        self.id_counter = 0
        self.name = name

    def add_parties(self, party_ids: List[str]):
        """
        Add the parties to the database.
        This method is optional, and is defined as a no-op by default.

        Params:
                party_ids: a list of party IDs to be added.
        """
        return

    def get_next_identifier(self):
        """
        Get the next available identifier for evidence.

        Returns:
            An integer representing the next identifier.
        """
        self.id_counter += 1
        return self.id_counter

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

    def get_evidence_by_party(self, party_id: str) -> List[evidence.Evidence]:
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
            if evidence.receiver == party_id and evidence.valid_from <= time.time() <= evidence.valid_untill
        ]

    def revoke(self, evidence_id: int):
        """
        Revoke evidence by its ID.

        Params:
            evidence_id: the ID of the evidence to be revoked.
        """
        self.revocations.append(evidence_id)


class DatabaseBroker:
    """This class functions as a broker for multiple databases, allowing to simulate a multi-AR test environment.
    In reality, this system would likely be implemented using a DNS (like system) to route requests to the appropriate database.
    """

    def __init__(self):
        self.databases = {}

    def add_database(self, db_name: str, database: Database):
        """
        Add a database to the broker.

        Params:
            db_name: the name of the database.
            database: the Database object to be added.
        """
        self.databases[db_name] = database

    def get_database(self, db_name: str) -> Database:
        """
        Retrieve a database by its name.

        Params:
            db_name: the name of the database to retrieve.

        Returns:
            The Database object if found, otherwise None.
        """
        return self.databases.get(db_name, None)

    def get_database_entry(self, db_name: str, identifier: int):
        """
        Retrieve a specific entry from a database by its identifier.

        Params:
            db_name: the name of the database.
            identifier: the ID of the evidence to retrieve.

        Returns:
            The evidence object if found, otherwise None.
        """
        database = self.get_database(db_name)
        if database:
            return database.get_evidence(identifier)
        return None

    def get_evidence_by_party(self, db_name: str, party_id: str) -> List[evidence.Evidence]:
        """
        Retrieve all currently relevant evidence for a specific party from a specific database.

        Params:
            db_name: the name of the database.
            party_id: the ID of the party whose evidence is to be retrieved.
        Returns:
            A list of evidence objects for the specified party.
        """
        database = self.get_database(db_name)
        if database:
            return database.get_evidence_by_party(party_id)
        return []

    def get_all_evidence_by_party(self, party_id: str) -> List[Tuple[str, evidence.Evidence]]:
        """
        Retrieve all currently relevant evidence for a specific party across all databases.

        Params:
            party_id: the ID of the party whose evidence is to be retrieved.

        Returns:
            A list of tuples, each containing the database name and the evidence object for the specified party.
        """
        all_evidence = []
        for db_name, db in self.databases.items():
            for ev in db.get_evidence_by_party(party_id):
                all_evidence.append((db_name, ev))
        return all_evidence
