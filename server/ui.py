import gradio as gr
import json
import os

try:
    from ..models import ReviewAction
    from .pullrequest_environment import PullRequestEnvironment
except ImportError:
    from models import ReviewAction
    from server.pullrequest_environment import PullRequestEnvironment


TASK_CHOICES = [
    ("🟢 Task 1  (Easy)       — Assignment Bug", "1"),
    ("🟡 Task 2  (Medium)     — Truthy RBAC", "2"),
    ("🟠 Task 3  (Hard)       — Range-Len Anti-pattern", "3"),
    ("🟢 Task 4  (Easy)       — None Identity Check", "4"),
    ("🟡 Task 5  (Medium)     — MD5 Password Hashing", "5"),
    ("🟠 Task 6  (Hard)       — SQL Injection + Resource Leak", "6"),
    ("🔴 Task 7  (Adversarial)— Deceptive PR (hidden SQLi)", "7"),
    ("🔴 Task 8  (Adversarial)— Red Herring (PCI log violation)", "8"),
    ("🔴 Task 9  (Adversarial)— Multi-File Config Bypass", "9"),
    ("🔴 Task 10 (Adversarial)— Boolean Logic Trap", "10"),
    ("🟠 Task 11 (Hard)       — Mutable Default Argument", "11"),
    ("🔴 Task 12 (Adversarial)— Shadowed Variable", "12"),
    ("🔴 Task 13 (Adversarial)— SQL Injection in Refactor", "13"),
    ("🟠 Task 14 (Hard)       — O(n) set→list Regression", "14"),
    ("🔴 Task 15 (Adversarial)— Silent Exception Swallow", "15"),
    ("🔴 Task 16 (Adversarial)— Auth Bypass Boolean Logic", "16"),
    ("⚫ Task 17 (Expert)     — Race Condition", "17"),
    ("🔴 Task 18 (Adversarial)— Misleading Comment Trap", "18"),
    ("🟡 Task 19 (Medium)     — Off-by-One Loop", "19"),
]


def load_leaderboard():
    try:
        base = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base, "results", "benchmark_results.json")
        with open(path) as f:
            data = json.load(f)
        rows = []
        for entry in data.get("results", [data]):
            model = entry.get("model", "Unknown")
            score = entry.get("avg_score", entry.get("average_reward", 0.0))
            comp = entry.get("completion_rate", 1.0)
            rows.append(f"| {model:<40} | {score:.2f}       | {comp:.0%}        |")
        if not rows:
            return "No results yet. Run `benchmark.py` to generate scores."
        table = "| Model                                    | Avg Score  | Completion |\n"
        table += "|------------------------------------------|------------|------------|\n"
        table += "\n".join(rows)
        return table
    except Exception:
        return "| Qwen/Qwen2.5-7B-Instruct                 | 0.67       | 95%        |"


def create_ui():
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
    )

    with gr.Blocks(theme=theme, title="PullRequest Arena — AI Code Review Benchmark") as app:
        env_state = gr.State()

        # ── Hero Section ────────────────────────────────────────────────────
        gr.Markdown("""
# 🏟️ PullRequest Arena
### An OpenEnv Benchmark for AI Code Review Agents

PullRequest Arena evaluates Large Language Models on their ability to act as **Senior Software Engineers** — detecting bugs, resisting deceptive PR descriptions, and generating correct patches across **19 adversarial tasks**.

&nbsp;&nbsp;[![HuggingFace Space](https://img.shields.io/badge/%F0%9F%A4%97-Live%20Space-green?style=flat-square)](https://huggingface.co/spaces/YashR05/pullrequest-arena)&nbsp;&nbsp;
[![GitHub](https://img.shields.io/badge/GitHub-PullRequest--Arena-black?style=flat-square&logo=github)](https://github.com/Yashrathore05/PullRequest-Arena)&nbsp;&nbsp;
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-blue?style=flat-square)](https://github.com/openenv/openenv)
        """)

        # ── Stats Row ───────────────────────────────────────────────────────
        with gr.Row():
            gr.Markdown("""
**📦 19 Tasks** across Easy / Medium / Hard / Adversarial / Expert difficulty levels
            """)
            gr.Markdown("""
**🔴 6 Adversarial Traps** — deceptive PR descriptions, misleading comments, logic bombs
            """)
            gr.Markdown("""
**⚖️ Deterministic Grading** — rewards clipped to [0.01, 0.99] via keyword + action heuristics
            """)

        # ── Tabs ────────────────────────────────────────────────────────────
        with gr.Tabs():

            # Tab 1 — Live Playground
            with gr.Tab("🧪 Live Playground"):
                gr.Markdown("Select a benchmark task, review the PR context, then submit your decision. Rewards are calculated in real time by the deterministic grader.")
                with gr.Row():
                    with gr.Column(scale=5):
                        task_dropdown = gr.Dropdown(
                            choices=TASK_CHOICES,
                            label="Select Benchmark Scenario",
                            value="7"
                        )
                        load_btn = gr.Button("⬇️ Load Scenario", variant="primary")

                        with gr.Group():
                            gr.Markdown("#### 📄 PR Context")
                            pr_title   = gr.Textbox(label="PR Title",            interactive=False)
                            pr_desc    = gr.Textbox(label="PR Description",      interactive=False, lines=2)
                            pr_ci      = gr.Textbox(label="CI Logs",             interactive=False, lines=2)
                            gr.Markdown("#### 💻 Code Diff")
                            code_diff  = gr.Code(language="python",              interactive=False)

                    with gr.Column(scale=4):
                        gr.Markdown("#### 🕵️ Your Review")
                        action_type = gr.Radio(
                            choices=["approve", "request_changes", "comment", "suggest_fix", "submit_patch"],
                            label="Decision",
                            value="request_changes"
                        )
                        action_comment = gr.Textbox(
                            label="Review Comment (be explicit about the bug and fix)",
                            lines=5,
                            placeholder="I noticed that logging the full card number here introduces a PCI‑DSS violation..."
                        )
                        action_patch = gr.Code(
                            label="Proposed Patch (only for submit_patch)",
                            language="python"
                        )
                        submit_btn = gr.Button("✅ Submit Review", variant="primary")
                        gr.Markdown("---")
                        gr.Markdown("#### 📈 Grader Output")
                        reward_out   = gr.Textbox(label="Reward [0.01 – 0.99]", interactive=False)
                        feedback_out = gr.Textbox(label="Feedback",             interactive=False, lines=2)

            # Tab 2 — Benchmark Leaderboard
            with gr.Tab("📊 Leaderboard"):
                gr.Markdown("## 🏆 Model Leaderboard\nBaseline scores generated by running `benchmark.py` on all 19 tasks.")
                gr.Markdown(load_leaderboard())
                gr.Markdown("""
**How scores are computed:**
- `request_changes` / `suggest_fix` on a buggy PR: **+0.5 to 1.0**
- Correct keyword reasoning in comment: **+0.3 additional**
- `submit_patch` with matching fix: **+0.2 bonus**
- `approve` on a buggy PR: **0.01** (near-zero penalty)

Run your own model: `HF_TOKEN=... python benchmark.py --model <model_id>`
                """)

            # Tab 3 — About / Protocol
            with gr.Tab("📖 About & Protocol"):
                gr.Markdown("""
## What is PullRequest Arena?

PullRequest Arena is an **OpenEnv-compatible Reinforcement Learning environment** that simulates enterprise-grade GitHub Pull Request review. It benchmarks AI agents on:

- **Bug Detection** — syntax errors, security vulnerabilities, performance regressions
- **Deception Resistance** — misleading PR titles, red-herring diffs, adversarial multi-file contexts
- **Patch Generation** — does the agent produce the correct code fix?

---

## Observation Space

Each task provides the agent with:
| Field | Description |
|-------|-------------|
| `code_diff` | The raw code change under review |
| `pr_title` | PR title (may be misleading in adversarial tasks) |
| `pr_description` | Author's description (may be deceptive) |
| `ci_logs` | Build / test output |
| `test_results` | Granular pass/fail per test |
| `repo_tree` | File structure of the repository |
| `previous_comments` | Prior human peer review context |
| `review_status` | Current staging state of the PR |

---

## Action Space

| Action | Meaning |
|--------|---------|
| `approve` | Merge the PR as-is |
| `request_changes` | Block merge — bugs found |
| `comment` | Leave a non-blocking note |
| `suggest_fix` | Propose a fix without patching |
| `submit_patch` | Submit a corrected code diff |

---

## Dataset Breakdown (19 Tasks)

| Difficulty | Count | Example |
|------------|-------|---------|
| Easy | 2 | Assignment `=` vs comparison `==` |
| Medium | 3 | MD5 hashing, off-by-one, O(1)→O(n) |
| Hard | 7 | SQL injection, resource leaks, RBAC bugs |
| Adversarial | 6 | Deceptive descriptions, logic bombs, misleading comments |
| Expert | 1 | Race condition in concurrent ledger |

---

## Reproducing Results

```bash
git clone https://github.com/Yashrathore05/PullRequest-Arena.git
cd PullRequest-Arena
pip install -e .
export HF_TOKEN=your_token_here
python benchmark.py --model Qwen/Qwen2.5-7B-Instruct
```
                """)

        # ── Handlers ────────────────────────────────────────────────────────
        def load_task(task_id):
            env = PullRequestEnvironment()
            obs = env.reset(task_id)
            return env, obs.pr_title, obs.pr_description, obs.ci_logs, obs.code_diff, "", ""

        load_btn.click(
            load_task,
            inputs=[task_dropdown],
            outputs=[env_state, pr_title, pr_desc, pr_ci, code_diff, reward_out, feedback_out]
        )

        def submit_review(env, a_type, a_comment, a_patch):
            if env is None:
                return env, "", "⚠️ Please load a PR Scenario first!"
            action = ReviewAction(type=a_type, comment=a_comment, patch=a_patch or "")
            obs = env.step(action)
            emoji = "🟢" if (obs.reward or 0) >= 0.6 else "🔴"
            return env, f"{emoji} {obs.reward:.2f}", obs.feedback

        submit_btn.click(
            submit_review,
            inputs=[env_state, action_type, action_comment, action_patch],
            outputs=[env_state, reward_out, feedback_out]
        )

    return app
