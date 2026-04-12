"""
Pydantic models for the PullRequest Arena environment.

ReviewAction — The structured action an AI agent returns after reviewing a PR.
    Supports four action types: approve, request_changes, comment, suggest_fix.
    The comment field contains the agent's explanation of any issues found.

PRObservation — The observation presented to the agent for each task.
    Contains all context needed to review a fake pull request: title, description,
    changed files, code diff, language, test/CI status, repository context,
    task metadata, and episode feedback (reward, done flag).
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field, BaseModel
from typing import Optional


class ReviewAction(BaseModel):
    """
    Action format the agent must output to interact with the environment.
    """
    type: str = Field(description="Action type: approve, request_changes, comment, suggest_fix, submit_patch")
    comment: str = Field(description="Review comment text")
    patch: str | None = Field(default=None, description="The proposed code patch (only for submit_patch)")


class PRObservation(Observation):
    """Observation containing all pull-request context for a single review task."""

    pr_title: str = Field(default="")
    pr_description: str = Field(default="")
    files_changed: list = Field(default_factory=list)
    code_diff: str = Field(default="")
    language: str = Field(default="python")
    tests_passed: bool = Field(default=False)
    ci_logs: str = Field(default="")
    repository_context: str = Field(default="")
    test_results: dict | None = Field(default=None, description="Detailed breakdown of passed/failed tests")
    repo_tree: list[str] | None = Field(default=None, description="Current structure of files in the repo")
    previous_comments: list[str] | None = Field(default=None, description="Any previous human peer reviews on this PR")
    review_status: str | None = Field(default="pending", description="The current staging status of the PR")
    task_id: str = Field(default="")
    difficulty: str = Field(default="easy")
    feedback: str = Field(default="")
    done: bool = Field(default=False)
    reward: float = Field(default=0.01)
