from models.base import database, evidence
from models.prev_party import service as prevparty_service
from models.prev_delegation import service as prevdelegation_service
from models.prev_delegation import evidence as prevdelegation_evidence
from models.all_prev_delegations import evidence as all_prev_delegation_evidence
from models.all_prev_delegations import service as allprevdelegation_service
from models.oracle import database as oracle_database
from models.oracle import service as oracleservice

import tests.main as tests

if __name__ == "__main__":
    oracle_tester = tests.DelegationModelTests(
        oracle_database.Database,
        oracleservice.OracleService,
    )
    results = oracle_tester.run_tests(verbose=False)
    oracle_tester.print_test_results(results)

    prev_party_tester = tests.DelegationModelTests(
        database.Database, prevparty_service.PrevPartyService
    )
    results = prev_party_tester.run_tests(verbose=False)
    prev_party_tester.print_test_results(results)

    prev_delegation_tester = tests.DelegationModelTests(
        database.Database, prevdelegation_service.PrevDelegationService
    )
    results = prev_delegation_tester.run_tests(verbose=False)
    prev_delegation_tester.print_test_results(results)

    all_prev_delegation_tester = tests.DelegationModelTests(
        database.Database, allprevdelegation_service.AllPrevDelegationsService
    )
    results = all_prev_delegation_tester.run_tests(verbose=False)
    all_prev_delegation_tester.print_test_results(results)
