try:
    from ..models import ReviewAction, PRObservation
    from .pullrequest_environment import PullRequestEnvironment
    from .ui import create_ui
except ImportError:
    from models import ReviewAction, PRObservation
    from server.pullrequest_environment import PullRequestEnvironment
    from server.ui import create_ui

import gradio as gr

from openenv.core.env_server import create_app

env_app = create_app(
    PullRequestEnvironment,
    ReviewAction,
    PRObservation,
    env_name="pullrequest_arena"
)

# Render production UI overlay
ui = create_ui()
app = gr.mount_gradio_app(env_app, ui, path="/")
