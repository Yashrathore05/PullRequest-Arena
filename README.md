---
title: PullRequest Arena
emoji: 🏟️
colorFrom: gray
colorTo: purple
sdk: docker
pinned: false
---
# 🏟️ PullRequest Arena

**PullRequest Arena** is an [OpenEnv](https://github.com/openenv/openenv) reinforcement learning environment that simulates a real-world GitHub code review flow. It is built to benchmark AI agents on their ability to act as senior software engineers by reviewing Pull Requests, analyzing complex diffs, and identifying critical programmatic vulnerabilities.

## 🚀 The Challenge
Agents are presented with Pull Request metadata (Title, Description, CI Logs, Changed Files) and the exact Code Diff. The agent must return a strict decision (`approve`, `request_changes`, `comment`, `suggest_fix`) along with an explanatory comment identifying the bug.

Unlike simple algorithmic tests, **PullRequest Arena heavily tests an agent's ability to resist deception**.

### 🌟 Featured Tasks (The Traps)
We've engineered 9 distinct tasks mapping from Easy to Hard. Features include:
1. **The Deceptive PR (Task 7):** The PR description claims to "Just fix a minor typo", but the actual diff introduces a blatant SQL Injection. Will the AI trust the description, or actually read the code?
2. **The Red Herring (Task 8):** A PR filled with multiple suspicious-looking (but perfectly safe) styling anti-patterns alongside a single critical PCI compliance violation (logging full credit card numbers). Can the AI ignore the distractions?
3. **Multi-File Reasoning (Task 9):** A rate-limiting update where the deceptive code occurs in `middleware.py`, but the actual disabling bug occurs in `config.py` (`RATE_LIMIT = 0`).

## 🛠️ Usage & Installation

**Prerequisites:** Python 3.11+

```bash
git clone https://github.com/Yashrathore05/PullRequest-Arena.git
cd PullRequest-Arena
pip install -e .
```

### Running the Environment (Programmatically)
```python
from client import PullRequestEnv
from models import ReviewAction

env = PullRequestEnv()
obs = env.reset(task_id="7")

print(f"Reviewing PR: {obs.pr_title}")

action = ReviewAction(type="request_changes", comment="Found an unparameterized SQL Injection in the diff.")
next_obs = env.step(action)

print(f"Reward received: {next_obs.reward}")
```

### Running Baseline Inference
We provide a baseline inference script using the OpenAI client spec to evaluate open-weights models (via HuggingFace) or direct OpenAI models. 
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
export HF_TOKEN="your_hf_token"

python inference.py
```

## 🏗️ Architecture
This environment flawlessly complies with the **OpenEnv multi-node specification**:
- Standardized `pyproject.toml` definition.
- Native `app.py` wrapper operating on `FastAPI` runtime.
- Dedicated `Dockerfile` mapping to HuggingFace Spaces requirements.
- Strictly deterministic, clipped grading `[0.01, 0.99]` algorithms enforcing proportional AI commentary evaluation.
