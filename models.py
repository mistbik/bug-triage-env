"""
Data models for the Bug Triage & Patch Validation Environment.

An AI agent receives buggy code snippets with failing tests and must
diagnose the bug, identify the root cause, and produce a correct patch.
"""

from typing import Dict, List, Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class BugTriageAction(Action):
    """Action for the Bug Triage environment.

    The agent can perform one of several tool-call style actions:
    - read_code: Inspect a specific file/function in the codebase
    - run_tests: Execute the test suite to see which tests pass/fail
    - identify_bug: Declare the buggy line number and description
    - submit_patch: Submit a corrected version of the buggy code
    """

    tool: str = Field(
        ...,
        description=(
            "Tool to invoke. One of: read_code, run_tests, "
            "identify_bug, submit_patch"
        ),
    )
    parameters: Dict = Field(
        default_factory=dict,
        description=(
            "Parameters for the tool call. "
            "read_code: {file: str} | "
            "run_tests: {} | "
            "identify_bug: {line: int, description: str} | "
            "submit_patch: {patched_code: str}"
        ),
    )


class TestResult(Action):
    """A single test result."""

    name: str = Field(default="", description="Test function name")
    passed: bool = Field(default=False, description="Whether the test passed")
    error_message: str = Field(
        default="", description="Error message if the test failed"
    )


class BugTriageObservation(Observation):
    """Observation from the Bug Triage environment."""

    # Current scenario info
    scenario_id: str = Field(default="", description="ID of the current bug scenario")
    difficulty: str = Field(
        default="easy", description="Difficulty: easy, medium, or hard"
    )
    task_description: str = Field(
        default="", description="Natural language description of the task"
    )

    # Code context
    buggy_code: str = Field(default="", description="The buggy source code")
    file_name: str = Field(default="", description="Name of the buggy file")
    test_code: str = Field(default="", description="The test suite code")

    # Action results
    last_action_result: str = Field(
        default="", description="Result of the last action taken"
    )
    test_results: List[Dict] = Field(
        default_factory=list,
        description="List of test results from the last run_tests call",
    )
    tests_passing: int = Field(default=0, description="Number of tests currently passing")
    tests_total: int = Field(default=0, description="Total number of tests")

    # Episode state
    bug_identified: bool = Field(
        default=False, description="Whether the agent correctly identified the bug"
    )
    patch_submitted: bool = Field(
        default=False, description="Whether a patch has been submitted"
    )
    patch_correct: bool = Field(
        default=False, description="Whether the submitted patch is correct"
    )
    steps_taken: int = Field(default=0, description="Number of steps taken so far")
    max_steps: int = Field(default=10, description="Maximum steps allowed")
    steps_remaining: int = Field(default=10, description="Steps left before episode ends")

    # Accumulated context from actions
    files_read: List[str] = Field(
        default_factory=list, description="Files the agent has read so far"
    )
    action_history: List[str] = Field(
        default_factory=list,
        description="Chronological log of actions taken this episode (e.g. 'read_code(main)', 'run_tests')",
    )
    error_trace: str = Field(
        default="",
        description="Full error traceback from the last failing test or code execution",
    )
    patch_attempts: int = Field(
        default=0, description="Number of patches submitted so far (re-submissions cost steps)"
    )
