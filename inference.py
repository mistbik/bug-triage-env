"""
Baseline inference script for the Bug Triage Environment.

Uses the OpenAI-compatible client to run an LLM agent against the environment.
Environment must be running (locally or on HF Spaces) before this script is
executed. The agent uses agentic tool-use: read code, run tests, identify bugs,
submit patches.

Mandatory environment variables:
    HF_TOKEN       HuggingFace / API key for LLM inference
    API_BASE_URL   LLM API endpoint (default: https://router.huggingface.co/v1)
    MODEL_NAME     Model identifier  (default: Qwen/Qwen2.5-72B-Instruct)

Optional:
    OPENAI_API_KEY Fallback if HF_TOKEN not set
    ENV_URL        Bug Triage server URL (default: http://localhost:7860)
"""

import json
import os
import re
import sys
from typing import Any

from openai import OpenAI
from openenv import GenericEnvClient

# ---------------------------------------------------------------------------
# Configuration — matches spec variable names exactly
# ---------------------------------------------------------------------------
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY", "")
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

# Client is created at module level; will fail at runtime if API_KEY is empty.
client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY or "__placeholder__")


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert software engineer performing bug triage on Python code.

You have access to an environment with the following tools:
- read_code:    Read the source file. Parameters: {"file": "main"} or {"file": "test"}
- run_tests:    Execute the test suite. Parameters: {}
- identify_bug: Report the bug location. Parameters: {"line": <int>, "description": "<str>"}
- submit_patch: Submit corrected code.  Parameters: {"patched_code": "<full file content>"}

WORKFLOW:
1. read_code {"file": "main"} — read the buggy source file
2. run_tests {}               — see which tests fail
3. identify_bug               — state the exact line and root cause
4. submit_patch               — provide the COMPLETE corrected file (all lines)

RULES:
- Respond with EXACTLY ONE tool call per turn, as a JSON object.
- Do NOT include any text outside the JSON.
- For submit_patch, provide the complete file — not just the changed line.

Format:
{"tool": "<tool_name>", "parameters": {<params>}}
"""

# ---------------------------------------------------------------------------
# Structured logging (mandatory stdout format)
# ---------------------------------------------------------------------------


def log_start(task: str, env_name: str, model: str) -> None:
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None) -> None:
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


# ---------------------------------------------------------------------------
# LLM interaction
# ---------------------------------------------------------------------------


def call_llm(messages: list[dict]) -> str:
    """Call the LLM and return the assistant's response text."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content.strip()


def parse_action(text: str) -> dict | None:
    """
    Extract the JSON action from LLM response.

    Uses bracket-counting so patched_code containing braces is handled
    correctly even when the model adds prose before/after the JSON.
    """
    text = text.strip()

    # Fast path: entire response is valid JSON
    try:
        action = json.loads(text)
        if "tool" in action:
            return action
    except json.JSONDecodeError:
        pass

    # Bracket-counting scan — handles nested dicts and code with braces
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
        if not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        action = json.loads(text[start : i + 1])
                        if "tool" in action:
                            return action
                    except json.JSONDecodeError:
                        pass
                    break
    return None


# ---------------------------------------------------------------------------
# Episode runner
# ---------------------------------------------------------------------------


def run_episode(task_id: str, scenario_id: str | None = None, env_name: str = "bug_triage") -> dict:
    """
    Run a single episode via WebSocket (stateful session).

    Each call opens a fresh WebSocket connection, so state is properly
    maintained across the reset → step → step → … loop.
    """
    reset_kwargs: dict[str, Any] = {"task_id": task_id}
    if scenario_id:
        reset_kwargs["scenario_id"] = scenario_id

    env = GenericEnvClient(base_url=ENV_URL).sync()
    step_rewards: list[float] = []
    steps_taken = 0
    prev_reward = 0.0
    final_reward = 0.0
    obs: dict = {}
    done = False

    log_start(task=task_id, env_name=env_name, model=MODEL_NAME)
    try:
        with env:
            # ── Reset ──────────────────────────────────────────────────────
            r = env.reset(**reset_kwargs)
            obs = r.observation
            done = r.done
            max_steps: int = obs.get("max_steps", 12)

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Task: {obs.get('task_description', task_id)}\n\n"
                        f"Difficulty: {obs.get('difficulty', 'unknown')}\n"
                        f"File: {obs.get('file_name', 'unknown')}\n"
                        f"Max steps: {max_steps}\n\n"
                        "Begin by reading the code."
                    ),
                },
            ]

            # ── Step loop ─────────────────────────────────────────────────
            for _ in range(max_steps):
                if done:
                    break

                llm_response = call_llm(messages)
                messages.append({"role": "assistant", "content": llm_response})

                action = parse_action(llm_response)
                if action is None:
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Invalid response. Reply with ONLY a JSON object:\n"
                                '{"tool": "<tool_name>", "parameters": {<params>}}'
                            ),
                        }
                    )
                    continue

                # Execute — step() accepts a plain dict for GenericEnvClient
                result = env.step(action)
                obs = result.observation
                current_reward = result.reward or 0.0
                done = result.done

                step_delta = current_reward - prev_reward
                prev_reward = current_reward
                steps_taken += 1
                step_rewards.append(step_delta)

                error_msg = obs.get("last_action_error") or None
                log_step(
                    step=steps_taken,
                    action=json.dumps(action, separators=(",", ":")),
                    reward=step_delta,
                    done=done,
                    error=error_msg,
                )

                tests_info = ""
                if obs.get("tests_passing") is not None:
                    tests_info = (
                        f"\nTests: {obs['tests_passing']}/{obs.get('tests_total', '?')} passing"
                    )
                error_info = ""
                if obs.get("error_trace"):
                    error_info = f"\nError trace:\n{obs['error_trace'][:300]}"

                feedback = (
                    f"Action result:\n{obs.get('last_action_result', '')}"
                    f"{tests_info}{error_info}\n"
                    f"Step {steps_taken}/{max_steps} | "
                    f"steps_remaining={obs.get('steps_remaining', '?')} | "
                    f"Reward so far: {current_reward:.3f}"
                )

                messages.append({"role": "user", "content": feedback})

            final_reward = prev_reward
    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)

    success = final_reward >= 0.5
    log_end(success=success, steps=steps_taken, score=final_reward, rewards=step_rewards)
    return {"observation": obs, "reward": final_reward, "done": done, "step_rewards": step_rewards}


# ---------------------------------------------------------------------------
# Main: run all tasks across all scenarios
# ---------------------------------------------------------------------------

TASKS = [
    {"id": "identify_bug", "name": "Bug Identification"},
    {"id": "fix_bug", "name": "Bug Fix"},
    {"id": "full_triage", "name": "Full Bug Triage"},
]

# One representative scenario per difficulty tier.
# Running all 27 (3×9) episodes would exceed the 20-minute runtime budget on
# 2 vCPU / 8 GB hardware.  Judges see scores for easy → medium → hard.
SCENARIO_IDS = [
    "easy_off_by_one",
    "medium_boundary_check",
    "hard_algorithm_bug",
]


def main():
    """Run baseline inference across all tasks and scenarios."""
    if not API_KEY:
        print("ERROR: Set HF_TOKEN (or OPENAI_API_KEY) before running.", file=sys.stderr)
        sys.exit(1)

    print(f"API: {API_BASE_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Environment: {ENV_URL}")
    print(f"Scenarios: {', '.join(SCENARIO_IDS)}")
    print("=" * 60)

    all_results = {}

    for task in TASKS:
        task_id = task["id"]
        task_name = task["name"]
        print(f"\n{'='*60}")
        print(f"Task: {task_name} ({task_id})")
        print(f"{'='*60}")

        scenario_results = []
        for scenario_id in SCENARIO_IDS:
            difficulty = scenario_id.split("_")[0]  # easy / medium / hard
            print(f"\n  [{difficulty.upper()}] {scenario_id}")
            try:
                result = run_episode(task_id, scenario_id)
                reward = result.get("reward", 0.0)
                scenario_results.append({"scenario_id": scenario_id, "difficulty": difficulty, "reward": reward})
                print(f"  → reward={reward:.3f}")
            except Exception as exc:
                print(f"  ERROR: {exc}")
                scenario_results.append({"scenario_id": scenario_id, "difficulty": difficulty, "reward": 0.0})

        rewards = [s["reward"] for s in scenario_results]
        avg_reward = sum(rewards) / len(rewards) if rewards else 0.0
        all_results[task_id] = {
            "task_name": task_name,
            "scenarios": scenario_results,
            "average": avg_reward,
        }
        print(f"\n  ─── {task_name} average: {avg_reward:.3f} ───")

    # ── Summary ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SCORE SUMMARY (difficulty curve)")
    print(f"{'='*60}")
    print(f"  {'Task':<22} {'Easy':>6}  {'Medium':>8}  {'Hard':>6}  {'Avg':>6}")
    print(f"  {'-'*22} {'-'*6}  {'-'*8}  {'-'*6}  {'-'*6}")

    overall_rewards: list[float] = []
    for t_id, data in all_results.items():
        by_diff: dict[str, float] = {}
        for s in data["scenarios"]:
            by_diff[s["difficulty"]] = s["reward"]
            overall_rewards.append(s["reward"])
        easy   = f"{by_diff.get('easy',   0.0):.3f}"
        medium = f"{by_diff.get('medium', 0.0):.3f}"
        hard   = f"{by_diff.get('hard',   0.0):.3f}"
        avg    = f"{data['average']:.3f}"
        print(f"  {data['task_name']:<22} {easy:>6}  {medium:>8}  {hard:>6}  {avg:>6}")

    overall_avg = sum(overall_rewards) / len(overall_rewards) if overall_rewards else 0.0
    print(f"\n  Overall: {overall_avg:.3f}")
    print()
    print("  Expected: easy > medium > hard (meaningful difficulty curve)")

    # ── Save results ───────────────────────────────────────────────────
    with open("inference_results.json", "w") as f:
        json.dump(
            {
                "api_base_url": API_BASE_URL,
                "model": MODEL_NAME,
                "scenarios": SCENARIO_IDS,
                "overall_average": overall_avg,
                "tasks": all_results,
            },
            f,
            indent=2,
        )
    print("\nResults saved to inference_results.json")


if __name__ == "__main__":
    main()
