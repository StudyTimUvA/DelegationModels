import time
import inspect
import json


class DelegationModelTests:
    def __init__(
        self,
        db_class,
        database_broker_class,
        service_class,
        performance_time_limit=1,
        performance_test_count=10,
    ):
        # Set up simulation components
        self.db_class = db_class
        self.database_broker_class = database_broker_class
        self.service = service_class(self.db_class, self.database_broker_class())
        self.service.db_broker.add_database("base", self.service.db_class("base"))

        # Store performance test parameters
        self.performance_time_limit = performance_time_limit
        self.performance_test_count = performance_test_count

        self.PARTIES = [
            "owner1",
            "party1",
            "party2",
            "party3",
            "party4",
        ]

    def generate_report(self, filename: str, expectations: dict = None, verbose=False) -> dict:
        """
        Generate a report of the test results and save it to a json file.

        Params:
            filename: The name of the file to save the report to, without extension.
            expectations: A dictionary with the expected results for each category (dict[str, bool]).

        Returns:
            A dictionary with the test results, including performance and summary.
        """

        tests = {
            "basic_delegations": [self.test_single_delegation, self.test_triple_delegation],
            "flexibility": [
                self.test_parallel_paths,
                self.test_partial_delegations,
                self.test_changing_paths,
            ],
            "revocation": [
                self.test_simple_revocation,
                self.test_triple_delegation_final_revoked,
                self.test_triple_delegation_first_revoked_propagation,
            ],
            "multi_ar": [
                self.test_multi_database_delegation,
                self.test_multi_database_first_delegation_revocation,
                self.test_multi_database_parallel_paths,
            ],
        }
        tests["other"] = [
            test_method
            for name, test_method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test_")
            and test_method not in [test for test_list in tests.values() for test in test_list]
        ]

        results = {}
        for category, test_list in tests.items():
            results[category] = {}
            for test_method in test_list:
                test_name = test_method.__name__
                self.service.db_broker.add_database(
                    "base",
                    self.service.db_class("base"),
                )
                self.service.add_parties(self.PARTIES, "base")

                try:
                    test_method()
                    results[category][test_name] = True
                    print(f"Test {test_name} passed.") if verbose else None
                except Exception as e:
                    results[category][test_name] = False
                    print(f"Test {test_name} failed: {e}") if verbose else None

        results = {"tests": results}

        # Performance test
        self.service.db_broker.add_database("base", self.service.db_class("base"))
        performance_results = self.get_performance_values()
        results["performance"] = performance_results

        # # Reset database
        self.service.db_broker.add_database("base", self.service.db_class("base"))
        performance_additional_parties = self.get_performance_values_additional_parties()
        results["performance_additional_parties"] = performance_additional_parties

        # Reset database
        self.service.db_broker.add_database("base", self.service.db_class("base"))
        performance_related_additional_parties = self.get_performance_values_related_additional_parties()
        results["performance_related_additional_parties"] = performance_related_additional_parties

        # Add a summary per category
        results["summary"] = {}
        for category, test_results in results["tests"].items():
            all_passed = all(test_results.values())
            results["summary"][category] = all_passed

        with open(filename, "w") as f:
            json.dump(results, f, indent=4)

        return results

    def run_tests(self, verbose=True) -> dict:
        """
        Run all tests in the class and return the results.

        Params:
            verbose: If True, print the test results.

        Returns:
            A dictionary with the test names as keys and the results as values.
        """
        tests = [
            (name, test_method)
            for name, test_method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test_")
        ]

        results = {}

        for name, test_method in tests:
            self.service.db.add_parties(self.PARTIES)

            if verbose:
                print(f"Running test: {name}")

            try:
                test_method()
                if verbose:
                    print(f"Test {name} passed.")

                results[name] = True
            except Exception as e:
                if verbose:
                    print(f"Test {name} failed: {e}")

                results[name] = False

        return results

    def print_test_results(self, results) -> None:
        """
        Print the test results in a formatted table.

        Params:
            results: A dictionary with the test names as keys and the results as values.
        """
        CHECK = "✓"
        CROSS = "✗"

        results = results["tests"]

        print(f"Test Results: {self.service.__class__.__name__}")

        longest_cat_name = max(len(name) for name in results.keys())
        longest_test_name = max(
            max(len(test_name) for test_name in cat_results.keys()) for cat_results in results.values()
        )
        print(f"| {'Category':<{longest_cat_name}} | {'Test Name':<{longest_test_name}} | Result |")
        print("-" * (longest_cat_name + longest_test_name + 16))
        for category, cat_results in results.items():

            for name, result in cat_results.items():
                result_symbol = CHECK if result else CROSS
                print(f"| {category:<{longest_cat_name}} | {name:<{longest_test_name}} | {result_symbol}      |")

        print("-" * (longest_cat_name + longest_test_name + 16))
        print("")

    def test_single_delegation(self):
        """
        Test the delegation model with a single delegation.
        data_owner -> party1.
        """
        evid = self.service.add_delegation(
            "owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base", evidence=None
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid) == True
        ), "party1 should have read access to object1 in DO->p1"

        # Test cases that should hold false
        assert (
            self.service.has_access("party1", "owner1", "object2", "read", "base", evid) == False
        ), "party1 should have access to object1 in DO->p1"
        assert (
            self.service.has_access("party1", "owner1", "object2", "write", "base", evid) == False
        ), "party1 should have access to object1 in DO->p1"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", evid) == False
        ), "party2 should not have access to object1 in DO->p1"

    def test_triple_delegation(self):
        """
        Test the delegation model with a triple delegation,
        data_owner -> party1 -> party2 -> party3.
        """
        evid1 = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base")
        evid2 = self.service.add_delegation(
            "party1", "party2", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid1
        )
        evid3 = self.service.add_delegation(
            "party2", "party3", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid2
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid1) == True
        ), "party1 should have read access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", evid2) == True
        ), "party2 should have read access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read", "base", evid3) == True
        ), "party3 should have read access to object1 in DO->p1->p2->p3"

        # Test cases that should hold false
        for evid in [evid1, evid2, evid3]:
            assert (
                self.service.has_access("party1", "owner1", "object1", "write", "base", evid) == False
            ), "party1 should not have write access to object1 in DO->p1->p2->p3"
            assert (
                self.service.has_access("party2", "owner1", "object1", "write", "base", evid) == False
            ), "party2 should not have write access to object1 in DO->p1->p2->p3"
            assert (
                self.service.has_access("party3", "owner1", "object1", "write", "base", evid) == False
            ), "party3 should not have write access to object1 in DO->p1->p2->p3"
            assert (
                self.service.has_access("party4", "owner1", "object1", "read", "base", evid) == False
            ), "party4 should have any access to object1 in DO->p1->p2->p3"

    def test_parallel_paths(self):
        """
        Test the delegation model with parallel paths (aka diveringing/converging paths),
        data_owner -> party1 -> party2 and data_owner -> party2.
        """
        evid1 = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base")
        evid2 = self.service.add_delegation(
            "party1", "party2", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid1
        )
        evid3 = self.service.add_delegation(
            "owner1", "party2", ["object1"], ["read", "write"], time.time() + 1000000, "base"
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid1) == True
        ), "party1 should have read access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", evid2) == True
        ), "party2 should have read access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object1", "write", "base", evid3) == True
        ), "party2 should have write access to object1 in DO->p1->p2"

        # Test cases that should hold false
        for evid in [evid1, evid2, evid3]:
            assert (
                self.service.has_access("party1", "owner1", "object1", "write", "base", evid) == False
            ), "party1 should not have write access to object1 in DO->p1->p2"
            assert (
                self.service.has_access("party3", "owner1", "object1", "read", "base", evid) == False
            ), "party3 should not have access to object1 in DO->p1->p2"

    def test_partial_delegations(self):
        """
        Test the delegation model with partial delegations,
        data_owner -> party1 -> party2, where party1->party2 contains a subset of the rights of party1.
        """
        evid1 = self.service.add_delegation(
            "owner1", "party1", ["object1", "object2"], ["read"], time.time() + 1000000, "base"
        )
        evid2 = self.service.add_delegation(
            "party1", "party2", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid1
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid1) == True
        ), "party1 should have read access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party1", "owner1", "object2", "read", "base", evid1) == True
        ), "party1 should have read access to object2 in DO->p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", evid2) == True
        ), "party2 should have read access to object1 in DO->p1->p2"

        # Test cases that should hold false
        for evid in [evid1, evid2]:
            assert (
                self.service.has_access("party2", "owner1", "object2", "read", "base", evid) == False
            ), "party2 should not have read access to object2 in DO->p1->p2"

    def test_invalid_delegation(self):
        """
        Test the delegation model with an invalid delegation,
        party1 -> party2, where party1 has no access to object3.
        """
        delegation = self.service.add_delegation(
            "party1", "party2", ["object3"], ["read"], time.time() + 1000000, "base"
        )

        # Test cases that should hold true
        assert not delegation, "Delegation should not be valid as party1 has no access to object3"

        # Test cases that should hold false
        assert (
            self.service.has_access("party1", "owner1", "object3", "read", "base") == False
        ), "party1 should not have read access to object3 in p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object3", "read", "base") == False
        ), "party2 should not have read access to object3 in p1->p2"

    def test_simple_revocation(self):
        """
        Test the delegation model with a simple revocation,
        data_owner -> party1, where party1 is revoked.
        """
        evid = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base")
        self.service.revoke_delegation(evid.identifier, "base")

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid) == False
        ), "party1 should not have read access to object1 in DO->p1, when revoked"

    def test_triple_delegation_final_revoked(self):
        """
        Test the delegation model with a triple delegation,
        data_owner -> party1 -> party2 -> party3, where party3 is revoked.
        """
        evid1 = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base")
        evid2 = self.service.add_delegation(
            "party1", "party2", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid1
        )
        evid3 = self.service.add_delegation(
            "party2", "party3", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid2
        )
        self.service.revoke_delegation(evid3.identifier, "base")

        # Test cases
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid1) == True
        ), "party1 should have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", evid2) == True
        ), "party2 should have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read", "base", evid3) == False
        ), "party3 should not have read access to object1 in DO->p1->p2->p3, when revoked"

    def test_triple_delegation_first_revoked_propagation(self):
        """
        Test the delegation model with a triple delegation,
        data_owner -> party1 -> party2 -> party3, where party1 is revoked.
        """
        evid1 = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base")
        evid2 = self.service.add_delegation(
            "party1", "party2", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid1
        )
        evid3 = self.service.add_delegation(
            "party2", "party3", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid2
        )
        self.service.revoke_delegation(evid1.identifier, "base")

        # Test cases
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid1) == False
        ), "party1 should not have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", evid2) == False
        ), "party2 should not have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read", "base", evid3) == False
        ), "party3 should not have read access to object1 in DO->p1->p2->p3, when revoked"

    def test_changing_paths(self):
        """
        Test the delegation model with changing paths,
        data_owner -> party1 -> party2 -> party3, where party1 is revoked and data_owner->party2 is added.
        """
        evid1 = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 100000, "base")
        evid2 = self.service.add_delegation(
            "party1", "party2", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid1
        )
        evid3 = self.service.add_delegation(
            "party2", "party3", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid2
        )
        self.service.revoke_delegation(evid1.identifier, "base")

        new_evid = self.service.add_delegation("owner1", "party2", ["object1"], ["read"], time.time() + 1000000, "base")

        # Test cases
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "base", new_evid) == True
        ), "party2 should have read access to object1 in DO->p2->p3"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read", "base", evid3) == True
        ), "party2 should have read access to object1 in DO->p2->p3, when revoked"

    def test_multi_database_delegation(self):
        """
        Test the delegation model with multiple databases.
        This tests the delegation model with a single delegation in a different database.
        """
        self.service.db_broker.add_database("other_db", self.service.db_class("other_db"))
        self.service.add_parties(["owner1", "party1"], "other_db")

        evid1 = self.service.add_delegation(
            "owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "other_db"
        )

        evid2 = self.service.add_delegation(  # This forms a bridge!
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
            "other_db",
            evidence=evid1,
        )

        evid3 = self.service.add_delegation(
            "party2", "party3", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid2
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "other_db", evid2) == True
        ), "party2 should have read access to object1 in DO->p1->p2 in other_db"
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "other_db", evid1) == True
        ), "party1 should have read access to object1 in DO->p1->p2 in other_db"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read", "base", evid3) == True
        ), "party3 should have read access to object1 in DO->p1->p2->p3 in base"

        # Test cases that should hold false
        for evid in [evid1, evid2]:
            assert (
                self.service.has_access("party3", "owner1", "object1", "read", "other_db", evid) == False
            ), "party3 should not have access to object1 in DO->p1 in other_db"

    def test_multi_database_first_delegation_revocation(self):
        """
        Test the delegation model with multiple databases,
        where the first delegation is revoked.
        """
        self.service.db_broker.add_database("other_db", self.service.db_class("other_db"))
        self.service.add_parties(self.PARTIES, "other_db")

        evid1 = self.service.add_delegation("owner1", "party1", ["object1"], ["read"], time.time() + 1000000, "base")

        evid2 = self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
            "other_db",
            evidence=evid1,
        )

        # Revoke the first delegation
        self.service.revoke_delegation(evid1.identifier, "base")

        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "other_db", evid2) == False
        ), "party2 should not have read access to object1 in DO->p1->p2 in other_db"
        assert (
            self.service.has_access("party1", "owner1", "object1", "read", "base", evid1) == False
        ), "party1 should not have read access to object1 in DO->p1->p2 in base"

    def test_multi_database_parallel_paths(self):
        """
        Test the delegation model with multiple databases and a parallel path
        """
        OTHER_DB_PARTIES = [  # Limit parties to other databases to force bridges
            "party_b1",
        ]

        self.service.db_broker.add_database("other_db_left", self.service.db_class("other_db_left"))
        self.service.add_parties(OTHER_DB_PARTIES, "other_db_left")

        self.service.db_broker.add_database("other_db_right", self.service.db_class("other_db_right"))
        self.service.add_parties(OTHER_DB_PARTIES, "other_db_right")

        evid1 = self.service.add_delegation(
            "owner1", "party_b1", ["object1"], ["read", "write"], time.time() + 1000000, "base"
        )
        evid2 = self.service.add_delegation(
            "party_b1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
            "other_db_left",
            evidence=evid1,
        )
        evid3 = self.service.add_delegation(
            "party_b1",
            "party3",
            ["object1"],
            ["write"],
            time.time() + 1000000,
            "other_db_right",
            evidence=evid1,
        )
        evid4 = self.service.add_delegation(
            "party2", "party4", ["object1"], ["read"], time.time() + 1000000, "base", evidence=evid2
        )
        evid5 = self.service.add_delegation(
            "party3",
            "party4",
            ["object1"],
            ["write"],
            time.time() + 1000000,
            "base",
            evidence=evid3,
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party2", "owner1", "object1", "read", "other_db_left", evid2) == True
        ), "party2 should have read access to object1 in DO->p1->p2 in other_db_left"
        assert (
            self.service.has_access("party3", "owner1", "object1", "write", "other_db_right", evid3) == True
        ), "party3 should have write access to object1 in DO->p1->p3 in other_db_right"
        assert (
            self.service.has_access("party4", "owner1", "object1", "read", "base", evid4) == True
        ), "party4 should have read access to object1 in DO->p1->p2->p4 in base"
        assert (
            self.service.has_access("party4", "owner1", "object1", "write", "base", evid5) == True
        ), "party4 should have write access to object1 in DO->p1->p3->p4 in base"

    def get_performance_values(self):
        """
        Test the performance of the delegation model with a growing number of parties and delegations.
        This task focusses on the performance of the has_access method.
        """

        numbers_of_delegations = [5, 10, 50, 100, 250, 500]
        last_party_number = 0
        times_taken = []

        self.service.db_broker.get_database("base").add_parties(
            [f"party{i}" for i in range(0, max(numbers_of_delegations) + 1)]
        )

        prev_delegation = None

        for idx, number_of_delegations in enumerate(numbers_of_delegations):
            number_to_add = number_of_delegations - (numbers_of_delegations[idx - 1] if idx > 0 else 0)

            for _ in range(number_to_add):
                prev_delegation = self.service.add_delegation(
                    f"party{last_party_number}",
                    f"party{last_party_number + 1}",
                    ["object1"],
                    ["read"],
                    time.time() + 1000000,
                    "base",
                    evidence=prev_delegation,
                )
                last_party_number += 1

            elapsed_avg = 0
            for _ in range(self.performance_test_count):
                start_time = time.time()
                success = self.service.has_access(
                    f"party{last_party_number}",
                    f"party0",
                    "object1",
                    "read",
                    "base",
                    prev_delegation,
                )
                end_time = time.time()
                elapsed_time = end_time - start_time
                elapsed_avg += elapsed_time

                # If a single test takes longer than the performance time limit, fail the test
                assert (
                    elapsed_time < self.performance_time_limit
                ), f"Performance test failed, took {elapsed_time:.6f} seconds, expected less than {self.performance_time_limit:.6f} seconds."

            elapsed_avg /= self.performance_test_count

            assert success, "Performance test failed, as access was expected, but failed."

            times_taken.append(format(elapsed_avg, ".6f"))

        return dict(zip(numbers_of_delegations, times_taken))

    def get_performance_values_additional_parties(self):
        """
        Test the performance of the delegation model with a growing number of parties and delegations.
        This starts with a single long delegation chain, and then adds different delegations to the existing parties.
        """

        number_of_delegations = 250
        last_party_number = 0

        self.service.db_broker.get_database("base").add_parties([f"party{i}" for i in range(number_of_delegations + 1)])

        prev_delegation = None
        delegation_per_party = {"party0": None}  # Store the delegation for each party

        # Create the single long delegation chain
        for _ in range(number_of_delegations):
            prev_delegation = self.service.add_delegation(
                f"party{last_party_number}",
                f"party{last_party_number + 1}",
                ["object1", "object2"],
                ["read"],
                time.time() + 1000000,
                "base",
                evidence=prev_delegation,
            )
            delegation_per_party[f"party{last_party_number+1}"] = prev_delegation
            last_party_number += 1

        additional_delegations = [0, 5, 10, 50, 100, 500, 1000]
        times_taken = []
        parties = [f"party{i}" for i in range(number_of_delegations)]
        links = [(party, party2) for party2 in parties for party in parties if party != party2]
        for idx, num_add_delegations in enumerate(additional_delegations):
            start = additional_delegations[idx - 1] if idx > 0 else 0
            end = additional_delegations[idx]
            for source, target in links[start:end]:
                self.service.add_delegation(
                    source,
                    target,
                    [f"object2"],
                    ["read"],
                    time.time() + 1000000,
                    "base",
                    evidence=delegation_per_party[source],
                )

            # self.service.db.visualize_graph(f"delegation_graph_{num_add_delegations}.png")
            # for entry in self.service.db.graph.edges(data=True):
            # print(entry)

            elapsed_avg = 0
            for _ in range(self.performance_test_count):
                start_time = time.time()
                success = self.service.has_access(
                    f"party{number_of_delegations}",
                    f"party0",
                    "object1",
                    "read",
                    "base",
                    evidence=prev_delegation,
                )
                end_time = time.time()
                elapsed_time = end_time - start_time
                elapsed_avg += elapsed_time

                # print(num_add_delegations, success)

                # If a single test takes longer than the performance time limit, fail the test
                assert (
                    elapsed_time < self.performance_time_limit
                ), f"Performance test failed, took {elapsed_time:.6f} seconds, expected less than {self.performance_time_limit:.6f} seconds."

            elapsed_avg /= self.performance_test_count

            assert success, "Performance test failed, as access was expected, but failed."

            times_taken.append(format(elapsed_avg, ".6f"))

        return dict(zip(additional_delegations, times_taken))

    def get_performance_values_related_additional_parties(self):
        number_of_delegations = 250
        number_of_additional_parties = 500
        last_party_number = 0
        total_parties = number_of_delegations + number_of_additional_parties

        self.service.db_broker.get_database("base").add_parties([f"party{i}" for i in range(total_parties + 1)])

        prev_delegation = None
        delegation_per_party = {"party0": None}  # Store the delegation for each party

        # Create the single long delegation chain
        for _ in range(number_of_delegations):
            prev_delegation = self.service.add_delegation(
                f"party{last_party_number}",
                f"party{last_party_number + 1}",
                [f"object1"],
                ["read"],
                time.time() + 1000000,
                "base",
                evidence=prev_delegation,
            )
            delegation_per_party[f"party{last_party_number+1}"] = prev_delegation
            last_party_number += 1

        additional_delegations = [0, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        times_taken = []

        initial_parties = [f"party{i}" for i in range(number_of_delegations)]
        additional_parties = [f"party{i}" for i in range(number_of_delegations, total_parties + 1)]
        links = [
            (initial_party, additional_party)
            for additional_party in additional_parties
            for initial_party in initial_parties
        ]

        for idx, num_add_delegations in enumerate(additional_delegations):
            start = additional_delegations[idx - 1] if idx > 0 else 0
            end = additional_delegations[idx]
            for source, target in links[start:end]:
                self.service.add_delegation(
                    source,
                    target,
                    [f"object1"],
                    ["read"],
                    time.time() + 1000000,
                    "base",
                    evidence=delegation_per_party[source],
                )

            # self.service.db.visualize_graph(f"delegation_graph_{num_add_delegations}.png")

            elapsed_avg = 0
            for _ in range(self.performance_test_count):
                start_time = time.time()
                success = self.service.has_access(
                    f"party{last_party_number}",
                    f"party0",
                    "object1",
                    "read",
                    "base",
                    evidence=delegation_per_party[f"party{last_party_number}"],
                )
                end_time = time.time()
                elapsed_time = end_time - start_time
                elapsed_avg += elapsed_time

                # If a single test takes longer than the performance time limit, fail the test
                assert (
                    elapsed_time < self.performance_time_limit
                ), f"Performance test failed, took {elapsed_time:.6f} seconds, expected less than {self.performance_time_limit:.6f} seconds."

            elapsed_avg /= self.performance_test_count

            assert success, "Performance test failed, as access was expected, but failed."

            times_taken.append(format(elapsed_avg, ".6f"))

        return dict(zip(additional_delegations, times_taken))
