from models.base import database, evidence, service
import time


# Create a dummy evidence database
db = database.Database()

# Create some dummy evidence
rule1 = evidence.Rule("object1", "read", True)
rule2 = evidence.Rule("object1", "write", True)
rule3 = evidence.Rule("object2", "write", False)
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
assert service.party_has_access_to_object(db, "party1", "object1", "read") == True
assert service.party_has_access_to_object(db, "party1", "object1", "write") == True
assert service.party_has_access_to_object(db, "party1", "object2", "write") == False
assert service.party_has_access_to_object(db, "party1", "object2", "read") == False

# Test the has_recursive_access function
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
assert service.has_recursive_access(db, "party1", "owner1", "object1", "read") == True
assert service.has_recursive_access(db, "party2", "owner1", "object1", "read") == True
assert service.has_recursive_access(db, "party1", "owner1", "object2", "write") == False
assert service.has_recursive_access(db, "party2", "owner1", "object2", "write") == False
