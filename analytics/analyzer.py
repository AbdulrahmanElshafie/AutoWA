import json
import os
from datetime import datetime

LOG_FILE = "logs/execution_log.jsonl"

def load_logs(file_path=LOG_FILE):
    """Loads logs from a .jsonl file."""
    logs = []
    if not os.path.exists(file_path):
        return logs
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs

def get_total_messages(logs):
    return sum(1 for log in logs if log.get("action") == "send_message")

def get_success_rate(logs):
    if not logs:
        return 0.0
    success_count = sum(1 for log in logs if log.get("status") == "success")
    return round((success_count / len(logs)) * 100, 2)

def get_failure_count(logs):
    return sum(1 for log in logs if log.get("status") == "failed")

def get_average_duration(logs):
    if not logs:
        return 0.0
    total_duration = sum(log.get("duration", 0) for log in logs)
    return round(total_duration / len(logs), 2)

def get_messages_per_minute(logs):
    send_logs = [log for log in logs if log.get("action") == "send_message"]
    if not send_logs:
        return {"avg_all": 0.0, "avg_last_session": 0.0, "avg_current_session": 0.0}
    
    sessions = {}
    for log in send_logs:
        session_id = log.get("session_id", "default")
        sessions.setdefault(session_id, []).append(log)
    
    def calculate_throughput(session_logs):
        if not session_logs:
            return 0.0
        try:
            start_time = datetime.fromisoformat(session_logs[0]["timestamp"])
            end_time = datetime.fromisoformat(session_logs[-1]["timestamp"])
            minutes_diff = (end_time - start_time).total_seconds() / 60.0
            
            if minutes_diff <= 0:
                return len(session_logs)
                
            return round(len(session_logs) / minutes_diff, 2)
        except (ValueError, KeyError):
            return 0.0

    session_throughputs = [calculate_throughput(logs) for logs in sessions.values()]
    avg_all = round(sum(session_throughputs) / len(session_throughputs), 2) if session_throughputs else 0.0
    
    session_ids = list(sessions.keys())
    # Assuming sessions are appended in order, last one is current
    current_session = sessions[session_ids[-1]]
    avg_current_session = calculate_throughput(current_session)
    
    avg_last_session = 0.0
    if len(session_ids) > 1:
        last_session = sessions[session_ids[-2]]
        avg_last_session = calculate_throughput(last_session)
    
    return {
        "avg_all": avg_all,
        "avg_last_session": avg_last_session,
        "avg_current_session": avg_current_session
    }

def get_full_analytics(file_path=LOG_FILE):
    logs = load_logs(file_path)
    return {
        "total": len(logs),
        "total_messages": get_total_messages(logs),
        "success_rate": get_success_rate(logs),
        "failures": get_failure_count(logs),
        "avg_duration": get_average_duration(logs),
        "throughput": get_messages_per_minute(logs)
    }

