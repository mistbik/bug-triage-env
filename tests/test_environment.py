"""
Tests for the Bug Triage & Patch Validation Environment.

Covers: scenarios, graders, environment step logic, and all tools.
"""

import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scenarios import SCENARIOS, get_scenario_by_id, get_scenarios_by_difficulty
from graders import (
    grade_identify_bug,
    grade_fix_bug,
    grade_full_triage,
    _extract_test_names,
    _exec_tests,
    TASKS,
)
from server.bug_triage_environment import BugTriageEnvironment
from models import BugTriageAction


# ============================================================
# Scenario tests
# ============================================================


class TestScenarios:
    def test_scenario_count(self):
        assert len(SCENARIOS) == 22

    def test_all_scenarios_have_required_keys(self):
        required = {
            "id", "difficulty", "file_name", "task_description",
            "buggy_code", "correct_code", "test_code",
            "bug_line", "bug_description",
        }
        for s in SCENARIOS:
            missing = required - set(s.keys())
            assert not missing, f"Scenario {s['id']} missing keys: {missing}"

    def test_difficulties(self):
        assert len(get_scenarios_by_difficulty("easy")) == 3
        assert len(get_scenarios_by_difficulty("medium")) == 3
        assert len(get_scenarios_by_difficulty("hard")) == 3

    def test_get_scenario_by_id(self):
        for s in SCENARIOS:
            found = get_scenario_by_id(s["id"])
            assert found is not None
            assert found["id"] == s["id"]

    def test_get_nonexistent_scenario(self):
        assert get_scenario_by_id("nonexistent") is None

    def test_buggy_code_fails_tests(self):
        """All buggy code should have at least one failing test."""
        for s in SCENARIOS:
            test_names = _extract_test_names(s["test_code"])
            assert len(test_names) > 0, f"Scenario {s['id']} has no tests"
            results = _exec_tests(s["buggy_code"], s["test_code"], test_names)
            failing = sum(1 for r in results.values() if not r["passed"])
            assert failing > 0, f"Scenario {s['id']}: buggy code passes all tests!"

    def test_correct_code_passes_tests(self):
        """All correct code should pass all tests."""
        for s in SCENARIOS:
            test_names = _extract_test_names(s["test_code"])
            results = _exec_tests(s["correct_code"], s["test_code"], test_names)
            passing = sum(1 for r in results.values() if r["passed"])
            assert passing == len(test_names), (
                f"Scenario {s['id']}: correct code fails "
                f"{len(test_names) - passing}/{len(test_names)} tests. "
                f"Failures: {[n for n, r in results.items() if not r['passed']]}"
            )


# ============================================================
# Grader tests
# ============================================================


class TestGraders:
    def test_extract_test_names(self):
        code = "def test_foo():\n    pass\ndef test_bar():\n    pass\n"
        names = _extract_test_names(code)
        assert names == ["test_foo", "test_bar"]

    def test_exec_tests_passing(self):
        code = "def add(a, b): return a + b"
        tests = "def test_add(): assert add(1, 2) == 3"
        results = _exec_tests(code, tests, ["test_add"])
        assert results["test_add"]["passed"]

    def test_exec_tests_failing(self):
        code = "def add(a, b): return a - b"
        tests = "def test_add(): assert add(1, 2) == 3"
        results = _exec_tests(code, tests, ["test_add"])
        assert not results["test_add"]["passed"]

    def test_grade_identify_bug_perfect(self):
        scenario = SCENARIOS[0]  # easy_off_by_one
        score = grade_identify_bug(
            scenario, scenario["bug_line"], scenario["bug_description"]
        )
        assert score >= 0.8, f"Perfect identification should score high, got {score}"

    def test_grade_identify_bug_wrong_line(self):
        scenario = SCENARIOS[0]
        score = grade_identify_bug(scenario, 999, "completely wrong")
        assert score < 0.4, f"Wrong identification should score low, got {score}"

    def test_grade_identify_bug_close_line(self):
        scenario = SCENARIOS[0]
        score = grade_identify_bug(
            scenario, scenario["bug_line"] + 1, scenario["bug_description"]
        )
        # Close line (±1) gets partial credit
        assert 0.2 < score < 1.0

    def test_grade_fix_bug_correct(self):
        for s in SCENARIOS:
            score = grade_fix_bug(s, s["correct_code"])
            assert score >= 0.9, (
                f"Scenario {s['id']}: correct fix should score >=0.9, got {score}"
            )

    def test_grade_fix_bug_buggy(self):
        for s in SCENARIOS:
            score = grade_fix_bug(s, s["buggy_code"])
            assert score < 0.9, (
                f"Scenario {s['id']}: buggy code should not score >=0.9, got {score}"
            )

    def test_grade_fix_bug_empty(self):
        score = grade_fix_bug(SCENARIOS[0], "")
        assert score == 0.0

    def test_grade_full_triage_perfect(self):
        s = SCENARIOS[0]
        score = grade_full_triage(
            s,
            agent_line=s["bug_line"],
            agent_description=s["bug_description"],
            patched_code=s["correct_code"],
            steps_taken=1,
            max_steps=12,
        )
        assert score >= 0.7, f"Perfect triage should score high, got {score}"

    def test_grade_full_triage_bad(self):
        s = SCENARIOS[0]
        score = grade_full_triage(
            s,
            agent_line=999,
            agent_description="no idea",
            patched_code="def broken(): pass",
            steps_taken=12,
            max_steps=12,
        )
        assert score < 0.2, f"Bad triage should score low, got {score}"

    def test_tasks_reference_valid_scenarios(self):
        scenario_ids = {s["id"] for s in SCENARIOS}
        for task in TASKS:
            for sid in task["scenarios"]:
                assert sid in scenario_ids, (
                    f"Task {task['id']} references unknown scenario: {sid}"
                )


# ============================================================
# Environment tests
# ============================================================


class TestEnvironment:
    def _make_env(self):
        env = BugTriageEnvironment()
        return env

    def test_reset(self):
        env = self._make_env()
        obs = env.reset(task_id="identify_bug")
        assert obs.scenario_id in [s["id"] for s in SCENARIOS]
        assert obs.steps_taken == 0
        assert obs.done is False

    def test_reset_specific_scenario(self):
        env = self._make_env()
        obs = env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        assert obs.scenario_id == "easy_off_by_one"

    def test_read_code_main(self):
        env = self._make_env()
        obs = env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        action = BugTriageAction(tool="read_code", parameters={"file": "utils.py"})
        obs = env.step(action)
        assert "def sum_list" in obs.last_action_result
        assert obs.steps_taken == 1

    def test_read_code_tests(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        action = BugTriageAction(tool="read_code", parameters={"file": "test"})
        obs = env.step(action)
        assert "test_sum_list" in obs.last_action_result

    def test_run_tests(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        action = BugTriageAction(tool="run_tests", parameters={})
        obs = env.step(action)
        assert "FAIL" in obs.last_action_result
        assert obs.tests_total > 0

    def test_identify_bug(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        action = BugTriageAction(
            tool="identify_bug",
            parameters={"line": 4, "description": "Off-by-one error in range"},
        )
        obs = env.step(action)
        assert obs.bug_identified is True
        assert "accepted" in obs.last_action_result.lower() or "recorded" in obs.last_action_result.lower()

    def test_submit_correct_patch(self):
        env = self._make_env()
        env.reset(task_id="fix_bug", scenario_id="easy_off_by_one")
        s = get_scenario_by_id("easy_off_by_one")
        action = BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": s["correct_code"]},
        )
        obs = env.step(action)
        assert obs.patch_submitted is True
        assert obs.patch_correct is True
        assert obs.done is True
        assert "ALL TESTS PASS" in obs.last_action_result

    def test_submit_wrong_patch(self):
        env = self._make_env()
        env.reset(task_id="fix_bug", scenario_id="easy_off_by_one")
        action = BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": "def sum_list(numbers): return -1"},
        )
        obs = env.step(action)
        assert obs.patch_submitted is True
        assert obs.patch_correct is False

    def test_unknown_tool(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        action = BugTriageAction(tool="hack_the_system", parameters={})
        obs = env.step(action)
        assert "Unknown tool" in obs.last_action_result

    def test_max_steps_ends_episode(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        # identify_bug task has max_steps=5
        for i in range(5):
            action = BugTriageAction(tool="read_code", parameters={"file": "main"})
            obs = env.step(action)
        assert obs.done is True
        assert "max steps" in obs.last_action_result.lower()

    def test_step_after_done(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        # Exhaust steps
        for _ in range(5):
            env.step(BugTriageAction(tool="read_code", parameters={}))
        obs = env.step(BugTriageAction(tool="read_code", parameters={}))
        assert "already done" in obs.last_action_result.lower()

    def test_state_property(self):
        env = self._make_env()
        env.reset(task_id="identify_bug")
        state = env.state
        assert state.episode_id
        assert state.step_count == 0

    def test_full_workflow(self):
        """Full agent workflow: read → run tests → identify → patch."""
        env = self._make_env()
        env.reset(task_id="full_triage", scenario_id="easy_off_by_one")
        s = get_scenario_by_id("easy_off_by_one")

        # Read code
        obs = env.step(BugTriageAction(tool="read_code", parameters={"file": "utils.py"}))
        assert "def sum_list" in obs.last_action_result

        # Run tests
        obs = env.step(BugTriageAction(tool="run_tests", parameters={}))
        assert "FAIL" in obs.last_action_result

        # Identify bug
        obs = env.step(BugTriageAction(
            tool="identify_bug",
            parameters={"line": 4, "description": "range starts at 1 instead of 0"},
        ))
        assert obs.bug_identified

        # Submit patch
        obs = env.step(BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": s["correct_code"]},
        ))
        assert obs.patch_correct
        assert obs.done

    def test_all_scenarios_playable(self):
        """Verify every scenario can be reset and played through."""
        env = self._make_env()
        for s in SCENARIOS:
            obs = env.reset(scenario_id=s["id"])
            assert obs.scenario_id == s["id"]
            # Read code
            obs = env.step(BugTriageAction(tool="read_code", parameters={}))
            assert obs.steps_taken == 1
            # Submit correct patch
            obs = env.step(BugTriageAction(
                tool="submit_patch",
                parameters={"patched_code": s["correct_code"]},
            ))
            assert obs.patch_correct, f"Scenario {s['id']}: correct patch rejected"

    # ---- New: state richness & multi-step enforcement tests ----

    def test_action_history_tracked(self):
        env = self._make_env()
        env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        env.step(BugTriageAction(tool="read_code", parameters={"file": "utils.py"}))
        obs = env.step(BugTriageAction(tool="run_tests", parameters={}))
        assert len(obs.action_history) == 2
        assert "read_code" in obs.action_history[0]
        assert "run_tests" in obs.action_history[1]

    def test_steps_remaining(self):
        env = self._make_env()
        obs = env.reset(task_id="identify_bug", scenario_id="easy_off_by_one")
        assert obs.steps_remaining == obs.max_steps
        obs = env.step(BugTriageAction(tool="read_code", parameters={}))
        assert obs.steps_remaining == obs.max_steps - 1

    def test_error_trace_populated(self):
        env = self._make_env()
        env.reset(task_id="fix_bug", scenario_id="easy_off_by_one")
        obs = env.step(BugTriageAction(tool="run_tests", parameters={}))
        # Buggy code should have failing tests → error_trace non-empty
        assert obs.error_trace != "", "Error trace should be populated for failing tests"

    def test_patch_attempts_tracked(self):
        env = self._make_env()
        env.reset(task_id="fix_bug", scenario_id="easy_off_by_one")
        obs = env.step(BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": "def sum_list(numbers): return -1"},
        ))
        assert obs.patch_attempts == 1
        obs = env.step(BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": "def sum_list(numbers): return -2"},
        ))
        assert obs.patch_attempts == 2

    def test_hard_task_requires_read_before_patch(self):
        """Full triage task should reject patch if agent hasn't read code."""
        env = self._make_env()
        env.reset(task_id="full_triage", scenario_id="easy_off_by_one")
        s = get_scenario_by_id("easy_off_by_one")
        obs = env.step(BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": s["correct_code"]},
        ))
        # Should be rejected — must read code first
        assert "must read" in obs.last_action_result.lower()
        assert obs.patch_correct is False

    def test_hard_task_requires_tests_before_patch(self):
        """Full triage task should reject patch if agent hasn't run tests."""
        env = self._make_env()
        env.reset(task_id="full_triage", scenario_id="easy_off_by_one")
        # Read code but don't run tests
        env.step(BugTriageAction(tool="read_code", parameters={"file": "utils.py"}))
        s = get_scenario_by_id("easy_off_by_one")
        obs = env.step(BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": s["correct_code"]},
        ))
        assert "must run" in obs.last_action_result.lower()
        assert obs.patch_correct is False

    def test_hard_task_allows_patch_after_prerequisites(self):
        """Full triage: patch accepted after reading code + running tests."""
        env = self._make_env()
        env.reset(task_id="full_triage", scenario_id="easy_off_by_one")
        env.step(BugTriageAction(tool="read_code", parameters={"file": "utils.py"}))
        env.step(BugTriageAction(tool="run_tests", parameters={}))
        s = get_scenario_by_id("easy_off_by_one")
        obs = env.step(BugTriageAction(
            tool="submit_patch",
            parameters={"patched_code": s["correct_code"]},
        ))
        assert obs.patch_correct is True
