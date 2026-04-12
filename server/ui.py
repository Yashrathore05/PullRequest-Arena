import gradio as gr

try:
    from ..models import ReviewAction
    from .pullrequest_environment import PullRequestEnvironment
except ImportError:
    from models import ReviewAction
    from server.pullrequest_environment import PullRequestEnvironment

def create_ui():
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
    )

    with gr.Blocks(theme=theme, title="PullRequest Arena") as app:
        env_state = gr.State()
        
        with gr.Row():
            gr.Markdown(
                """
                # 🏟️ PullRequest Arena
                **Welcome to the definitive AI Code Review Benchmark.** 
                Test your skills (or your model's) against deceptive tasks featuring Red Herrings, misleading PR descriptions, and multi-file tracking.
                """
            )
        
        with gr.Row():
            with gr.Column(scale=5):
                with gr.Group():
                    task_dropdown = gr.Dropdown(
                        choices=[
                            ("Task 1 (Easy) - Assignment Bug", "1"), 
                            ("Task 2 (Medium) - Truthy RBAC", "2"), 
                            ("Task 3 (Hard) - Range-Len Pattern", "3"),
                            ("Task 4 (Easy) - None Identity", "4"), 
                            ("Task 5 (Medium) - MD5 Cryptography", "5"), 
                            ("Task 6 (Hard) - Resource Leak", "6"),
                            ("Task 7 (Hard) - DECEPTIVE PR (SQLi)", "7"), 
                            ("Task 8 (Hard) - RED HERRING (PCI logs)", "8"), 
                            ("Task 9 (Hard) - MULTI-FILE (Config bypass)", "9")
                        ],
                        label="Select Benchmark Scenario",
                        value="7"
                    )
                    load_btn = gr.Button("Load Scenario", variant="primary")
                    
                gr.Markdown("### 📄 Review Context")
                pr_title = gr.Textbox(label="PR Title", interactive=False)
                pr_desc = gr.Textbox(label="PR Description", interactive=False, lines=2)
                pr_ci = gr.Textbox(label="CI Logs / Build Output", interactive=False, lines=2)
                
                gr.Markdown("### 💻 Proposed Action (Code Diff)")
                code_diff = gr.Code(language="python", interactive=False)
                
            with gr.Column(scale=4):
                gr.Markdown("### 🕵️ Submit Code Review")
                gr.Markdown("Act as a Senior Engineer. Make a decision and write your finding. Our heuristic graders will evaluate your review.")
                
                action_type = gr.Radio(
                    choices=["approve", "request_changes", "comment", "suggest_fix", "submit_patch"],
                    label="Decision",
                    value="request_changes"
                )
                action_comment = gr.Textbox(label="Review Comment (Provide explicit reasoning)", lines=4, placeholder="I noticed that logging the card details directly here introduces a severe PCI-DSS violation...")
                action_patch = gr.Code(label="Proposed Patch (Required for submit_patch)", language="diff")
                submit_btn = gr.Button("Submit Evaluation", variant="primary")
                
                gr.Markdown("---")
                gr.Markdown("### 📈 Mathematical Evaluation")
                reward_out = gr.Textbox(label="Calculated Reward [0.01 - 0.99]", interactive=False)
                feedback_out = gr.Textbox(label="System Details", interactive=False, lines=2)

        def load_task(task_id):
            env = PullRequestEnvironment()
            obs = env.reset(task_id)
            return (
                env,
                obs.pr_title,
                obs.pr_description,
                obs.ci_logs,
                obs.code_diff,
                "",  
                ""   
            )

        load_btn.click(
            load_task,
            inputs=[task_dropdown],
            outputs=[env_state, pr_title, pr_desc, pr_ci, code_diff, reward_out, feedback_out]
        )

        def submit_review(env, a_type, a_comment, a_patch):
            if env is None:
                return env, "", "ERROR: Please load a PR Scenario first!"
            
            action = ReviewAction(type=a_type, comment=a_comment, patch=a_patch)
            obs = env.step(action)
            
            return env, str(obs.reward), obs.feedback

        submit_btn.click(
            submit_review,
            inputs=[env_state, action_type, action_comment, action_patch],
            outputs=[env_state, reward_out, feedback_out]
        )

    return app
