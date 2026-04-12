try:
    from ..models import ReviewAction, PRObservation
    from .pullrequest_environment import PullRequestEnvironment
except ImportError:
    from models import ReviewAction, PRObservation
    from server.pullrequest_environment import PullRequestEnvironment

from openenv.core.env_server import create_app

app = create_app(
    PullRequestEnvironment,
    ReviewAction,
    PRObservation,
    env_name="pullrequest_arena"
)
