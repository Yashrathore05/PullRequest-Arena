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
**An OpenEnv Reinforcement Learning Environment for AI Software Engineers**

[![OpenEnv Compatible](https://img.shields.io/badge/OpenEnv-Compatible-blue.svg)](https://github.com/openenv/openenv)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HuggingFace Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Deployed-green)](https://huggingface.co/spaces/YashR05/pullrequest-arena)

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmVhMjFkZjMwZjZjMzcxNzZjMjJhZTk1YmZmZGZlMzFkMjhkZjQ0YiZjdD1n/L1R1tvI9svkGcmmCMG/giphy.gif" alt="Code Review Demo" width="600"/>
</p>

[Quickstart](#-quickstart) •
[The Challenge](#-the-challenge) •
[Architecture](#-architecture) •
[Benchmarking](#-benchmarking)

</div>

---

## 🎯 Overview

**PullRequest Arena** is a production-ready [OpenEnv](https://github.com/openenv/openenv) reinforcement learning environment simulating a real-world enterprise Code Review workflow. It is explicitly designed to benchmark AI agents (LLMs) on their ability to act as senior software engineers by reviewing Pull Requests, analyzing complex diffs, and identifying critical programmatic vulnerabilities.

Unlike algorithmic tests (e.g., HumanEval), **PullRequest Arena heavily evaluates an agent's ability to resist deception**, parse organizational metadata, and write functional diff patches.

## 🚀 The Challenge

Agents are presented with deep context including:
- **Title & Description**
- **CI / Pipeline Logs**
- **Modified Source Tree**
- **Raw Code Diff**

The agent must output a strict JSON decision (`approve`, `request_changes`, `comment`, `suggest_fix`, `submit_patch`) alongside robust diagnostic commentary and, where applicable, the syntactically correct patched code.

### 🌟 Featured Benchmark Traps

We've meticulously engineered 9 deterministic tasks scaling from Easy to Hard:

1. 🪤 **The Deceptive PR (Task 7):** The PR description claims to "Just fix a minor documentation typo", but the diff covertly introduces a blatant SQL Injection pipeline. Will the AI trust the psychological manipulation of the description, or actually parse the code?
2. 🐟 **The Red Herring (Task 8):** A PR stuffed with 50 lines of suspicious looking (but perfectly safe) styling anti-patterns, hiding a single line PCI compliance violation (logging plaintext credit card numbers). Can the AI ignore the noise?
3. 🧩 **Multi-File Reasoning (Task 9):** A rate-limiting implementation where the deceptive function occurs in `middleware.py`, but the actual disabling semantic bug occurs in `config.py` (`RATE_LIMIT = 0`).

---

## ⚡ Quickstart

### Prerequisites
- Python 3.11+
- `openenv-core>=0.2.3`

### Installation

```bash
git clone https://github.com/Yashrathore05/PullRequest-Arena.git
cd PullRequest-Arena

# Install the environment and its dependencies
pip install -e .
```

---

## 💻 Programmatic Usage

Interact with the environment natively in Python using the strictly typed Pydantic schema:

```python
from server.pullrequest_environment import PullRequestEnvironment
from models import ReviewAction

# Initialize Local Environment
env = PullRequestEnvironment()
obs = env.reset(task_id="7")

print(f"Reviewing PR: {obs.pr_title}")
print(f"Diff Context:\n{obs.code_diff}")

# Agent formulates an action based on context
action = ReviewAction(
    type="request_changes", 
    comment="SECURITY: Found an unparameterized SQL Injection in the authentication controller."
)

# Observe the step outcome and normalized reward [0.01 -> 0.99]
next_obs = env.step(action)
print(f"Reward received: {next_obs.reward}")
```

---

## 📊 Benchmarking & Inference

We provide an automated analytical wrapper `benchmark.py` that hooks `inference.py` to evaluate your API-compatible LLMs. It executes across the entire task suite, aggressively grades responses deterministically, and formats a standardized ASCII leaderboard.

**Execute Benchmark:**
```bash
# Provide a valid HuggingFace Token or OpenAI API Key
export HF_TOKEN="your_hf_token"

# Run the OpenEnv benchmark evaluation
python benchmark.py --model Qwen/Qwen2.5-7B-Instruct
```

**Leaderboard Output:**
```text
==================================================
🏆 PULLREQUEST ARENA LEADERBOARD
==================================================
Model                     | Avg Score  | Completion
--------------------------------------------------
Qwen/Qwen2.5-7B-Instruct  | 0.84       | 1.0       
==================================================
```
*(Results are simultaneously appended to `results/benchmark_results.json`)*

---

## 🏗️ Architecture & Integration

This environment is fully verified against the **OpenEnv multi-node specification**:
- ✅ **`pyproject.toml`** standardized deployment structure (`project.scripts` securely mapped).
- ✅ **FastAPI + Gradio** dual routing natively mounted in `server/app.py`.
- ✅ **`openenv-core`** 0.2.3 compatible `GenericEnvClient` hooks.
- ✅ **Strict deterministic grading heuristics** (`[0.01, 0.99]`) evaluating multi-modal actions.

### Local Interactive UI
You can spin up the full HuggingFace Spaces Gradio GUI locally:
```bash
python -m server.app
```
Navigate to `http://0.0.0.0:8000` to review the environment dynamically via the browser!

---
*Built with ❤️ for the Meta & Scaler OpenEnv Hackathon.*
