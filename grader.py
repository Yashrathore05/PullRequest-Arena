"""
grader.py — Deterministic Grading Logic for PullRequest Arena

Evaluates agent review actions against expected solutions.
Produces scores between 0.0 and 1.0.

Scoring:
    - Correct action type + relevant keywords in comment  → 1.0
    - Correct action type + partial keyword match          → 0.7
    - Correct action type, no keyword match                → 0.5
    - Partially related action type                        → 0.3
    - Wrong action type entirely                           → 0.0
"""

# Action types that are considered partially related.
# e.g., "comment" is partial credit when "request_changes" was expected.
PARTIAL_CREDIT_MAP = {
    "request_changes": ["comment", "suggest_fix"],
    "suggest_fix": ["comment", "request_changes"],
    "comment": ["request_changes", "suggest_fix"],
    "approve": [],
}

# Minimum fraction of expected keywords that must match for full keyword credit.
FULL_KEYWORD_THRESHOLD = 0.4
# Minimum fraction for partial keyword credit.
PARTIAL_KEYWORD_THRESHOLD = 0.15


def _normalize_text(text: str) -> str:
    """Lowercase and strip text for keyword matching."""
    return text.lower().strip()


def _compute_keyword_score(comment: str, expected_keywords: list[str]) -> float:
    """
    Compute a keyword match score between 0.0 and 1.0.

    Checks how many expected keywords appear in the agent's comment.
    Returns:
        1.0  if >= FULL_KEYWORD_THRESHOLD fraction of keywords found
        0.5  if >= PARTIAL_KEYWORD_THRESHOLD fraction found
        0.0  otherwise
    """
    if not expected_keywords or not comment:
        return 0.0

    normalized_comment = _normalize_text(comment)
    matches = sum(
        1 for kw in expected_keywords
        if _normalize_text(kw) in normalized_comment
    )

    match_ratio = matches / len(expected_keywords)

    if match_ratio >= FULL_KEYWORD_THRESHOLD:
        return 1.0
    elif match_ratio >= PARTIAL_KEYWORD_THRESHOLD:
        return 0.5
    return 0.0


def grade(action: dict, task: dict) -> float:
    """
    Grade an agent's review action against the expected solution.

    Args:
        action: Agent's action dict with keys:
            - "type"    (str): One of "approve", "request_changes",
                               "comment", "suggest_fix"
            - "comment" (str): The agent's review comment
        task: Task dict from tasks.json with keys:
            - "expected_action"   (str) : Correct action type
            - "expected_keywords" (list): Keywords for comment quality

    Returns:
        float: Reward score between 0.0 and 1.0

    Scoring breakdown:
        - action_score (60% weight): Based on action type match
        - keyword_score (40% weight): Based on comment keyword match

    The scores are combined as:
        reward = (action_score * 0.6) + (keyword_score * 0.4)
    """
    action_type = action.get("type", "").strip().lower()
    comment = action.get("comment", "")
    expected_action = task.get("expected_action", "").strip().lower()
    expected_keywords = task.get("expected_keywords", [])

    # --- Action type scoring ---
    if action_type == expected_action:
        action_score = 1.0
    elif action_type in PARTIAL_CREDIT_MAP.get(expected_action, []):
        action_score = 0.5
    else:
        # Completely wrong action (e.g., approving buggy code)
        # No keyword credit either — early return 0.0
        return 0.0

    # --- Keyword scoring ---
    keyword_score = _compute_keyword_score(comment, expected_keywords)

    # --- Composite reward ---
    reward = (action_score * 0.6) + (keyword_score * 0.4)

    # Clamp to [0.0, 1.0]
    return round(min(max(reward, 0.0), 1.0), 2)
