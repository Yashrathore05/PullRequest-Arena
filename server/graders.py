try:
    from ..models import ReviewAction
except ImportError:
    from models import ReviewAction

def _clip(score: float) -> float:
    return max(0.01, min(0.99, score))

def _get_action_match(action: ReviewAction, expected: str) -> float:
    if action.type == "approve":
        return 0.0
    if action.type == expected:
        return 1.0
    if action.type == "submit_patch" and expected in ["request_changes", "suggest_fix", "submit_patch"]:
        return 1.0
    if action.type == "comment":
        return 0.5
    # If they use suggest_fix instead of request_changes or vice versa, still give partial/full credit
    return 0.5

def _get_keyword_quality(action: ReviewAction, keywords: list) -> float:
    comment = action.comment.lower()
    hits = sum(1 for kw in keywords if kw.lower() in comment)
    if hits >= 2:
        return 1.0
    if hits == 1:
        return 0.5
    return 0.0

def _base_grade(action: ReviewAction, task: dict) -> float:
    action_match = _get_action_match(action, task.get("expected_action", "request_changes"))
    keyword_quality = _get_keyword_quality(action, task.get("keywords", []))
    
    # If the agent attempts a patch, award bonus points if the patch is decent
    patch_score = 0.0
    if action.type == "submit_patch" and action.patch:
        patch = action.patch.strip()
        expected_patch = task.get("expected_patch", "")
        if expected_patch and expected_patch in patch:
            patch_score = 1.0
        elif len(patch) > 5:
            patch_score = 0.5
            
    raw = (0.5 * action_match) + (0.3 * keyword_quality) + (0.2 * patch_score)
    return raw

def grade_task_1(action: ReviewAction, task: dict) -> float:
    return _clip(_base_grade(action, task))

def grade_task_2(action: ReviewAction, task: dict) -> float:
    return _clip(_base_grade(action, task))

def grade_task_3(action: ReviewAction, task: dict) -> float:
    return _clip(_base_grade(action, task))

def grade_task_4(action: ReviewAction, task: dict) -> float:
    return _clip(_base_grade(action, task))

def grade_task_5(action: ReviewAction, task: dict) -> float:
    return _clip(_base_grade(action, task))

def grade_task_6(action: ReviewAction, task: dict) -> float:
    return _clip(_base_grade(action, task))

def grade_task_7(action: ReviewAction, task: dict) -> float:
    if action.type == "approve":
        return 0.01
        
    comment = action.comment.lower()
    action_match = _get_action_match(action, task.get("expected_action", "request_changes"))
    
    if "sql injection" in comment and ("description" in comment or "misleading" in comment):
        keyword_quality = 1.0
    else:
        keyword_quality = _get_keyword_quality(action, task.get("keywords", []))
        
    raw = (0.6 * action_match) + (0.4 * keyword_quality)
    return _clip(raw)

def grade_task_8(action: ReviewAction, task: dict) -> float:
    comment = action.comment.lower()
    action_match = _get_action_match(action, task.get("expected_action", "request_changes"))
    
    if ("logging" in comment or "log" in comment) and "card" in comment:
        keyword_quality = 1.0
    else:
        keyword_quality = 0.0
        
    raw = (0.6 * action_match) + (0.4 * keyword_quality)
    return _clip(raw)

def grade_task_9(action: ReviewAction, task: dict) -> float:
    comment = action.comment.lower()
    action_match = _get_action_match(action, task.get("expected_action", "request_changes"))
    
    keyword_quality = _get_keyword_quality(action, task.get("keywords", []))
    
    if "config.py" in comment:
        action_match = 1.0
    elif "middleware.py" in comment:
        keyword_quality = 0.0
        
    raw = (0.6 * action_match) + (0.4 * keyword_quality)
    return _clip(raw)

def route_grader(task_id: str, action: ReviewAction, task: dict) -> float:
    graders = {
        "1": grade_task_1,
        "2": grade_task_2,
        "3": grade_task_3,
        "4": grade_task_4,
        "5": grade_task_5,
        "6": grade_task_6,
        "7": grade_task_7,
        "8": grade_task_8,
        "9": grade_task_9,
    }
    grader_func = graders.get(str(task_id))
    if grader_func:
        return grader_func(action, task)
    return _clip(_base_grade(action, task))
