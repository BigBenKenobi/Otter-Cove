from __future__ import annotations

import unittest

from core.demo_states import DemoScenario, DemoStatus, DeterministicDemoAdapter


class DeterministicDemoAdapterTests(unittest.TestCase):
    def test_all_required_fixture_scenarios_are_explicit(self) -> None:
        self.assertEqual(
            {scenario.value for scenario in DemoScenario},
            {"success", "empty", "loading", "failure", "cancellation"},
        )

    def test_terminal_scenarios_are_deterministic(self) -> None:
        expected = {
            DemoScenario.SUCCESS: DemoStatus.SUCCESS,
            DemoScenario.EMPTY: DemoStatus.EMPTY,
            DemoScenario.FAILURE: DemoStatus.FAILURE,
            DemoScenario.CANCELLATION: DemoStatus.CANCELLED,
        }
        for scenario, status in expected.items():
            with self.subTest(scenario=scenario):
                adapter = DeterministicDemoAdapter()
                request = adapter.begin(scenario)
                outcome = adapter.complete(request.request_id)
                self.assertEqual(outcome.status, status)
                self.assertFalse(outcome.stale)
                self.assertIsNone(adapter.active_request_id)

    def test_loading_fixture_stays_pending_until_cancelled(self) -> None:
        adapter = DeterministicDemoAdapter()
        request = adapter.begin(DemoScenario.LOADING)
        first = adapter.complete(request.request_id)
        second = adapter.complete(request.request_id)
        self.assertEqual(first.status, DemoStatus.LOADING)
        self.assertEqual(second.status, DemoStatus.LOADING)
        self.assertEqual(adapter.active_request_id, request.request_id)
        cancelled = adapter.cancel(request.request_id)
        self.assertEqual(cancelled.status, DemoStatus.CANCELLED)
        self.assertIsNone(adapter.active_request_id)

    def test_new_request_makes_old_completion_stale(self) -> None:
        adapter = DeterministicDemoAdapter()
        old = adapter.begin(DemoScenario.SUCCESS)
        current = adapter.begin(DemoScenario.FAILURE)
        stale = adapter.complete(old.request_id)
        self.assertEqual(stale.status, DemoStatus.STALE)
        self.assertTrue(stale.stale)
        current_result = adapter.complete(current.request_id)
        self.assertEqual(current_result.status, DemoStatus.FAILURE)

    def test_retry_allocates_a_fresh_request_id(self) -> None:
        adapter = DeterministicDemoAdapter()
        first = adapter.begin(DemoScenario.FAILURE)
        second = adapter.retry()
        self.assertNotEqual(first.request_id, second.request_id)
        self.assertEqual(second.scenario, DemoScenario.FAILURE)
        self.assertEqual(adapter.complete(first.request_id).status, DemoStatus.STALE)
        self.assertEqual(adapter.complete(second.request_id).status, DemoStatus.FAILURE)

    def test_duplicate_completion_cannot_apply_twice(self) -> None:
        adapter = DeterministicDemoAdapter()
        request = adapter.begin(DemoScenario.SUCCESS)
        self.assertEqual(adapter.complete(request.request_id).status, DemoStatus.SUCCESS)
        self.assertEqual(adapter.complete(request.request_id).status, DemoStatus.STALE)


if __name__ == "__main__":
    unittest.main()
