from dataclasses import dataclass
from typing import List, Dict

@dataclass
class AutomationError:
    type: str
    severity: str  # LOW, MEDIUM, CRITICAL
    message: str

def detect_repeated_errors(logs: List[Dict]) -> List[AutomationError]:
    """Identify if the same error type repeats consecutively."""
    repeated_errors = []
    if not logs:
        return repeated_errors
    
    last_error_type = None
    repeat_count = 0
    
    # Analyze recent 50 logs for repeated sequences
    recent_logs = logs[-50:]
    for log in recent_logs:
        if log.get("status") == "failed" and log.get("error_type"):
            current_error = log.get("error_type")
            if current_error == last_error_type:
                repeat_count += 1
                if repeat_count == 3:  # 3 in a row is a repeated error
                    repeated_errors.append(AutomationError(
                        type=current_error,
                        severity="MEDIUM",
                        message=f"Repeated error detected: {current_error}"
                    ))
                if repeat_count == 5:
                    err = repeated_errors.pop()
                    err.severity = "CRITICAL"
                    repeated_errors.append(err)
            else:
                last_error_type = current_error
                repeat_count = 1
        else:
            last_error_type = None
            repeat_count = 0
            
    return repeated_errors

def detect_critical_failures(logs: List[Dict]) -> List[AutomationError]:
    """Identify critical errors like full system crashes, disconnections."""
    critical_errors = []
    if not logs:
        return critical_errors

    CRITICAL_TYPES = ["DISCONNECTED", "BROWSER_CRASH", "FATAL_ERROR", "SYSTEM_HALT"]
    
    for log in logs[-20:]:  # Check recent window
        if log.get("status") == "failed" and log.get("error_type") in CRITICAL_TYPES:
            critical_errors.append(AutomationError(
                type=log["error_type"],
                severity="CRITICAL",
                message=f"Critical failure detected: {log['error_type']}"
            ))
            
    return critical_errors

def detect_minor_errors(logs: List[Dict], repeated_errors: List[AutomationError], critical_errors: List[AutomationError]) -> List[AutomationError]:
    """Identify minor errors, which are any errors not in repeated or critical lists."""
    if not logs:
        return []
    
    repeated_types = {err.type for err in repeated_errors}
    critical_types = {err.type for err in critical_errors}
    
    minor_errors = []
    
    for log in logs:
        if log.get("status") == "failed" and log.get("error_type"):
            err_type = log.get("error_type")
            if err_type not in repeated_types and err_type not in critical_types:
                minor_errors.append(AutomationError(
                    type=err_type,
                    severity="LOW",
                    message=f"Minor error detected: {err_type}"
                ))
    return minor_errors

def calculate_health_score(logs: List[Dict]) -> int:
    score = 100
    if not logs:
        return score
    
    # Assess recent window to determine current health
    recent_logs = logs[-100:] if len(logs) > 100 else logs
    
    repeated = detect_repeated_errors(recent_logs)
    critical = detect_critical_failures(recent_logs)
    minor = detect_minor_errors(recent_logs, repeated, critical)
    
    score -= (len(critical) * 40)
    score -= (len(repeated) * 15)
    score -= (len(minor) * 5)
    
    return max(0, min(100, score))  # Clamp between 0 and 100

def get_health_status(score: int) -> str:
    if score >= 80:
        return ('HEALTHY', '#00FF00')
    elif score >= 50:
        return ('WARNING', '#FFB347')
    else:
        return ('CRITICAL', '#FF6666')

def get_system_health(logs: List[Dict]) -> Dict:
    score = calculate_health_score(logs)
    status, color = get_health_status(score)
    return {
        "score": score,
        "status": status,
        "color": color,
        "repeated_issues": [err.__dict__ for err in detect_repeated_errors(logs)],
        "critical_issues": [err.__dict__ for err in detect_critical_failures(logs)]
    }
