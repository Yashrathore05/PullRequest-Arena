from openenv.core.env_client import EnvClient

try:
    from .models import ReviewAction, PRObservation
except ImportError:
    from models import ReviewAction, PRObservation

class PullRequestEnv(EnvClient):
    action_type = ReviewAction
    observation_type = PRObservation
