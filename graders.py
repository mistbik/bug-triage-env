"""
Graders for the Bug Triage & Patch Validation environment.

Three tasks with programmatic graders, each scoring 0.0-1.0:
- Task 1 (Easy): identify_bug — find the buggy line in a simple function
- Task 2 (Medium): fix_bug — produce a patch that passes all tests
- Task 3 (Hard): full_triage — diagnose + fix + efficiency, on hard scenarios
"""

import traceback
from typing import Dict


def _exec_tests(code: str, test_code: str, func_names: list) -> Dict:
    """Execute code + tests in a sandboxed namespace. Returns dict of test results."""
    namespace = {}
    results = {}
    try:
        exec(code, namespace)  # noqa: S102
    except Exception as e:
        return {name: {"passed": False, "error": f"Code exec error: {e}"} for name in func_names}

    # Inject defined names into test namespace
    test_namespace = dict(namespace)
    try:
        exec(test_code, test_namespace)  # noqa: S102
    except Exception as e:
        return {name: {"passed": False, "error": f"Test parse error: {e}"} for name in func_names}

    for name in func_names:
        fn = test_namespace.get(name)
        if fn is None:
            results[name] = {"passed": False, "error": f"Test {name} not found"}
            continue
        try:
            fn()
            results[name] = {"passed": True, "error": ""}
        except Exception as e:
            # Capture full traceback for richer error context
            tb = traceback.format_exc()
            error_msg = str(e) if str(e) else tb.strip().split("\n")[-1]
            results[name] = {"passed": False, "error": error_msg, "traceback": tb}
    return results


def _extract_test_names(test_code: str) -> list:
    """Extract test function names from test code."""
    names = []
    for line in test_code.splitlines():
        stripped = line.strip()
        if stripped.startswith("def test_"):
            name = stripped.split("(")[0].replace("def ", "")
            names.append(name)
    return names


def _normalize_code(code: str) -> str:
    """Normalize whitespace for comparison."""
    lines = [line.rstrip() for line in code.strip().splitlines()]
    return "\n".join(lines)


def _clamp(score: float) -> float:
    """Ensure score is strictly within (0, 1) as required by the validator."""
    return max(0.01, min(round(score, 4), 0.99))


def grade_identify_bug(scenario: Dict, agent_line: int, agent_description: str) -> float:
    """Grade Task 1: Bug identification.

    Score breakdown:
    - 0.6 for identifying the correct line (±1 tolerance)
    - 0.4 for a description that mentions relevant keywords

    Returns: float in [0.0, 1.0]
    """
    score = 0.0
    correct_line = scenario["bug_line"]

    # Line identification (0.6 weight)
    if agent_line == correct_line:
        score += 0.6
    elif abs(agent_line - correct_line) <= 1:
        score += 0.3

    # Description quality (0.4 weight) — keyword matching
    desc_lower = agent_description.lower()
    bug_desc_lower = scenario["bug_description"].lower()

    # Extract key terms from the ground truth description
    keywords = set()
    for word in bug_desc_lower.split():
        cleaned = word.strip(".,!?;:()")
        if len(cleaned) > 3:
            keywords.add(cleaned)

    if keywords:
        matched = sum(1 for kw in keywords if kw in desc_lower)
        keyword_score = min(matched / max(len(keywords) * 0.4, 1), 1.0)
        score += 0.4 * keyword_score

    return _clamp(score)


def grade_fix_bug(scenario: Dict, patched_code: str) -> float:
    """Grade Task 2: Bug fix via patch submission.

    Score breakdown:
    - 0.7 for all tests passing on the patched code
    - 0.15 for partial test passes (proportional)
    - 0.15 for code similarity to the correct solution (not identical copy-paste)

    Returns: float in [0.0, 1.0]
    """
    test_code = scenario["test_code"]
    test_names = _extract_test_names(test_code)

    if not test_names:
        return 0.01

    results = _exec_tests(patched_code, test_code, test_names)
    passing = sum(1 for r in results.values() if r["passed"])
    total = len(test_names)

    # Test pass score (0.85 weight)
    if passing == total:
        test_score = 0.85
    else:
        test_score = 0.85 * (passing / total)

    # Code quality: penalize if the patch is empty or trivially wrong
    code_score = 0.0
    if patched_code.strip():
        correct = _normalize_code(scenario["correct_code"])
        patched = _normalize_code(patched_code)
        if patched == correct:
            code_score = 0.15
        elif passing == total:
            # Different but also correct — reward novel fix
            code_score = 0.15
        elif passing > 0:
            code_score = 0.05

    return _clamp(test_score + code_score)


def grade_full_triage(
    scenario: Dict,
    agent_line: int,
    agent_description: str,
    patched_code: str,
    steps_taken: int,
    max_steps: int,
) -> float:
    """Grade Task 3: Full triage (hard).

    Score breakdown:
    - 0.20 for correct bug identification
    - 0.50 for a patch that passes all tests
    - 0.15 for description quality
    - 0.15 for efficiency (fewer steps = higher score)

    Returns: float in [0.0, 1.0]
    """
    # Bug identification (0.20)
    id_score = grade_identify_bug(scenario, agent_line, agent_description)
    identification = 0.20 * id_score

    # Patch quality (0.50)
    fix_score = grade_fix_bug(scenario, patched_code)
    patch_quality = 0.50 * fix_score

    # Description quality (0.15) — reuse keyword scoring from identify
    desc_score = id_score  # Already includes description component
    description = 0.15 * desc_score

    # Efficiency (0.15) — linear decay from max_steps
    if max_steps > 0:
        efficiency = 0.15 * max(0.0, 1.0 - (steps_taken / max_steps))
    else:
        efficiency = 0.0

    return _clamp(identification + patch_quality + description + efficiency)


# Task definitions for the openenv.yaml / task registry
TASKS = [
    {
        "id": "identify_bug",
        "name": "Identify Bug",
        "difficulty": "easy",
        "description": (
            "Given a buggy code snippet and failing tests, identify the "
            "exact line containing the bug and describe the root cause."
        ),
        "grader": "grade_identify_bug",
        "max_steps": 5,
        "scenarios": [
            "easy_off_by_one",
            "easy_wrong_operator",
            "easy_wrong_return",
            "easy_wrong_comparison",
            "easy_missing_return",
        ],
    },
    {
        "id": "fix_bug",
        "name": "Fix Bug",
        "difficulty": "medium",
        "description": (
            "Given a buggy code snippet, diagnose the issue and submit "
            "a corrected version that passes all provided tests."
        ),
        "grader": "grade_fix_bug",
        "max_steps": 10,
        "scenarios": [
            "medium_boundary_check",
            "medium_logic_error",
            "medium_missing_edge",
            "medium_wrong_default",
            "medium_mutation_bug",
        ],
    },
    {
        "id": "full_triage",
        "name": "Full Triage & Patch",
        "difficulty": "hard",
        "description": (
            "Given complex buggy code, diagnose the root cause, identify "
            "the buggy line, describe the issue, and submit a correct patch — "
            "all within a limited step budget."
        ),
        "grader": "grade_full_triage",
        "max_steps": 15,
        "scenarios": [
            "hard_concurrency_bug",
            "hard_state_machine",
            "hard_algorithm_bug",
            "hard_scope_bug",
            "hard_memoization_bug",
        ],
    },
]
