from models.base import database
from models.prev_party import service as prevparty_service
from models.prev_delegation import service as prevdelegation_service
from models.all_prev_delegations import service as allprevdelegation_service
from models.oracle import database as oracle_database
from models.oracle import service as oracleservice
from models.on_delegate_check import service as ondelegatecheck_service
from models.concat import service as concat_service
from models.macaroons import database as macaroon_database
from models.macaroons import service as macaroon_service

import tests.main as tests

if __name__ == "__main__":
    # Test the Oracle model ---------------------------------------
    oracle_tester = tests.DelegationModelTests(
        oracle_database.Database,
        oracle_database.DatabaseBroker,
        oracleservice.OracleService,
    )
    results = oracle_tester.generate_report("reports/oracle_model.json")
    oracle_tester.print_test_results(results)

    # The previous party model --------------------------------
    prev_party_tester = tests.DelegationModelTests(
        database.Database, database.DatabaseBroker, prevparty_service.PrevPartyService
    )
    results = prev_party_tester.generate_report("reports/prev_party_model.json")
    prev_party_tester.print_test_results(results)

    # The previous delegation model ---------------------------
    prev_delegation_tester = tests.DelegationModelTests(
        database.Database, database.DatabaseBroker, prevdelegation_service.PrevDelegationService
    )
    results = prev_delegation_tester.generate_report("reports/prev_delegation_model.json")
    prev_delegation_tester.print_test_results(results)

    # The all previous delegation model -----------------------
    all_prev_delegation_tester = tests.DelegationModelTests(
        database.Database,
        database.DatabaseBroker,
        allprevdelegation_service.AllPrevDelegationsService,
    )
    results = all_prev_delegation_tester.generate_report("reports/all_prev_delegation_model.json")
    all_prev_delegation_tester.print_test_results(results)

    # The on delegate check model ----------------------------
    on_delegate_check_tester = tests.DelegationModelTests(
        database.Database,
        database.DatabaseBroker,
        ondelegatecheck_service.OnDelegateCheckService,
    )
    results = on_delegate_check_tester.generate_report("reports/on_delegate_check_model.json")
    on_delegate_check_tester.print_test_results(results)

    # The concat model ----------------------------------------
    concat_tester = tests.DelegationModelTests(
        database.Database, database.DatabaseBroker, concat_service.ConcatService
    )
    results = concat_tester.generate_report("reports/concat_model.json")
    concat_tester.print_test_results(results)

    # The macaroon model --------------------------------------
    macaroon_tester = tests.DelegationModelTests(
        macaroon_database.Database,
        database.DatabaseBroker,
        macaroon_service.Service,
    )
    results = macaroon_tester.generate_report("reports/macaroon_model.json", verbose=True)
    # results = macaroon_tester.run_tests(verbose=False)
    macaroon_tester.print_test_results(results)