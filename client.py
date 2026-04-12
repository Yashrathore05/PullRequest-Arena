from openenv.core.generic_client import GenericEnvClient

try:
    from .models import ReviewAction, PRObservation
except ImportError:
    from models import ReviewAction, PRObservation

class PullRequestEnv(GenericEnvClient):
    action_type = ReviewAction
    observation_type = PRObservation
