from models.base import database, evidence
from models.prev_party import service as prevparty_service
from models.prev_delegation import service as prevdelegation_service
from models.prev_delegation import evidence as prevdelegation_evidence
import time


# Create a dummy evidence database
db = database.Database()

# Create some dummy rules
rule1 = evidence.Rule("object1", "read", True)
rule2 = evidence.Rule("object1", "write", True)
rule3 = evidence.Rule("object2", "write", False)

prev_party_service = prevparty_service.PrevPartyService()
prev_delegation_service = prevdelegation_service.PrevDelegationService()


def unique_id_generator():
    i = 1
    while True:
        yield i
        i += 1


id_gen = unique_id_generator()


def simple_single_delegation_test():
    """
    Test the party_has_access_to_object function with simple single delegation.
    """
    evidence1 = evidence.Evidence(
        identifier=next(id_gen),
        data_owner="issuer1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="issuer1",
        receiver="party1",
        rules=[rule1, rule2],
    )
    evidence2 = evidence.Evidence(
        identifier=next(id_gen),
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


def simple_double_delegation_test_party_id():
    """
    Test the prev_party model with a simple double delegation,
    data_owner -> party1 -> party2."""
    evidence3 = evidence.Evidence(
        identifier=next(id_gen),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
    )

    evidence4 = evidence.Evidence(
        identifier=next(id_gen),
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


def simple_double_delegation_test_prev_delegation():
    """
    Test the prev_party model with a simple double delegation,
    data_owner -> party1 -> party2.
    """
    evidence3 = prevdelegation_evidence.Evidence(
        identifier=next(id_gen),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
        prev_delegation=None,
    )

    evidence4 = prevdelegation_evidence.Evidence(
        identifier=next(id_gen),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
        prev_delegation=30,
    )

    db.add_evidence(evidence3)
    db.add_evidence(evidence4)

    # Test cases
    assert (
        prev_delegation_service.has_recursive_access(
            db, "party1", "owner1", "object1", "read", evidence3.identifier
        )
        == True
    )
    assert (
        prev_delegation_service.has_recursive_access(
            db, "party2", "owner1", "object1", "read", evidence4.identifier
        )
        == True
    )


def triple_delegation_test():
    """
    Test the prev_party model with a triple delegation,
    data_owner -> party1 -> party2 -> party3.
    """
    evidence5 = evidence.Evidence(
        identifier=next(id_gen),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
    )

    evidence6 = evidence.Evidence(
        identifier=next(id_gen),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
    )

    evidence7 = evidence.Evidence(
        identifier=next(id_gen),
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
    simple_double_delegation_test_party_id()
    simple_double_delegation_test_prev_delegation()
    triple_delegation_test()
    print("All tests passed!")
