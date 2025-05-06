from models.base import database, evidence, service as base_service
from models.prev_party import service
import time


# Create a dummy evidence database
db = database.Database()

# Create some dummy rules
rule1 = evidence.Rule("object1", "read", True)
rule2 = evidence.Rule("object1", "write", True)
rule3 = evidence.Rule("object2", "write", False)

prev_party_service = service.PrevPartyService()


def simple_single_delegation_test():
    """
    Test the party_has_access_to_object function with simple single delegation.
    """
    evidence1 = evidence.Evidence(
        identifier=1,
        data_owner="issuer1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="issuer1",
        receiver="party1",
        rules=[rule1, rule2],
    )
    evidence2 = evidence.Evidence(
        identifier=2,
        data_owner="issuer2",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="issuer2",
        receiver="party1",
        rules=[rule2, rule3],
    )

    # Add evidence to the database
    db.add_evidence(evidence1)
    db.add_evidence(evidence2)

    # Check if a party has access to an object
    assert prev_party_service.party_has_access_to_object(db, "party1", "object1", "read") == True
    assert prev_party_service.party_has_access_to_object(db, "party1", "object1", "write") == True
    assert prev_party_service.party_has_access_to_object(db, "party1", "object2", "write") == False
    assert prev_party_service.party_has_access_to_object(db, "party1", "object2", "read") == False


def simple_double_delegation_test():
    """
    Test the prev_party model with a simple double delegation,
    data_owner -> party1 -> party2."""
    evidence3 = evidence.Evidence(
        identifier=3,
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
    )

    evidence4 = evidence.Evidence(
        identifier=4,
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
    )

    db.add_evidence(evidence3)
    db.add_evidence(evidence4)

    # Test cases
    assert (
        prev_party_service.has_recursive_access(db, "party1", "owner1", "object1", "read") == True
    )
    assert (
        prev_party_service.has_recursive_access(db, "party2", "owner1", "object1", "read") == True
    )
    assert (
        prev_party_service.has_recursive_access(db, "party1", "owner1", "object2", "write") == False
    )
    assert (
        prev_party_service.has_recursive_access(db, "party2", "owner1", "object2", "write") == False
    )


def triple_delegation_test():
    """
    Test the prev_party model with a triple delegation,
    data_owner -> party1 -> party2 -> party3.
    """
    evidence5 = evidence.Evidence(
        identifier=5,
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
    )

    evidence6 = evidence.Evidence(
        identifier=6,
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
    )

    evidence7 = evidence.Evidence(
        identifier=7,
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party2",
        receiver="party3",
        rules=[rule1],
    )

    db.add_evidence(evidence5)
    db.add_evidence(evidence6)
    db.add_evidence(evidence7)

    # Test cases
    assert (
        prev_party_service.has_recursive_access(db, "party3", "owner1", "object1", "read") == True
    )
    assert (
        prev_party_service.has_recursive_access(db, "party2", "owner1", "object2", "write") == False
    )


if __name__ == "__main__":
    simple_single_delegation_test()
    simple_double_delegation_test()
    triple_delegation_test()
    print("All tests passed!")
