"""
Bug Triage Environment Implementation.

An AI agent receives buggy code with failing tests and must diagnose
the bug, identify the root cause, and produce a correct patch.
"""

import os
import sys
import random
from uuid import uuid4

# Ensure parent directory is on sys.path for flat imports
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import BugTriageAction, BugTriageObservation
    from ..scenarios import SCENARIOS, get_scenario_by_id, get_scenarios_by_difficulty
    from ..graders import (
        grade_identify_bug,
        grade_fix_bug,
        grade_full_triage,
        _extract_test_names,
        _exec_tests,
        TASKS,
    )
except (ImportError, ModuleNotFoundError):
    from models import BugTriageAction, BugTriageObservation
    from scenarios import SCENARIOS, get_scenario_by_id, get_scenarios_by_difficulty
    from graders import (
        grade_identify_bug,
        grade_fix_bug,
        grade_full_triage,
        _extract_test_names,
        _exec_tests,
        TASKS,
    )


class BugTriageEnvironment(Environment):
    """
    Bug Triage & Patch Validation Environment.

    The agent is given buggy code + failing tests and must use tools to
    investigate, identify, and fix the bug.

    Actions (tools):
    - read_code: View the buggy source file
    - run_tests: Execute the test suite against the current code
    - identify_bug: Declare the buggy line and describe the root cause
    - submit_patch: Submit corrected code and see if tests pass

    The environment supports three task difficulties (easy/medium/hard),
    each with multiple scenarios and a deterministic grader.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._scenario = None
        self._task = None
        self._done = False
        self._cumulative_reward = 0.0
        self._files_read = []
        self._tests_run = False
        self._bug_identified = False
        self._identified_line = -1
        self._identified_desc = ""
        self._patch_submitted = False
        self._patch_code = ""
        self._patch_correct = False
        self._last_action_result = ""
        self._last_test_results = []
        self._tests_passing = 0
        self._tests_total = 0
        self._max_steps = 10
        self._action_history = []
        self._error_trace = ""
        self._patch_attempts = 0

    def reset(self, task_id: str = None, scenario_id: str = None) -> BugTriageObservation:
        """Reset the environment with a new scenario.

        Args:
            task_id: Optional task ID to set difficulty context.
            scenario_id: Optional specific scenario ID. If not given, picks randomly.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._done = False
        self._cumulative_reward = 0.0
        self._files_read = []
        self._tests_run = False
        self._bug_identified = False
        self._identified_line = -1
        self._identified_desc = ""
        self._patch_submitted = False
        self._patch_code = ""
        self._patch_correct = False
        self._last_action_result = ""
        self._last_test_results = []
        self._tests_passing = 0
        self._tests_total = 0
        self._action_history = []
        self._error_trace = ""
        self._patch_attempts = 0

        # Select task
        if task_id:
            task = next((t for t in TASKS if t["id"] == task_id), None)
            if task:
                self._task = task
                self._max_steps = task["max_steps"]
                valid_scenarios = [
                    get_scenario_by_id(sid) for sid in task["scenarios"]
                ]
                valid_scenarios = [s for s in valid_scenarios if s is not None]
                if scenario_id:
                    self._scenario = get_scenario_by_id(scenario_id)
                else:
                    self._scenario = random.choice(valid_scenarios)
            else:
                self._scenario = random.choice(SCENARIOS)
                self._max_steps = 10
        elif scenario_id:
            self._scenario = get_scenario_by_id(scenario_id)
            self._max_steps = 10
        else:
            self._scenario = random.choice(SCENARIOS)
            self._max_steps = 10

        if self._scenario is None:
            self._scenario = SCENARIOS[0]

        # Count total tests
        test_names = _extract_test_names(self._scenario["test_code"])
        self._tests_total = len(test_names)

        return self._make_observation(
            last_action_result="Environment reset. You are given buggy code and failing tests. "
            "Use read_code, run_tests, identify_bug, and submit_patch to fix the issue."
        )

    def step(self, action: BugTriageAction) -> BugTriageObservation:
        """Execute one step."""
        if self._scenario is None:
            # Auto-reset with a random scenario if step called before reset
            self.reset()

        if self._done:
            return self._make_observation(
                last_action_result="Episode is already done. Call reset() to start a new one."
            )

        self._state.step_count += 1
        reward = 0.0

        tool = action.tool.lower().strip()
        params = action.parameters or {}

        # Log action to history
        param_summary = ", ".join(f"{k}={repr(v)[:40]}" for k, v in params.items())
        self._action_history.append(f"{tool}({param_summary})")

        if tool == "read_code":
            reward, result = self._handle_read_code(params)
        elif tool == "run_tests":
            reward, result = self._handle_run_tests(params)
        elif tool == "identify_bug":
            reward, result = self._handle_identify_bug(params)
        elif tool == "submit_patch":
            reward, result = self._handle_submit_patch(params)
        else:
            reward = -0.05
            result = (
                f"Unknown tool '{tool}'. Available tools: "
                "read_code, run_tests, identify_bug, submit_patch"
            )

        self._cumulative_reward += reward

        # Check if episode is done
        if self._state.step_count >= self._max_steps:
            self._done = True
            result += "\n[Episode ended: max steps reached.]"

        return self._make_observation(last_action_result=result, reward=reward)

    def _handle_read_code(self, params):
        """Handle the read_code tool."""
        file_name = params.get("file", self._scenario["file_name"])
        # Always record that the agent attempted to read code, regardless of
        # which filename was requested.  This lets the prereq guard work even
        # when the agent uses a generic alias like "main" or "source".
        if "code" not in self._files_read and self._scenario["file_name"] not in self._files_read:
            self._files_read.append("code")  # generic marker

        if file_name == self._scenario["file_name"] or file_name in ("", "main", "source", "code"):
            code = self._scenario["buggy_code"]
            if self._scenario["file_name"] not in self._files_read:
                self._files_read.append(self._scenario["file_name"])
            return 0.01, f"--- {self._scenario['file_name']} ---\n{code}"
        elif file_name == "tests" or "test" in file_name.lower():
            code = self._scenario["test_code"]
            if "tests" not in self._files_read:
                self._files_read.append("tests")
            return 0.01, f"--- test_{self._scenario['file_name']} ---\n{code}"
        else:
            # File not found by exact name — list available files as hints.
            return 0.0, f"File '{file_name}' not found. Available: {self._scenario['file_name']}, tests"

    def _handle_run_tests(self, params):
        """Handle the run_tests tool — execute tests against buggy code."""
        self._tests_run = True
        test_code = self._scenario["test_code"]
        test_names = _extract_test_names(test_code)

        # Run against the current code (buggy unless patched)
        code = self._patch_code if self._patch_submitted else self._scenario["buggy_code"]
        results = _exec_tests(code, test_code, test_names)

        self._last_test_results = []
        passing = 0
        output_lines = []
        error_traces = []
        for name in test_names:
            r = results.get(name, {"passed": False, "error": "Not run"})
            self._last_test_results.append({
                "name": name,
                "passed": r["passed"],
                "error_message": r.get("error", ""),
            })
            status = "PASS" if r["passed"] else "FAIL"
            passing += int(r["passed"])
            line = f"  {status}: {name}"
            if not r["passed"] and r.get("error"):
                line += f"  ({r['error']})"
                error_traces.append(f"[{name}] {r['error']}")
            output_lines.append(line)

        self._tests_passing = passing
        self._tests_total = len(test_names)

        # Capture error trace for state richness
        self._error_trace = "\n".join(error_traces) if error_traces else ""

        header = f"Test Results: {passing}/{len(test_names)} passing\n"
        return 0.02, header + "\n".join(output_lines)

    def _handle_identify_bug(self, params):
        """Handle the identify_bug tool."""
        line = params.get("line", -1)
        description = params.get("description", "")

        if not isinstance(line, int) or line < 1:
            return -0.02, "Invalid parameters. Provide {line: int, description: str}."

        self._bug_identified = True
        self._identified_line = line
        self._identified_desc = description

        id_score = grade_identify_bug(self._scenario, line, description)
        task_id = self._task["id"] if self._task else None

        if task_id == "identify_bug":
            # Terminal action — return the full grader score (0.0–1.0) and end episode.
            self._done = True
            reward = id_score
            if id_score >= 0.6:
                msg = (
                    f"Bug identification accepted! Score: {id_score:.2f}. "
                    f"Line {line}: {description}\n[Episode complete]"
                )
            else:
                msg = (
                    f"Bug identification recorded. Score: {id_score:.2f}. "
                    f"Line {line}: {description}\n[Episode complete]"
                )
        else:
            # Intermediate step for fix_bug / full_triage — small partial reward.
            reward = 0.1 * id_score
            if id_score >= 0.6:
                msg = f"Bug identification accepted (confidence: {id_score:.2f}). Line {line}: {description}"
            else:
                msg = f"Bug identification recorded (confidence: {id_score:.2f}). Line {line}: {description}"

        return reward, msg

    def _handle_submit_patch(self, params):
        """Handle the submit_patch tool."""
        patched_code = params.get("patched_code", "")

        if not patched_code.strip():
            return -0.05, "Empty patch submitted. Provide {patched_code: str}."

        # For hard scenarios (full_triage), enforce multi-step reasoning:
        # agent must have read code AND run tests before submitting
        task_id = self._task["id"] if self._task else None
        if task_id == "full_triage":
            if not self._files_read:
                return -0.03, (
                    "You must read the code before submitting a patch. "
                    "Use read_code first to understand the bug."
                )
            if not self._tests_run:
                return -0.03, (
                    "You must run the tests before submitting a patch. "
                    "Use run_tests first to see which tests fail."
                )

        self._patch_attempts += 1
        self._patch_submitted = True
        self._patch_code = patched_code

        # Run tests against patched code
        test_code = self._scenario["test_code"]
        test_names = _extract_test_names(test_code)
        results = _exec_tests(patched_code, test_code, test_names)

        passing = sum(1 for r in results.values() if r["passed"])
        total = len(test_names)
        self._tests_passing = passing
        self._tests_total = total

        self._last_test_results = []
        output_lines = []
        error_traces = []
        for name in test_names:
            r = results.get(name, {"passed": False, "error": "Not run"})
            self._last_test_results.append({
                "name": name,
                "passed": r["passed"],
                "error_message": r.get("error", ""),
            })
            status = "PASS" if r["passed"] else "FAIL"
            line = f"  {status}: {name}"
            if not r["passed"] and r.get("error"):
                line += f"  ({r['error']})"
                error_traces.append(f"[{name}] {r['error']}")
            output_lines.append(line)

        # Capture error trace from patch attempt
        self._error_trace = "\n".join(error_traces) if error_traces else ""

        if passing == total:
            self._patch_correct = True
            self._done = True
            # Terminal reward — use appropriate grader (0.85–1.0 range)
            task_id = self._task["id"] if self._task else None
            if task_id == "fix_bug":
                reward = grade_fix_bug(self._scenario, patched_code)
            elif task_id == "full_triage":
                reward = grade_full_triage(
                    self._scenario,
                    self._identified_line,
                    self._identified_desc,
                    patched_code,
                    self._state.step_count,
                    self._max_steps,
                )
            else:
                reward = grade_fix_bug(self._scenario, patched_code)
            header = f"ALL TESTS PASS ({passing}/{total})! Patch accepted. Score: {reward:.3f}\n"
        else:
            # Partial pass — use grader for proper partial-credit signal.
            # The grader already handles proportional scoring (0.0–0.85) so
            # agents get meaningful reward from the first attempt onward.
            task_id = self._task["id"] if self._task else None
            if task_id == "fix_bug":
                reward = grade_fix_bug(self._scenario, patched_code)
            elif task_id == "full_triage":
                reward = grade_full_triage(
                    self._scenario,
                    self._identified_line,
                    self._identified_desc,
                    patched_code,
                    self._state.step_count,
                    self._max_steps,
                )
                reward = max(reward, 0.0)  # floor — prereq penalties already applied above
            else:
                # Fallback: proportional with escalating penalty for retries
                base_reward = 0.1 * (passing / total) if total > 0 else 0.0
                penalty = 0.02 * (self._patch_attempts - 1)
                reward = max(base_reward - penalty, -0.05)
            header = (
                f"Patch result: {passing}/{total} tests passing "
                f"(attempt #{self._patch_attempts}). Score: {reward:.3f}\n"
            )

        return reward, header + "\n".join(output_lines)

    def _make_observation(self, last_action_result="", reward=None):
        """Build the current observation."""
        obs = BugTriageObservation(
            scenario_id=self._scenario["id"] if self._scenario else "",
            difficulty=self._scenario["difficulty"] if self._scenario else "easy",
            task_description=self._scenario["task_description"] if self._scenario else "",
            buggy_code=self._scenario["buggy_code"] if self._scenario else "",
            file_name=self._scenario["file_name"] if self._scenario else "",
            test_code=self._scenario["test_code"] if self._scenario else "",
            last_action_result=last_action_result,
            test_results=self._last_test_results,
            tests_passing=self._tests_passing,
            tests_total=self._tests_total,
            bug_identified=self._bug_identified,
            patch_submitted=self._patch_submitted,
            patch_correct=self._patch_correct,
            steps_taken=self._state.step_count,
            max_steps=self._max_steps,
            steps_remaining=max(0, self._max_steps - self._state.step_count),
            files_read=list(self._files_read),
            action_history=list(self._action_history),
            error_trace=self._error_trace,
            patch_attempts=self._patch_attempts,
            done=self._done,
            reward=reward if reward is not None else self._cumulative_reward,
        )
        return obs

    @property
    def state(self) -> State:
        return self._state
