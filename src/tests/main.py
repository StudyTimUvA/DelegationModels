import time
import inspect


class DelegationModelTests:
    def __init__(self, db_class, service_class, performance_time_limit=0.1):
        self.db_class = db_class
        self.service = service_class(self.db_class())
        self.performance_time_limit = performance_time_limit

        self.parties = [
            "owner1",
            "party1",
            "party2",
            "party3",
            "party4",
        ]

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
            self.service.db = self.db_class()
            self.service.db.add_parties(self.parties)

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
        check = "✓"
        cross = "✗"

        print(f"Test Results: {self.service.__class__.__name__}")

        longest_name = max(len(name) for name in results.keys())
        print(f"| {'Test Name':<{longest_name}} | Result |")
        print("-" * (longest_name + 13))
        for name, result in results.items():
            result_symbol = check if result else cross
            print(f"| {name:<{longest_name}} | {result_symbol}      |")

        print("")

    def test_single_delegation(self):
        """
        Test the delegation model with a single delegation.
        data_owner -> party1.
        """
        self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == True
        ), "party1 should have read access to object1 in DO->p1"

        # Test cases that should hold false
        assert (
            self.service.has_access("party1", "owner1", "object2", "read") == False
        ), "party1 should have access to object1 in DO->p1"
        assert (
            self.service.has_access("party1", "owner1", "object2", "write") == False
        ), "party1 should have access to object1 in DO->p1"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == False
        ), "party2 should not have access to object1 in DO->p1"

    def test_triple_delegation(self):
        """
        Test the delegation model with a triple delegation,
        data_owner -> party1 -> party2 -> party3.
        """
        self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party2",
            "party3",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == True
        ), "party1 should have read access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == True
        ), "party2 should have read access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read") == True
        ), "party3 should have read access to object1 in DO->p1->p2->p3"

        # Test cases that should hold false
        assert (
            self.service.has_access("party1", "owner1", "object1", "write") == False
        ), "party1 should not have write access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party2", "owner1", "object1", "write") == False
        ), "party2 should not have write access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party3", "owner1", "object1", "write") == False
        ), "party3 should not have write access to object1 in DO->p1->p2->p3"
        assert (
            self.service.has_access("party4", "owner1", "object1", "read") == False
        ), "party4 should have any access to object1 in DO->p1->p2->p3"

    def test_parallel_paths(self):
        """
        Test the delegation model with parallel paths (aka diveringing/converging paths),
        data_owner -> party1 -> party2 and data_owner -> party2.
        """
        self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "owner1",
            "party2",
            ["object1"],
            ["read", "write"],
            time.time() + 1000000,
        )

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == True
        ), "party1 should have read access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == True
        ), "party2 should have read access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object1", "write") == True
        ), "party2 should have write access to object1 in DO->p1->p2"

        # Test cases that should hold false
        assert (
            self.service.has_access("party1", "owner1", "object1", "write") == False
        ), "party1 should not have write access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read") == False
        ), "party3 should not have access to object1 in DO->p1->p2"

    def test_partial_delegations(self):
        """
        Test the delegation model with partial delegations,
        data_owner -> party1 -> party2, where party1->party2 contains a subset of the rights of party1.
        """
        self.service.add_delegation(
            "owner1",
            "party1",
            ["object1", "object2"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == True
        ), "party1 should have read access to object1 in DO->p1->p2"
        assert (
            self.service.has_access("party1", "owner1", "object2", "read") == True
        ), "party1 should have read access to object2 in DO->p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == True
        ), "party2 should have read access to object1 in DO->p1->p2"

        # Test cases that should hold false
        assert (
            self.service.has_access("party2", "owner1", "object2", "read") == False
        ), "party2 should not have read access to object2 in DO->p1->p2"

    def test_invalid_delegation(self):
        """
        Test the delegation model with an invalid delegation,
        party1 -> party2, where party1 has no access to object3.
        """
        delegation = self.service.add_delegation(
            "party1",
            "party2",
            ["object3"],
            ["read"],
            time.time() + 1000000,
        )

        # Test cases that should hold true
        assert not delegation, "Delegation should not be valid as party1 has no access to object3"

        # Test cases that should hold false
        assert (
            self.service.has_access("party1", "owner1", "object3", "read") == False
        ), "party1 should not have read access to object3 in p1->p2"
        assert (
            self.service.has_access("party2", "owner1", "object3", "read") == False
        ), "party2 should not have read access to object3 in p1->p2"

    def test_simple_revocation(self):
        """
        Test the delegation model with a simple revocation,
        data_owner -> party1, where party1 is revoked.
        """
        identifier = self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.revoke_delegation(identifier)

        # Test cases that should hold true
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == False
        ), "party1 should not have read access to object1 in DO->p1, when revoked"

    def test_triple_delegation_final_revoked(self):
        """
        Test the delegation model with a triple delegation,
        data_owner -> party1 -> party2 -> party3, where party3 is revoked.
        """
        self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        identifier = self.service.add_delegation(
            "party2",
            "party3",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.revoke_delegation(identifier)

        # Test cases
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == True
        ), "party1 should have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == True
        ), "party2 should have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read") == False
        ), "party3 should not have read access to object1 in DO->p1->p2->p3, when revoked"

    def test_triple_delegation_first_revoked_propagation(self):
        """
        Test the delegation model with a triple delegation,
        data_owner -> party1 -> party2 -> party3, where party1 is revoked.
        """
        identifier = self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party2",
            "party3",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.revoke_delegation(identifier)

        # Test cases
        assert (
            self.service.has_access("party1", "owner1", "object1", "read") == False
        ), "party1 should not have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == False
        ), "party2 should not have read access to object1 in DO->p1->p2->p3, when revoked"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read") == False
        ), "party3 should not have read access to object1 in DO->p1->p2->p3, when revoked"

    def test_changing_paths(self):
        """
        Test the delegation model with changing paths,
        data_owner -> party1 -> party2 -> party3, where party1 is revoked and data_owner->party2 is added.
        """
        identifier = self.service.add_delegation(
            "owner1",
            "party1",
            ["object1"],
            ["read"],
            time.time() + 100000,
        )
        self.service.add_delegation(
            "party1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.add_delegation(
            "party2",
            "party3",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )
        self.service.revoke_delegation(identifier)

        self.service.add_delegation(
            "owner1",
            "party2",
            ["object1"],
            ["read"],
            time.time() + 1000000,
        )

        # Test cases
        assert (
            self.service.has_access("party2", "owner1", "object1", "read") == True
        ), "party2 should have read access to object1 in DO->p2->p3"
        assert (
            self.service.has_access("party3", "owner1", "object1", "read") == True
        ), "party2 should have read access to object1 in DO->p2->p3, when revoked"

    def test_performance(self):
        """
        Test the performance of the delegation model with a growing number of parties and delegations.
        This task focusses on the performance of the has_access method.
        """

        numbers_of_delegations = [5, 10, 50, 100, 250, 500]
        last_party_number = 0

        self.service.db.add_parties(
            [f"party{i}" for i in range(0, max(numbers_of_delegations) + 1)]
        )

        for idx, number_of_delegations in enumerate(numbers_of_delegations):
            number_to_add = number_of_delegations - (
                numbers_of_delegations[idx - 1] if idx > 0 else 0
            )

            for _ in range(number_to_add):
                self.service.add_delegation(
                    f"party{last_party_number}",
                    f"party{last_party_number + 1}",
                    [f"object1"],
                    ["read"],
                    time.time() + 1000000,
                )
                last_party_number += 1

            start_time = time.time()
            success = self.service.has_access(
                f"party{last_party_number - 1}",
                f"party0",
                "object1",
                "read",
            )
            end_time = time.time()

            assert success, "Performance test failed, as access was expected, but failed."

            elapsed_time = end_time - start_time
            assert (
                elapsed_time < self.performance_time_limit
            ), f"Performance test failed, took {elapsed_time:.6f} seconds, expected less than {self.performance_time_limit:.6f} seconds."

            print(
                f"Performance test with {number_of_delegations} delegations took {elapsed_time:.6f} seconds."
            )
