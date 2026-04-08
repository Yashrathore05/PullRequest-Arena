---
title: PullRequest Arena
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---
<<<<<<< HEAD
# PullRequest Arena

**An OpenEnv Environment for AI Code Review Training & Evaluation**

PullRequest Arena is an OpenEnv-compatible reinforcement learning environment that simulates a real-world GitHub pull request code review workflow. An AI agent acts as a code reviewer — receiving pull request descriptions and code diffs, identifying bugs and issues, and taking structured review actions. The environment scores each review based on correctness and comment quality, providing meaningful reward signals for training and benchmarking AI code review agents.

---

## Motivation

Code review is one of the most time-consuming and cognitively demanding tasks in software engineering. Studies show that developers spend **up to 6 hours per week** reviewing code, and even experienced reviewers miss bugs at measurable rates.

AI-powered code review has the potential to:

- **Catch bugs earlier** — detect syntax errors, logical flaws, and security vulnerabilities before they reach production.
- **Enforce consistency** — apply style guidelines and best practices uniformly across large codebases.
- **Reduce reviewer fatigue** — allow human reviewers to focus on high-level architectural decisions rather than line-by-line inspection.
- **Accelerate development** — provide instant feedback to developers without waiting for human reviewer availability.

PullRequest Arena provides a **structured, reproducible environment** for training and evaluating AI agents on these code review tasks, with deterministic grading and increasing difficulty levels.

---

## Observation Space

Each observation represents a pull request that the agent must review. Observations are structured JSON objects with the following fields:

| Field | Type | Description |
|---|---|---|
| `pr_title` | `string` | Title of the pull request |
| `pr_description` | `string` | Description explaining the purpose and changes |
| `files_changed` | `array[string]` | List of filenames modified in the PR |
| `code_diff` | `string` | The code diff the agent must review |
| `language` | `string` | Programming language (`python`, `javascript`, etc.) |
| `tests_passed` | `boolean` | Whether the existing test suite passes |
| `repository_context` | `string` | Additional context about the repository and module |

**Example observation:**

```json
{
  "pr_title": "Fix login validation",
  "pr_description": "Updated the login function to check user credentials before granting access.",
  "files_changed": ["auth.py"],
  "code_diff": "def login(user, password):\n    if password = user.password:\n        return True\n    return False",
  "language": "python",
  "tests_passed": false,
  "repository_context": "Flask web application with user authentication module."
}
```

---

## Action Space

Actions represent the reviewer's decision. Each action is a JSON object with two required fields:

| Field | Type | Values | Description |
|---|---|---|---|
| `type` | `string` | `approve`, `request_changes`, `comment`, `suggest_fix` | The review decision |
| `comment` | `string` | Free-text | Explanation of the issue or suggestion |

### Action Types

| Action | When to Use |
|---|---|
| `approve` | Code is correct and ready to merge |
| `request_changes` | Code has bugs, errors, or security issues that must be fixed |
| `comment` | Leave a question or observation about the code |
| `suggest_fix` | Propose a specific code improvement or refactoring |

**Example action:**

```json
{
  "type": "request_changes",
  "comment": "The if condition uses assignment (=) instead of comparison (==). This will cause a SyntaxError."
}
```

---

## Tasks

PullRequest Arena includes **6 tasks** across three difficulty levels, simulating realistic code review scenarios.

### Easy

| ID | Title | Bug Type | Expected Action |
|---|---|---|---|
| 1 | Fix login validation | Assignment instead of comparison (`=` vs `==`) | `request_changes` |
| 4 | Add null check for user profile | Identity check (`== None` vs `is None`) | `suggest_fix` |

### Medium

| ID | Title | Bug Type | Expected Action |
|---|---|---|---|
| 2 | Add role-based access control | Truthy string in boolean expression (always `True`) | `request_changes` |
| 5 | Implement secure password hashing | Insecure hash algorithm (MD5 for passwords) | `request_changes` |

### Hard

| ID | Title | Bug Type | Expected Action |
|---|---|---|---|
| 3 | Refactor data processing loop | Non-Pythonic `range(len())` pattern | `suggest_fix` |
| 6 | Add database connection handler | Resource leak + SQL injection vulnerability | `request_changes` |

---

## Reward Function

Rewards are **deterministic** and normalized between **0.0** and **1.0**.

The score is a weighted composite of:

- **Action type match (60%)** — Did the agent choose the correct action?
- **Comment quality (40%)** — Does the comment mention relevant keywords?

| Scenario | Score |
|---|---|
| Correct action + relevant keywords | **1.0** |
| Correct action + partial keyword match | **0.8** |
| Correct action, no keyword match | **0.6** |
| Partially related action (e.g., `comment` instead of `request_changes`) | **0.3** |
| Wrong action (e.g., `approve` on buggy code) | **0.0** |

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker (optional, for container deployment)

### Local Setup

```bash
# Clone the repository
git clone <repository-url>
cd pullrequest-arena

# Install dependencies
pip install -r requirements.txt

# Start the environment server
python env.py
```

The server starts on `http://localhost:7860`.

### Docker Setup

```bash
# Build the container
docker build -t pullrequest-arena .

# Run the container
docker run -p 7860:7860 pullrequest-arena
```

### Verify Installation

```bash
# Health check
curl http://localhost:7860/health

# List tasks
curl http://localhost:7860/tasks
```

---

## Running Inference

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_BASE_URL` | Yes | Base URL for an OpenAI-compatible API endpoint |
| `MODEL_NAME` | Yes | Model identifier (e.g., `gpt-4`, `codellama`) |
| `HF_TOKEN` | No | HuggingFace / API token for authentication |

### Run the Baseline Agent

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4"
export HF_TOKEN="your-token-here"

python inference.py
```

### Logging Format

The inference script logs output in the strict OpenEnv format:

```
[START] task=1 env=pullrequest-arena model=gpt-4
[STEP] step=1 action={"type":"request_changes","comment":"Use == not ="} reward=1.0 done=true error=null
[END] success=true steps=1 score=1.00 rewards=1.0
```

---

## API Endpoints

When running as an HTTP server, the following endpoints are available:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Landing page with API information |
| `POST` | `/reset` | Reset environment, returns initial observation |
| `POST` | `/step` | Submit review action, returns reward |
| `GET` | `/state` | Get current environment state |
| `GET` | `/health` | Health check |
| `GET` | `/tasks` | List all task summaries |

### Example: Full Review Cycle

```bash
# 1. Reset (start a new review)
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_index": 0}'

# 2. Submit review action
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"type": "request_changes", "comment": "Use == instead of ="}}'

# 3. Check state
curl http://localhost:7860/state
```

---

## Python API Usage

```python
from env import PullRequestArenaEnv

env = PullRequestArenaEnv()

# Reset to get a PR observation
observation = env.reset(task_index=0)
print(observation["pr_title"])    # "Fix login validation"
print(observation["code_diff"])   # "if password = user.password:"

# Submit a review action
action = {
    "type": "request_changes",
    "comment": "Use == comparison operator instead of = assignment"
}
observation, reward, done, info = env.step(action)
print(f"Reward: {reward}")  # 1.0
print(f"Done: {done}")      # True

# Check environment state
state = env.state()
print(state["review_status"])  # "completed"
```

---

## Baseline Results

Scores from running the baseline inference agent across all tasks:

| Task | Difficulty | PR Title | Expected Action | Baseline Score |
|---|---|---|---|---|
| 1 | Easy | Fix login validation | `request_changes` | 1.0 |
| 2 | Medium | Add role-based access control | `request_changes` | 1.0 |
| 3 | Hard | Refactor data processing loop | `suggest_fix` | 1.0 |
| 4 | Easy | Add null check for user profile | `suggest_fix` | 0.8 |
| 5 | Medium | Implement secure password hashing | `request_changes` | 0.8 |
| 6 | Hard | Add database connection handler | `request_changes` | 0.8 |

**Average baseline score: 0.90**

> Baseline scores are from a correct-action agent with partial keyword matching. Actual LLM agent scores will vary based on model capability and prompt quality.

---

## Project Structure

```
pullrequest-arena/
├── env.py              # Core OpenEnv environment (reset, step, state + HTTP server)
├── tasks.json          # Task dataset (6 tasks, 3 difficulty levels)
├── grader.py           # Deterministic grading logic (0.0–1.0)
├── inference.py        # Baseline inference script (OpenAI client)
├── openenv.yaml        # OpenEnv metadata & schema definitions
├── Dockerfile          # Container build for deployment
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Runtime Constraints

- Inference script completes in under **20 minutes**
- Tested on machines with **2 vCPU / 8GB RAM**

---

## License

MIT
=======
---
title: Pullrequest Arena
emoji: 📉
colorFrom: red
colorTo: pink
sdk: docker
pinned: false
license: mit
short_description: OpenEnv Environment for AI Code Review Training & Evaluation
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
>>>>>>> cb8e8e74c95250b25e15cff62f8dd97a2279436d
