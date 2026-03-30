"""
FastAPI application for the Bug Triage Environment.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /health: Health check
    - GET /tasks: List available tasks
    - WS /ws: WebSocket for persistent sessions
"""

import os
import sys

# Ensure the parent directory is on sys.path so flat imports work
# both locally (python -m uvicorn app:app from server/) and in Docker.
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv-core is required. Install with: pip install openenv-core"
    ) from e

try:
    from ..models import BugTriageAction, BugTriageObservation
    from .bug_triage_environment import BugTriageEnvironment
except (ImportError, ModuleNotFoundError):
    from models import BugTriageAction, BugTriageObservation
    from bug_triage_environment import BugTriageEnvironment


app = create_app(
    BugTriageEnvironment,
    BugTriageAction,
    BugTriageObservation,
    env_name="bug_triage",
    max_concurrent_envs=100,
)


# Add custom task listing endpoint
@app.get("/tasks")
def list_tasks():
    """List available tasks with their difficulty and descriptions."""
    try:
        from ..graders import TASKS
    except ImportError:
        from graders import TASKS

    return {"tasks": TASKS}


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
