"""Bug Triage Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import BugTriageAction, BugTriageObservation


class BugTriageEnv(EnvClient[BugTriageAction, BugTriageObservation, State]):
    """
    Client for the Bug Triage & Patch Validation Environment.

    Example:
        >>> async with BugTriageEnv(base_url="http://localhost:8000") as client:
        ...     result = await client.reset()
        ...     print(result.observation.task_description)
        ...     result = await client.step(
        ...         BugTriageAction(tool="read_code", parameters={"file": "utils.py"})
        ...     )
        ...     print(result.observation.last_action_result)
    """

    def _step_payload(self, action: BugTriageAction) -> Dict:
        return {
            "tool": action.tool,
            "parameters": action.parameters,
        }

    def _parse_result(self, payload: Dict) -> StepResult[BugTriageObservation]:
        obs_data = payload.get("observation", {})
        observation = BugTriageObservation(
            scenario_id=obs_data.get("scenario_id", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            task_description=obs_data.get("task_description", ""),
            buggy_code=obs_data.get("buggy_code", ""),
            file_name=obs_data.get("file_name", ""),
            test_code=obs_data.get("test_code", ""),
            last_action_result=obs_data.get("last_action_result", ""),
            test_results=obs_data.get("test_results", []),
            tests_passing=obs_data.get("tests_passing", 0),
            tests_total=obs_data.get("tests_total", 0),
            bug_identified=obs_data.get("bug_identified", False),
            patch_submitted=obs_data.get("patch_submitted", False),
            patch_correct=obs_data.get("patch_correct", False),
            steps_taken=obs_data.get("steps_taken", 0),
            max_steps=obs_data.get("max_steps", 10),
            files_read=obs_data.get("files_read", []),
            done=payload.get("done", False),
            reward=payload.get("reward"),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
