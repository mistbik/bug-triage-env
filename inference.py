"""
Baseline inference script for the Bug Triage Environment.

Runs a real LLM agent (Google Gemini via OpenAI-compatible API) against the
environment across 3 tasks × 3 scenarios and writes inference_results.json.

To run with Google AI Studio key:
    export HF_TOKEN="your-google-ai-studio-key"
    export API_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
    export MODEL_NAME="gemini-2.0-flash"
    export ENV_URL="http://localhost:7860"
    python inference.py

Mandatory environment variables:
    HF_TOKEN       Google AI Studio / HuggingFace API key (no default — must be set)
    API_BASE_URL   LLM API endpoint (default: https://generativelanguage.googleapis.com/v1beta/openai/)
    MODEL_NAME     Model identifier  (default: gemini-2.0-flash)

Optional:
    LOCAL_IMAGE_NAME Name of local Docker image (if using from_docker_image())
    ENV_URL          Bug Triage server URL (default: http://localhost:7860)

Stdout format (mandatory):
    [START] task=<task_name> env=bug_triage model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<0.000> rewards=<r1,r2,...>
"""

import json
import os
import sys
from typing import List, Optional

from openai import OpenAI
from openenv import GenericEnvClient

# ---------------------------------------------------------------------------
# Configuration — only API_BASE_URL and MODEL_NAME have defaults
# ---------------------------------------------------------------------------
API_BASE_URL     = os.environ.get("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME       = os.environ.get("MODEL_NAME",   "gemini-2.0-flash")
HF_TOKEN         = os.environ.get("HF_TOKEN")           # no default — must be set
LOCAL_IMAGE_NAME = os.environ.get("LOCAL_IMAGE_NAME")   # used if running from docker image
ENV_URL          = os.environ.get("ENV_URL",      "http://localhost:7860")
BENCHMARK        = "bug_triage"

# All LLM calls use the OpenAI client configured via these variables
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "__placeholder__")

# ---------------------------------------------------------------------------
# Mandatory structured logging
# ---------------------------------------------------------------------------

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val  = error if error else "null"
    done_val   = str(done).lower()
    action_str = action.replace("\n", " ")[:120]
    print(
        f"[STEP] step={step} action={action_str} reward={reward:.2f} "
        f"done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )

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
# LLM + action parsing
# ---------------------------------------------------------------------------

def call_llm(messages: list) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content.strip()


def parse_action(text: str) -> Optional[dict]:
    text = text.strip()
    # Strip markdown code fences if Gemini adds them
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        text = text.strip()

    try:
        action = json.loads(text)
        if "tool" in action:
            return action
    except json.JSONDecodeError:
        pass

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
                        action = json.loads(text[start: i + 1])
                        if "tool" in action:
                            return action
                    except json.JSONDecodeError:
                        pass
                    break
    return None

# ---------------------------------------------------------------------------
# Single episode — emits [START] [STEP]... [END]
# ---------------------------------------------------------------------------

def run_episode(task_id: str, scenario_id: Optional[str] = None) -> float:
    """Run one episode and return final score in [0, 1]. Emits structured logs."""
    reset_kwargs: dict = {"task_id": task_id}
    if scenario_id:
        reset_kwargs["scenario_id"] = scenario_id

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    reward = 0.0

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    env = GenericEnvClient(base_url=ENV_URL).sync()
    try:
        with env:
            r          = env.reset(**reset_kwargs)
            obs: dict  = r.observation
            done: bool = r.done
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

            for step_num in range(1, max_steps + 1):
                if done:
                    break

                try:
                    llm_response = call_llm(messages)
                except Exception as e:
                    log_step(step=step_num, action="LLM_ERROR", reward=0.0,
                             done=False, error=str(e)[:120])
                    break

                messages.append({"role": "assistant", "content": llm_response})

                action = parse_action(llm_response)
                if action is None:
                    log_step(step=step_num, action="INVALID_JSON", reward=0.0,
                             done=False, error="Could not parse action")
                    messages.append({
                        "role": "user",
                        "content": (
                            "Invalid response. Reply with ONLY a JSON object:\n"
                            '{"tool": "<tool_name>", "parameters": {<params>}}'
                        ),
                    })
                    continue

                result = env.step(action)
                obs    = result.observation
                reward = result.reward or 0.0
                done   = result.done
                error  = obs.get("error_trace") or None

                rewards.append(reward)
                steps_taken = step_num

                action_label = (
                    f"{action.get('tool')}"
                    f"({json.dumps(action.get('parameters', {}))})"
                )
                log_step(step=step_num, action=action_label, reward=reward,
                         done=done, error=error if error else None)

                feedback = (
                    f"Action result:\n{obs.get('last_action_result', '')}\n"
                    f"Tests: {obs.get('tests_passing', 0)}/{obs.get('tests_total', 0)} passing\n"
                    f"Steps remaining: {obs.get('steps_remaining', '?')}"
                )
                if error:
                    feedback += f"\nError trace:\n{error[:300]}"
                if done:
                    feedback += "\n\n[Episode complete]"

                messages.append({"role": "user", "content": feedback})

                if done:
                    break

            score   = float(max(0.0, min(reward, 1.0)))
            success = score > 0.5

    except Exception as exc:
        log_step(step=steps_taken + 1, action="ERROR", reward=0.0,
                 done=True, error=str(exc)[:120])

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score

# ---------------------------------------------------------------------------
# Main — 3 tasks × 3 scenarios, well within 20 min budget
# ---------------------------------------------------------------------------

TASKS = [
    {"id": "identify_bug", "name": "Bug Identification"},
    {"id": "fix_bug",       "name": "Bug Fix"},
    {"id": "full_triage",   "name": "Full Bug Triage"},
]

# One scenario per difficulty tier — 9 episodes total
SCENARIO_IDS = [
    "easy_off_by_one",
    "medium_boundary_check",
    "hard_algorithm_bug",
]


def main():
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN environment variable must be set before running.", file=sys.stderr)
        sys.exit(1)

    print(f"API:         {API_BASE_URL}", flush=True)
    print(f"Model:       {MODEL_NAME}", flush=True)
    print(f"Environment: {ENV_URL}", flush=True)
    print(f"Scenarios:   {', '.join(SCENARIO_IDS)}", flush=True)
    print("=" * 60, flush=True)

    all_results = {}

    for task in TASKS:
        task_id          = task["id"]
        task_name        = task["name"]
        scenario_results = []

        for scenario_id in SCENARIO_IDS:
            difficulty = scenario_id.split("_")[0]
            try:
                score = run_episode(task_id, scenario_id)
                scenario_results.append({
                    "scenario_id": scenario_id,
                    "difficulty":  difficulty,
                    "score":       round(score, 4),
                })
            except Exception as exc:
                print(f"[ERROR] {task_id}/{scenario_id}: {exc}", file=sys.stderr)
                scenario_results.append({
                    "scenario_id": scenario_id,
                    "difficulty":  difficulty,
                    "score":       0.0,
                })

        avg = sum(s["score"] for s in scenario_results) / len(scenario_results)
        all_results[task_id] = {
            "task_name": task_name,
            "scenarios": scenario_results,
            "average":   round(avg, 4),
        }

    overall_avg = sum(
        s["score"]
        for data in all_results.values()
        for s in data["scenarios"]
    ) / (len(TASKS) * len(SCENARIO_IDS))

    # Print summary
    print("\n" + "=" * 60, flush=True)
    print("INFERENCE RESULTS SUMMARY", flush=True)
    print("=" * 60, flush=True)
    print(f"  {'Task':<22} {'Easy':>6}  {'Medium':>8}  {'Hard':>6}  {'Avg':>6}", flush=True)
    print(f"  {'-'*22} {'-'*6}  {'-'*8}  {'-'*6}  {'-'*6}", flush=True)
    for t_id, data in all_results.items():
        by_diff = {s["difficulty"]: s["score"] for s in data["scenarios"]}
        print(
            f"  {data['task_name']:<22} "
            f"{by_diff.get('easy', 0):.3f}  "
            f"{by_diff.get('medium', 0):>8.3f}  "
            f"{by_diff.get('hard', 0):>6.3f}  "
            f"{data['average']:>6.3f}",
            flush=True,
        )
    print(f"\n  Overall average: {overall_avg:.3f}", flush=True)

    # Save results
    with open("inference_results.json", "w") as f:
        json.dump({
            "api_base_url":    API_BASE_URL,
            "model":           MODEL_NAME,
            "scenarios":       SCENARIO_IDS,
            "overall_average": round(overall_avg, 4),
            "tasks":           all_results,
        }, f, indent=2)

    print("\nResults saved to inference_results.json", flush=True)


if __name__ == "__main__":
    main()
