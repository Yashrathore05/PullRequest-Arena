import json
import random
import uuid
import os
from openenv.core.env_server.interfaces import Environment

try:
    from ..models import ReviewAction, PRObservation
    from .graders import route_grader
except ImportError:
    from models import ReviewAction, PRObservation
    from server.graders import route_grader

class PullRequestEnvironment(Environment):
    def __init__(self):
        self.current_task = None
        self.episode_id = None
        self.step_count = 0
        
        # Determine path to tasks.json (typically in parent directory from server/)
        base_dir = os.path.dirname(__file__)
        tasks_path = os.path.join(base_dir, "..", "tasks.json")
        if not os.path.exists(tasks_path):
            tasks_path = os.path.join(base_dir, "tasks.json")
            if not os.path.exists(tasks_path):
                # Fallback to CWD
                tasks_path = "tasks.json"
                
        with open(tasks_path, "r") as f:
            self.tasks = json.load(f)

    def reset(self, task_id=None):
        if task_id is not None:
            # Find the specific task by id string
            target = str(task_id)
            self.current_task = next((t for t in self.tasks if str(t["id"]) == target), None)
            if not self.current_task:
                self.current_task = random.choice(self.tasks)
        else:
            self.current_task = random.choice(self.tasks)
            
        self.episode_id = str(uuid.uuid4())
        self.step_count = 0
        
        return PRObservation(
            pr_title=self.current_task.get("pr_title", ""),
            pr_description=self.current_task.get("pr_description", ""),
            files_changed=self.current_task.get("files_changed", []),
            code_diff=self.current_task.get("code_diff", ""),
            language=self.current_task.get("language", "python"),
            tests_passed=self.current_task.get("tests_passed", False),
            ci_logs=self.current_task.get("ci_logs", ""),
            repository_context=self.current_task.get("repository_context", ""),
            task_id=str(self.current_task["id"]),
            difficulty=self.current_task.get("difficulty", "easy"),
            feedback="",
            done=False,
            reward=0.0
        )

    def step(self, action: ReviewAction):
        reward = route_grader(str(self.current_task["id"]), action, self.current_task)
        self.step_count += 1
        
        feedback = f"Review action '{action.type}' submitted. Evaluated reward: {reward:.2f}."
        
        return PRObservation(
            pr_title=self.current_task.get("pr_title", ""),
            pr_description=self.current_task.get("pr_description", ""),
            files_changed=self.current_task.get("files_changed", []),
            code_diff=self.current_task.get("code_diff", ""),
            language=self.current_task.get("language", "python"),
            tests_passed=self.current_task.get("tests_passed", False),
            ci_logs=self.current_task.get("ci_logs", ""),
            repository_context=self.current_task.get("repository_context", ""),
            task_id=str(self.current_task["id"]),
            difficulty=self.current_task.get("difficulty", "easy"),
            feedback=feedback,
            done=True,
            reward=reward
        )

    @property
    def state(self):
        return {
            "episode_id": self.episode_id,
            "step_count": self.step_count,
            "current_task_id": str(self.current_task["id"]) if self.current_task else None,
            "review_status": "done" if self.step_count > 0 else "pending"
        }
