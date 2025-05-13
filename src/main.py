from models.base import database, evidence
from models.prev_party import service as prevparty_service
from models.prev_delegation import service as prevdelegation_service
from models.prev_delegation import evidence as prevdelegation_evidence
from models.all_prev_delegations import evidence as all_prev_delegation_evidence
from models.all_prev_delegations import service as allprevdelegation_service
from models.oracle import database as oracle_database
from models.oracle import service as oracleservice
import time



parties = ["owner1", "party1", "party2", "party3"]

# Create a dummy evidence database
db = database.Database()
oracle_db = oracle_database.Database()
[oracle_db.add_party(party) for party in parties]


# Create some dummy rules
rule1 = evidence.Rule("object1", "read", True)
rule2 = evidence.Rule("object1", "write", True)
rule3 = evidence.Rule("object2", "write", False)

prev_party_service = prevparty_service.PrevPartyService()
prev_delegation_service = prevdelegation_service.PrevDelegationService()
all_prev_delegation_service = allprevdelegation_service.AllPrevDelegationsService()
oracle_service = oracleservice.OracleService()


def simple_single_delegation_test():
    """
    Test the party_has_access_to_object function with simple single delegation.
    """
    evidence1 = evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="issuer1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="issuer1",
        receiver="party1",
        rules=[rule1, rule2],
    )
    db.add_evidence(evidence1)

    evidence2 = evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="issuer2",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="issuer2",
        receiver="party1",
        rules=[rule2, rule3],
    )
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
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
    )
    db.add_evidence(evidence3)

    evidence4 = evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
    )
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
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
        prev_delegation=None,
    )
    db.add_evidence(evidence3)

    evidence4 = prevdelegation_evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
        prev_delegation=30,
    )
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


def simple_double_delegation_test_all_prev_delegation():
    """
    Test the prev_party model with a simple double delegation,
    data_owner -> party1 -> party2.
    """
    evidence3 = all_prev_delegation_evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
        prev_delegations=None,
    )
    db.add_evidence(evidence3)

    evidence4 = all_prev_delegation_evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
        prev_delegations=[evidence3.identifier],
    )
    db.add_evidence(evidence4)

    # Test cases
    assert (
        all_prev_delegation_service.has_recursive_access(
            db, "party1", "owner1", "object1", "read", evidence3.identifier
        )
        == True
    )
    assert (
        all_prev_delegation_service.has_recursive_access(
            db, "party2", "owner1", "object1", "read", evidence4.identifier
        )
        == True
    )


def simple_double_delegation_test_oracle():
    """
    Test the oracle model with a simple double delegation,
    data_owner -> party1 -> party2.
    """
    oracle_db.add_delegation(
        delegator_id="owner1",
        delegatee_id="party1",
        resources=["object1"],
        actions=["read"],
        expires=time.time() + 1000000,
    )
    oracle_db.add_delegation(
        delegator_id="party1",
        delegatee_id="party2",
        resources=["object1"],
        actions=["read"],
        expires=time.time() + 1000000,
    )

    oracle_db.visualize_graph("oracle_graph.png")

    # Test cases
    assert (
        oracle_service.has_recursive_access(oracle_db, "party1", "owner1", "object1", "read") == True
    )
    assert (
        oracle_service.has_recursive_access(oracle_db, "party2", "owner1", "object1", "read") == True
    )
    assert (
        oracle_service.has_recursive_access(oracle_db, "party1", "owner1", "object2", "write") == False
    )
    assert (
        oracle_service.has_recursive_access(oracle_db, "party2", "owner1", "object2", "write") == False
    )



def triple_delegation_test():
    """
    Test the prev_party model with a triple delegation,
    data_owner -> party1 -> party2 -> party3.
    """
    evidence5 = evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="owner1",
        receiver="party1",
        rules=[rule1],
    )
    db.add_evidence(evidence5)

    evidence6 = evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party1",
        receiver="party2",
        rules=[rule1],
    )
    db.add_evidence(evidence6)

    evidence7 = evidence.Evidence(
        identifier=db.get_next_identifier(),
        data_owner="owner1",
        valid_from=0,
        valid_untill=time.time() + 1000000,
        issuer="party2",
        receiver="party3",
        rules=[rule1],
    )
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
    simple_double_delegation_test_all_prev_delegation()
    simple_double_delegation_test_oracle()
    triple_delegation_test()
    print("All tests passed!")
