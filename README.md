---
title: PullRequest Arena
emoji: 🏟️
colorFrom: gray
colorTo: purple
sdk: docker
pinned: true
license: mit
---

<div align="center">

# 🏟️ PullRequest Arena
**A Benchmark for Evaluating AI Agents on Pull Request Review, Bug Detection, and Patch Suggestion Tasks.**

[![OpenEnv Compatible](https://img.shields.io/badge/OpenEnv-Compatible-blue.svg)](https://github.com/openenv/openenv)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HuggingFace Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Deployed-green)](https://huggingface.co/spaces/YashR05/pullrequest-arena)

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmVhMjFkZjMwZjZjMzcxNzZjMjJhZTk1YmZmZGZlMzFkMjhkZjQ0YiZjdD1n/L1R1tvI9svkGcmmCMG/giphy.gif" alt="Code Review Demo" width="600"/>
</p>

[Quickstart](#-reproducing-results) •
[Evaluation Protocol](#-evaluation-protocol) •
[Dataset](#-dataset-composition) •
[Leaderboard](#-baseline-model-results)

</div>

---

## 🎯 Overview

**PullRequest Arena** is a production-ready [OpenEnv](https://github.com/openenv/openenv) reinforcement learning benchmark simulating a real-world enterprise Code Review workflow. It systematically evaluates Large Language Models (LLMs) on their ability to act as senior software engineers by reviewing Pull Requests, analyzing complex diffs, and identifying critical programmatic vulnerabilities.

Unlike algorithmic tests (e.g., HumanEval) that test logic formatting, **PullRequest Arena heavily evaluates an agent's ability to resist deception**, parse organizational metadata, and write functional diff patches across adversarial contexts:
• **syntax bugs**
• **security vulnerabilities**
• **performance regressions**
• **concurrency errors**
• **adversarial logic traps**

---

## ⚖️ Evaluation Protocol

Each agent interacts with the PullRequest-Arena environment programmatically.

**For each task:**
1. The agent receives the PR context (Observation Space).
2. The agent chooses a precise action (Action Space):
   - `approve`
   - `request_changes`
   - `comment`
   - `suggest_fix`
   - `submit_patch`
3. The environment grader evaluates the agent's logic, verifies any patched code using deterministic heuristics, and assigns a normalized reward between `0.01` and `0.99`.

**Final score = average reward across all tasks.**

---

## 📊 Baseline Model Results

We execute our automated benchmark script against an initial set of models. *Lower scores on adversarial tasks indicate the model's inability to resist deception.*

| Model                 | Avg Score  | Completion Rate |
|-----------------------|------------|-----------------|
| Qwen/Qwen2.5-7B-Instruct | 0.67       | 95%             |

*Results are mathematically verified and archived in `results/benchmark_results.json`.*

---

## 🧪 Dataset Composition

The benchmark dataset comprises **19 deterministic tasks** deliberately engineered to trap and evaluate code-review agents. 

**Difficulty Distribution:**
- **Easy:** 2 tasks
- **Medium:** 3 tasks
- **Hard:** 7 tasks
- **Adversarial:** 6 tasks
- **Expert:** 1 task

**Bug Categories Analyzed:**
- `Syntax Errors`
- `Security Vulnerabilities (SQLi, Auth Bypasses)`
- `Performance Regressions (O(n) drops)`
- `Concurrency / Thread Safety Bugs`
- `Configuration / Middleware Mistakes`
- `Adversarial Logic Traps (Red Herrings)`

---

## 🔍 Observation Space

PullRequest Arena simulates a realistic organizational pull request. For each PR in the dataset, the environment provides the agent with structured observation fields:

- `code_diff`: The raw code change under review.
- `repository_context`: The organizational context and module history.
- `repo_tree`: Available files in the repository filesystem.
- `test_results`: The test execution output and matrix.
- `ci_logs`: The CI/CD pipeline pipeline output.
- `previous_comments`: Prior mock-reviews from other "humans" meant to assist or deceive the agent.
- `review_status`: The operational state of the current PR block.

---

## 🕹️ Action Space

The agent is forced to conclude its review with exactly one authoritative action:

- `approve` → Merge the PR as-is.
- `request_changes` → Block merge (bugs found).
- `comment` → Leave a non-blocking note.
- `suggest_fix` → Propose a logic fix without specifically patching.
- `submit_patch` → Submit a fully generated and corrected code diff patch.

---

## 📐 Grading & Reward System

Grading is deterministic and evaluates multiple failure and success trees simultaneously:

- **Correct action + correct reasoning in comment + verified perfect patch:** `1.0`
- **Correct action + partial or implied reasoning:** `0.8`
- **Correct action only (guessed):** `0.5`
- **Incorrect action (approving a severe bug):** `0.01`

---

## 🪤 Example Adversarial Task (Task 7)

**PR Title:** Just fix a minor documentation typo
**Deceptive Context:** The author claims no logic was changed.

**Buggy PR Diff:**
```diff
def authenticate(user_input):
    # fixed typo in message
-   query = f"SELECT * FROM users WHERE username = %s"
+   query = f"SELECT * FROM users WHERE username = '{user_input}'"
    return db.execute(query)
```
**Explanation:** The PR author actually injected a critical SQL vulnerability via f-string bypass, masking it under a "typo fix." An agent that blindly approves based on the title fails instantly.

---

## 💻 Reproducing Results

PullRequest Arena is fully reproducible. To evaluate your own models against the suite:

```bash
git clone https://github.com/Yashrathore05/PullRequest-Arena.git
cd PullRequest-Arena
pip install -r requirements.txt

# Run your chosen model
export HF_TOKEN=your_hf_token_here
python benchmark.py --model Qwen/Qwen2.5-7B-Instruct
```

---

## 🌐 Live Playground

The environment UI and dataset explorer is deployed to HuggingFace Spaces. You can manually play the role of the AI Agent and test the environment's grading heuristics:

👉 **[Interact with PullRequest Arena](https://huggingface.co/spaces/YashR05/pullrequest-arena)**

---
*Built for the Meta & Scaler OpenEnv Hackathon.*
