import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import ReviewAction, PRObservation
from server.pullrequest_environment import PullRequestEnvironment
from server.graders import route_grader

def test_reset_returns_valid_observation():
    env = PullRequestEnvironment()
    obs = env.reset()
    assert obs.pr_title != ""
    assert obs.code_diff != ""
    assert obs.done is False

def test_step_correct_action_task_1():
    env = PullRequestEnvironment()
    env.reset("1")
    action = ReviewAction(type="request_changes", comment="== comparison operator")
    next_obs = env.step(action)
    assert next_obs.reward >= 0.6

def test_step_wrong_action_gets_low_score():
    env = PullRequestEnvironment()
    env.reset("1")
    action = ReviewAction(type="approve", comment="looks good")
    next_obs = env.step(action)
    assert next_obs.reward <= 0.1

def test_deceptive_pr_task_7():
    env = PullRequestEnvironment()
    env.reset("7")
    action = ReviewAction(type="approve", comment="looks fine, just a typo")
    next_obs = env.step(action)
    assert next_obs.reward == 0.01

def test_all_9_tasks_load():
    env = PullRequestEnvironment()
    for task_id in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        obs = env.reset(task_id)
        assert obs.pr_title != ""
        assert obs.code_diff != ""
        assert str(obs.task_id) == str(task_id)
