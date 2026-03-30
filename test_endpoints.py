"""
Endpoint tests for the Bug Triage server.

KEY DESIGN NOTE (from OpenEnv tutorial-03):
  - HTTP /reset and /step are STATELESS: each call creates a new env instance.
  - State is NOT shared between separate HTTP calls.
  - For stateful episodes, use WebSocket (/ws) — that's what the Python client does.
  - HTTP endpoints are for debugging / one-shot use only.

So we test each endpoint independently.
"""
import urllib.request
import json

BASE = "http://localhost:7860"


def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read().decode())


def get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read().decode())


print("=" * 55)
print("Bug Triage — Endpoint Verification")
print("(HTTP endpoints are stateless by OpenEnv design)")
print("=" * 55)

# 1. Health
print("\n1. GET /health")
status, body = get("/health")
print(f"   {status} → {body}")
assert status == 200 and body.get("status") == "healthy"
print("   PASS")

# 2. Reset — stateless, returns full observation for specified scenario
print("\n2. POST /reset")
status, body = post("/reset", {"task_id": "identify_bug", "scenario_id": "easy_off_by_one"})
obs = body.get("observation", body)
print(f"   {status} → scenario_id={obs.get('scenario_id')}, difficulty={obs.get('difficulty')}")
print(f"   steps_taken={obs.get('steps_taken')}, steps_remaining={obs.get('steps_remaining')}")
print(f"   action_history={obs.get('action_history')}, patch_attempts={obs.get('patch_attempts')}")
assert status == 200
assert obs.get("scenario_id") == "easy_off_by_one"
assert obs.get("steps_taken") == 0
assert obs.get("steps_remaining") == obs.get("max_steps")
assert obs.get("action_history") == []
print("   PASS")

# 3. Step (read_code) — stateless: fresh env, auto-resets to random scenario
# Cannot assume specific scenario — just validate response shape + state richness
print("\n3. POST /step (read_code) — stateless, fresh env")
status, body = post("/step", {"action": {"tool": "read_code", "parameters": {"file": "main"}}})
obs = body.get("observation", body)
print(f"   {status} → steps_taken={obs.get('steps_taken')}, scenario={obs.get('scenario_id')}")
print(f"   action_history={obs.get('action_history')}")
print(f"   result: {str(obs.get('last_action_result',''))[:60]}...")
assert status == 200
assert obs.get("steps_taken") == 1
assert len(obs.get("action_history", [])) == 1
assert "read_code" in obs.get("action_history", [""])[0]
print("   PASS")

# 4. Step (run_tests) — stateless, fresh env
print("\n4. POST /step (run_tests) — stateless, fresh env")
status, body = post("/step", {"action": {"tool": "run_tests", "parameters": {}}})
obs = body.get("observation", body)
print(f"   {status} → tests {obs.get('tests_passing')}/{obs.get('tests_total')}")
print(f"   error_trace present: {bool(obs.get('error_trace'))}")
print(f"   steps_remaining={obs.get('steps_remaining')}")
assert status == 200
assert obs.get("tests_total", 0) > 0
assert obs.get("steps_taken") == 1
print("   PASS")

# 5. Step (identify_bug) — validate state richness fields
print("\n5. POST /step (identify_bug)")
status, body = post("/step", {"action": {"tool": "identify_bug", "parameters": {"line": 4, "description": "off-by-one error in range"}}})
obs = body.get("observation", body)
print(f"   {status} → bug_identified={obs.get('bug_identified')}")
print(f"   result: {str(obs.get('last_action_result',''))[:80]}")
assert status == 200
assert obs.get("bug_identified") is True
print("   PASS")

# 6. GET /state
print("\n6. GET /state")
status, body = get("/state")
print(f"   {status} → {json.dumps(body)[:150]}")
assert status == 200
print("   PASS")

# 7. GET /tasks
print("\n7. GET /tasks")
status, body = get("/tasks")
assert status == 200
for t in body.get("tasks", []):
    print(f"   - {t['id']}: {t['name']} ({t['difficulty']}, max_steps={t['max_steps']})")
assert len(body.get("tasks", [])) == 3
assert {t["id"] for t in body["tasks"]} == {"identify_bug", "fix_bug", "full_triage"}
print("   PASS")

print()
print("=" * 55)
print("ALL 7 ENDPOINT CHECKS PASSED")
print("=" * 55)
print()
print("Architecture summary:")
print("  /ws      → WebSocket, stateful sessions (Python client default)")
print("  /reset   → HTTP stateless, new env per call (debug/one-shot)")
print("  /step    → HTTP stateless, new env per call (debug/one-shot)")
print("  /state   → HTTP, episode metadata")
print("  /health  → HTTP, liveness probe")
print("  /tasks   → HTTP, task registry")
print()
print("HF Spaces: WebSocket only (HTTP /reset+/step blocked by HF infra)")
print("Local dev:  both HTTP and WebSocket work")

