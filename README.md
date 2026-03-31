---
title: Bug Triage Environment
emoji: 🐛
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Bug Triage & Patch Validation — OpenEnv Environment

An [OpenEnv](https://huggingface.co/openenv)-compliant environment where an AI agent receives **buggy Python code** with failing unit tests and must **diagnose the root cause**, **identify the faulty line**, and **produce a correct patch**. Grading is fully deterministic — patches are scored by actually executing the test suite.

## Why Bug Triage?

| Property | Detail |
|---|---|
| **Real-world relevance** | Debugging is a core engineering skill; models that can triage bugs save developer hours |
| **Deterministic grading** | Tests either pass or they don't — no subjective rubrics |
| **Genuine difficulty** | Requires reading code, understanding intent, reasoning about edge cases, and producing correct patches |
| **Scalable** | Easy to add more scenarios without changing graders |

## Tasks

| # | Task ID | Name | Difficulty | Max Steps | Description |
|---|---------|------|------------|-----------|-------------|
| 1 | `identify_bug` | Bug Identification | Easy | 5 | Read the code + tests, then report the bug's line number and a description |
| 2 | `fix_bug` | Bug Fix | Medium | 10 | Read the code + tests, then submit a corrected version that passes all tests |
| 3 | `full_triage` | Full Bug Triage | Hard | 15 | Identify the bug **and** submit a correct patch, scored on identification + patch quality + efficiency |

## Scenarios

15 handcrafted bug scenarios across 3 difficulty tiers (5 per tier):

### Easy
- **off_by_one** — `range(1, n)` skips the first element; should start at `0`
- **wrong_operator** — integer division `//` where float division `/` is needed
- **wrong_return** — `!=` used instead of `==` in a palindrome check
- **wrong_comparison** — `<` used instead of `>` in a clamp upper-bound check
- **missing_return** — function computes the correct result but never returns it

### Medium
- **boundary_check** — binary search initialises `high` to `len(arr)` instead of `len(arr) - 1`
- **logic_error** — rate limiter never records allowed timestamps, so it never blocks
- **missing_edge** — list flattener calls `extend(item)` instead of `extend(flatten(item))`
- **wrong_default** — `dict.get(word, 1)` seeds every first-seen word at count 2 instead of 1
- **mutation_bug** — `totals = numbers` aliases the input list, silently mutating the caller's data

### Hard
- **concurrency_bug** — LRU cache `get()` returns the value without promoting the key in access order
- **state_machine** — CSV parser guards the final field append with `if current`, dropping empty trailing fields
- **algorithm_bug** — cycle detection uses a single `visited` set, causing false positives on diamond DAGs
- **scope_bug** — lambda closures in a loop capture `i` by reference; all functions use the last value of `i`
- **memoization_bug** — mutable default argument `cache={}` is shared across all calls to `memoize()`

## Action Space

```json
{"tool": "read_code | run_tests | identify_bug | submit_patch", "parameters": {...}}
```

| Tool | Parameters | Description |
|------|-----------|-------------|
| `read_code` | `{"file": "main"}` or `{"file": "test"}` | Read the buggy source or the test file |
| `run_tests` | `{}` | Execute the test suite and get pass/fail results |
| `identify_bug` | `{"line": int, "description": str}` | Report the suspected bug location and root cause |
| `submit_patch` | `{"patched_code": str}` | Submit a complete corrected source file |

## Observation Space

Each step returns a JSON observation with:

| Field | Type | Description |
|-------|------|-------------|
| `scenario_id` | str | Active scenario identifier |
| `difficulty` | str | `easy` / `medium` / `hard` |
| `task_description` | str | Natural-language task prompt |
| `buggy_code` | str | The code containing the bug |
| `file_name` | str | Source file name |
| `test_code` | str | Test suite |
| `last_action_result` | str | Textual feedback from the last tool call |
| `test_results` | list | Per-test pass/fail details |
| `tests_passing` | int | Number of tests currently passing |
| `tests_total` | int | Total tests in the suite |
| `bug_identified` | bool | Whether `identify_bug` has been called |
| `patch_submitted` | bool | Whether `submit_patch` has been called |
| `patch_correct` | bool | Whether the last patch passed all tests |
| `steps_taken` | int | Steps used so far |
| `max_steps` | int | Step budget for this task |
| `steps_remaining` | int | `max_steps - steps_taken` |
| `action_history` | list[str] | Ordered list of all tool calls this episode |
| `error_trace` | str | Error output from the most recent test run or failed patch |
| `patch_attempts` | int | Number of `submit_patch` calls this episode |

## Reward Design

Rewards provide signal throughout the trajectory — not just at episode end.

| Event | Reward |
|-------|--------|
| `read_code` (first call) | +0.01 |
| `run_tests` | +0.02 |
| `identify_bug` — `identify_bug` task (terminal) | grader score × 1.0 |
| `identify_bug` — other tasks (intermediate) | grader score × 0.1 |
| `submit_patch` all tests pass — `fix_bug` | `grade_fix_bug()` (0.85–1.0) |
| `submit_patch` all tests pass — `full_triage` | `grade_full_triage()` (0.0–1.0, includes efficiency) |
| `submit_patch` partial pass — `fix_bug` / `full_triage` | `grade_fix_bug()` / `grade_full_triage()` on partial results (0.0–0.85) |
| Unknown tool / missing parameters | −0.05 |
| `full_triage`: patch before reading code or running tests | −0.03 |

## Grading Breakdown (0.0 – 1.0)

### Task 1: `identify_bug`
| Component | Weight |
|-----------|--------|
| Correct line number (exact) | 0.60 |
| Correct line ±1 | 0.30 |
| Keyword overlap with ground-truth description | 0.40 |

### Task 2: `fix_bug`
| Component | Weight |
|-----------|--------|
| Test pass rate | 0.85 |
| Code quality (non-empty, reasonable) | 0.15 |

### Task 3: `full_triage`
| Component | Weight |
|-----------|--------|
| Bug identification score | 0.20 |
| Patch test pass rate | 0.50 |
| Description quality | 0.15 |
| Step efficiency (1 − steps_taken/max_steps) | 0.15 |

## Baseline Scores

Produced by running scripted agents at three capability tiers (see `demo_scores.py`). No API key required — these are deterministic oracle scripts, not LLM calls.

| Task | Easy (Oracle) | Medium (Capable) | Hard (Weak) |
|------|:---:|:---:|:---:|
| `identify_bug` | 1.000 | 0.400 | 0.053 |
| `fix_bug` | 1.000 | 0.730 | 0.560 |
| `full_triage` | 0.960 | 0.750 | 0.408 |

**Agent tiers:**
- **Oracle (easy)** — correct line, full description, correct patch in optimal step sequence
- **Capable (medium)** — line off by 2, partial description, near-correct patch (fails 1–3 tests)
- **Weak (hard)** — wrong line, generic description, submits the original buggy code unchanged

> **Difficulty curve**: scores decrease monotonically easy → medium → hard across all tasks.  
> Hard partial scores reflect tests that happen to pass even on the unchanged buggy code.

### LLM Inference

`inference.py` runs a real LLM through all 3 tasks × 3 scenario tiers and writes `inference_results.json`. This requires an API key (see [Environment Variables](#environment-variables) below). The deterministic `demo_scores.py` baseline above is sufficient to verify the difficulty curve without one.

## Quick Start

### 1. Install dependencies

```bash
pip install -e ".[dev,inference]"
# or with uv:
uv sync --extra dev --extra inference
```

### 2. Start the server locally

```bash
cd server
uvicorn app:app --host 0.0.0.0 --port 7860
# Server starts at http://localhost:7860
```

### 3. Run deterministic difficulty-curve demo (no API key needed)

```bash
python demo_scores.py
```

Runs three scripted agents (oracle / capable / weak) and prints the score table. No LLM or API key required.

### 4. Run baseline LLM inference (requires API key)

```bash
export HF_TOKEN="hf_..."          # HuggingFace API key
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export ENV_URL="http://localhost:7860"

python inference.py
```

Results are written to `inference_results.json`.

### 5. Run tests

```bash
pytest tests/ -v   # 46 tests
```

### 6. Validate spec compliance

```bash
openenv validate   # or: python -m openenv validate
```

## Docker Deployment

```bash
# Build from repo root (Dockerfile is in server/)
docker build -f server/Dockerfile -t bug-triage-env .
docker run -p 7860:7860 bug-triage-env
# → http://localhost:7860/health
```

## HuggingFace Spaces Deployment

1. Create a new HF Space with **Docker** SDK
2. Push the entire project to the Space repository
3. The `server/Dockerfile` frontmatter configures the Space automatically

> **Note from OpenEnv tutorial-03**: HTTP `/reset` and `/step` are disabled on HF Spaces.  
> All stateful episodes use **WebSocket** (`/ws`) — which is what `inference.py` and the `EnvClient` use automatically.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws` | WebSocket | Persistent stateful session — used by `inference.py` and `EnvClient` |
| `/reset` | POST | Stateless reset (local dev / debug): `{"task_id": "...", "scenario_id": "..."}` |
| `/step` | POST | Stateless step (local dev / debug): `{"action": {"tool": "...", "parameters": {...}}}` |
| `/state` | GET | Current episode metadata (`episode_id`, `step_count`) |
| `/health` | GET | Liveness probe → `{"status": "healthy"}` |
| `/tasks` | GET | List all tasks with difficulty and `max_steps` |

## Project Structure

```
bug_triage_env/
├── models.py              # Pydantic Action / Observation models
├── scenarios.py           # 15 handcrafted bug scenarios (5 per difficulty tier)
├── graders.py             # 3 deterministic grader functions + TASKS registry
├── client.py              # Typed EnvClient subclass
├── inference.py           # Baseline LLM inference script (OpenAI client)
├── demo_scores.py         # Difficulty-curve demo (no LLM or API key required)
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Package + [project.scripts] entry point
├── uv.lock                # Locked dependency graph
├── __init__.py
├── server/
│   ├── app.py                      # FastAPI app + custom /tasks endpoint
│   ├── bug_triage_environment.py   # Environment implementation
│   ├── Dockerfile                  # HF Spaces Docker config
│   ├── requirements.txt
│   └── __init__.py
└── tests/
    └── test_environment.py         # 46 unit tests
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Only for `inference.py` | — | HuggingFace / API key for LLM inference |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM API endpoint |
| `MODEL_NAME` | No | `Qwen/Qwen2.5-72B-Instruct` | Model identifier |
| `OPENAI_API_KEY` | No | — | Alternative API key (fallback to `HF_TOKEN`) |
| `ENV_URL` | No | `http://localhost:7860` | Bug Triage server URL |

> `demo_scores.py` and all unit tests run without any API key.

## License

MIT
