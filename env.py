"""
env.py — Core OpenEnv Environment for PullRequest Arena

Implements the OpenEnv-compatible RL environment simulating a
real-world GitHub pull request code review workflow.

API:
    reset()        → observation (dict)
    step(action)   → (observation, reward, done, info)
    state()        → state (dict)

HTTP Endpoints (for HuggingFace Spaces deployment):
    POST /reset    → initial observation
    POST /step     → (observation, reward, done, info)
    GET  /state    → current state
    GET  /health   → health check
"""

import json
import os
from pathlib import Path

from grader import grade


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ACTION_TYPES = {"approve", "request_changes", "comment", "suggest_fix"}
TASKS_FILE = Path(__file__).parent / "tasks.json"


# ---------------------------------------------------------------------------
# Environment Class
# ---------------------------------------------------------------------------

class PullRequestArenaEnv:
    """
    OpenEnv-compatible environment for AI code review.

    The environment loads tasks from tasks.json and presents them
    as pull request observations. An agent reviews each PR by
    submitting structured actions, and receives reward signals
    based on the quality of its review.
    """

    def __init__(self, tasks_path: str | Path | None = None):
        """
        Initialize the environment.

        Args:
            tasks_path: Optional path to tasks.json.
                        Defaults to tasks.json in the same directory.
        """
        self._tasks_path = Path(tasks_path) if tasks_path else TASKS_FILE
        self._tasks: list[dict] = []
        self._current_task_index: int = 0
        self._current_task: dict | None = None
        self._done: bool = True
        self._episode_rewards: list[float] = []
        self._step_count: int = 0
        self._review_status: str = "idle"

        # Load tasks on init
        self._load_tasks()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_tasks(self) -> None:
        """Load and validate tasks from the JSON dataset."""
        with open(self._tasks_path, "r", encoding="utf-8") as f:
            self._tasks = json.load(f)

        if not self._tasks or len(self._tasks) < 3:
            raise ValueError(
                f"tasks.json must contain at least 3 tasks, "
                f"found {len(self._tasks)}."
            )

        # Validate each task has required fields
        required_fields = {
            "id", "difficulty", "pr_title", "pr_description",
            "files_changed", "code_diff", "language", "tests_passed",
            "expected_action", "expected_keywords", "bug_description",
        }
        for task in self._tasks:
            missing = required_fields - set(task.keys())
            if missing:
                raise ValueError(
                    f"Task {task.get('id', '?')} missing fields: {missing}"
                )

    def _build_observation(self, task: dict) -> dict:
        """
        Build a structured observation from a task.

        Returns a JSON-serializable dict matching the observation schema.
        """
        return {
            "pr_title": task["pr_title"],
            "pr_description": task["pr_description"],
            "files_changed": task["files_changed"],
            "code_diff": task["code_diff"],
            "language": task["language"],
            "tests_passed": task["tests_passed"],
            "repository_context": task.get("repository_context", ""),
        }

    def _validate_action(self, action: dict) -> None:
        """
        Validate that an action conforms to the action schema.

        Raises ValueError if the action is malformed.
        """
        if not isinstance(action, dict):
            raise ValueError(
                f"Action must be a dict, got {type(action).__name__}."
            )

        action_type = action.get("type")
        if not action_type or action_type not in VALID_ACTION_TYPES:
            raise ValueError(
                f"Invalid action type '{action_type}'. "
                f"Must be one of: {VALID_ACTION_TYPES}"
            )

        if "comment" not in action:
            raise ValueError("Action must include a 'comment' field.")

    # ------------------------------------------------------------------
    # OpenEnv Public API
    # ------------------------------------------------------------------

    def reset(self, task_index: int | None = None) -> dict:
        """
        Start a new episode.

        Loads a task, initializes episode state, and returns the
        initial observation.

        Args:
            task_index: Optional index to select a specific task.
                        If None, uses the next task in sequence.
                        Wraps around if index exceeds task count.

        Returns:
            observation (dict): The pull request data for the agent
                                to review.
        """
        if task_index is not None:
            self._current_task_index = task_index % len(self._tasks)
        # else keep current index (advances after each episode)

        self._current_task = self._tasks[self._current_task_index]
        self._done = False
        self._episode_rewards = []
        self._step_count = 0
        self._review_status = "pending"

        return self._build_observation(self._current_task)

    def step(self, action: dict) -> tuple[dict, float, bool, dict]:
        """
        Process an agent action and return the next state.

        Args:
            action (dict): Agent's review action with keys:
                - "type"    (str): One of approve, request_changes,
                                   comment, suggest_fix
                - "comment" (str): The review comment

        Returns:
            tuple of:
                observation (dict) : Updated observation (same PR)
                reward      (float): Score between 0.0 and 1.0
                done        (bool) : Whether the episode is complete
                info        (dict) : Additional metadata
        """
        if self._done:
            raise RuntimeError(
                "Episode is done. Call reset() to start a new episode."
            )

        if self._current_task is None:
            raise RuntimeError(
                "No active task. Call reset() before step()."
            )

        # Validate action
        self._validate_action(action)
        self._step_count += 1

        # Grade the action
        reward = grade(action, self._current_task)
        self._episode_rewards.append(reward)

        # Episode ends after one step (single-turn review)
        self._done = True
        self._review_status = "completed"

        # Advance to next task for the next reset()
        self._current_task_index = (
            (self._current_task_index + 1) % len(self._tasks)
        )

        # Build observation and info
        observation = self._build_observation(self._current_task)
        info = {
            "task_id": self._current_task["id"],
            "difficulty": self._current_task["difficulty"],
            "step_count": self._step_count,
            "episode_rewards": list(self._episode_rewards),
            "expected_action": self._current_task["expected_action"],
            "bug_description": self._current_task["bug_description"],
        }

        return observation, reward, self._done, info

    def state(self) -> dict:
        """
        Return the current environment state.

        Returns:
            dict with keys:
                - current_task_id   (int) : ID of the current task
                - current_task_index(int) : Index in the task list
                - total_tasks       (int) : Total number of tasks
                - files_remaining   (int) : Files left to review (0 or 1)
                - review_status     (str) : "idle", "pending", or "completed"
                - done              (bool): Whether episode is finished
                - step_count        (int) : Steps taken this episode
                - episode_rewards   (list): Rewards collected this episode
        """
        task_id = (
            self._current_task["id"] if self._current_task else None
        )

        return {
            "current_task_id": task_id,
            "current_task_index": self._current_task_index,
            "total_tasks": len(self._tasks),
            "files_remaining": 0 if self._done else 1,
            "review_status": self._review_status,
            "done": self._done,
            "step_count": self._step_count,
            "episode_rewards": list(self._episode_rewards),
        }

    @property
    def tasks(self) -> list[dict]:
        """Return the loaded task list (read-only copy)."""
        return list(self._tasks)

    @property
    def num_tasks(self) -> int:
        """Return the number of tasks."""
        return len(self._tasks)


# ---------------------------------------------------------------------------
# HTTP Server (Flask) for HuggingFace Spaces Deployment
# ---------------------------------------------------------------------------

def create_app(env: PullRequestArenaEnv | None = None):
    """
    Create a Flask application exposing the environment via HTTP.

    Endpoints:
        POST /reset           → Reset environment, return observation
        POST /step            → Submit action, return (obs, reward, done, info)
        GET  /state           → Return current environment state
        GET  /health          → Health check
        GET  /tasks           → List all task summaries
        GET  /                → Landing page / API info
    """
    from flask import Flask, request, jsonify

    app = Flask(__name__)
    environment = env or PullRequestArenaEnv()

    @app.route("/", methods=["GET"])
    def index():
        """Landing page with API information."""
        return jsonify({
            "name": "PullRequest Arena",
            "description": (
                "An OpenEnv environment for AI code review "
                "training and evaluation."
            ),
            "version": "1.0.0",
            "endpoints": {
                "POST /reset": "Start a new review episode",
                "POST /step": "Submit a review action",
                "GET /state": "Get current environment state",
                "GET /health": "Health check",
                "GET /tasks": "List available tasks",
            },
            "total_tasks": environment.num_tasks,
        })

    @app.route("/reset", methods=["POST"])
    def reset():
        """Reset the environment and return the initial observation."""
        data = request.get_json(silent=True) or {}
        task_index = data.get("task_index", None)

        observation = environment.reset(task_index=task_index)
        return jsonify({"observation": observation})

    @app.route("/step", methods=["POST"])
    def step():
        """Process an agent action and return results."""
        data = request.get_json(silent=True)

        if not data or "action" not in data:
            return jsonify({
                "error": (
                    "Request must include 'action' with "
                    "'type' and 'comment' fields."
                )
            }), 400

        action = data["action"]

        try:
            observation, reward, done, info = environment.step(action)
        except (ValueError, RuntimeError) as e:
            return jsonify({"error": str(e)}), 400

        return jsonify({
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info,
        })

    @app.route("/state", methods=["GET"])
    def get_state():
        """Return the current environment state."""
        return jsonify(environment.state())

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "tasks_loaded": environment.num_tasks})

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        """List task summaries (without solutions)."""
        summaries = [
            {
                "id": t["id"],
                "difficulty": t["difficulty"],
                "pr_title": t["pr_title"],
                "language": t["language"],
            }
            for t in environment.tasks
        ]
        return jsonify({"tasks": summaries, "total": environment.num_tasks})

    return app


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app = create_app()
    app.run(host="0.0.0.0", port=port)
