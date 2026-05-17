import json
import os
from datetime import datetime

LOG_FILE = "logs/execution_log.jsonl"

def load_logs(file_path=LOG_FILE):
    """
    Loads execution logs line-by-line from a .jsonl file.
    
    Logic Flow:
    1. Verifies the log file exists at the given path.
    2. Opens the file and reads it line-by-line to avoid loading the entire file into memory at once.
    3. Attempts to parse each valid line as a JSON object.
    4. Ignores any malformed JSON lines silently (JSONDecodeError).
    5. Returns a list of dictionary log entries.
    """
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
    """
    Calculates the total number of message sending attempts.
    
    Logic Flow:
    Iterates through all logs and increments the count for any log where the "action" key is "send_message".
    """
    return sum(1 for log in logs if log.get("action") == "send_message")

def get_success_rate(logs):
    """
    Calculates the overall success rate of logged actions.
    
    Logic Flow:
    1. Returns 0.0 if the logs list is empty to prevent division by zero.
    2. Counts the number of logs where "status" equals "success".
    3. Computes the percentage of successes relative to total logs, rounded to 2 decimal places.
    """
    if not logs:
        return 0.0
    success_count = sum(1 for log in logs if log.get("status") == "success")
    return round((success_count / len(logs)) * 100, 2)

def get_failure_count(logs):
    """
    Calculates the total number of failed actions.
    
    Logic Flow:
    Iterates through all logs and increments the count for any log where the "status" key is "failed".
    """
    return sum(1 for log in logs if log.get("status") == "failed")

def get_average_duration(logs):
    """
    Calculates the average duration of all logged actions.
    
    Logic Flow:
    1. Returns 0.0 if the logs list is empty.
    2. Sums the "duration" field across all log entries (defaulting to 0 if missing).
    3. Divides the total duration by the number of logs, rounded to 2 decimal places.
    """
    if not logs:
        return 0.0
    total_duration = sum(log.get("duration", 0) for log in logs)
    return round(total_duration / len(logs), 2)

def get_messages_per_minute(logs):
    """
    Calculates message processing throughput (messages per minute).
    
    Logic Flow:
    1. Filters logs to include only "send_message" actions.
    2. Groups the filtered logs into distinct sessions based on their "session_id".
    3. For each session, calculates throughput by taking the total number of messages 
       and dividing it by the time elapsed between the first and last message.
    4. Computes the average throughput across all historical sessions.
    5. Extracts the throughput specifically for the most recent ("current") session 
       and the one directly preceding it ("last" session).
    6. Returns a dictionary containing these three throughput metrics.
    """
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
    """
    Aggregates all KPIs into a single dictionary payload.
    
    Logic Flow:
    1. Loads the latest logs from the specified JSONL file path.
    2. Runs all individual KPI helper functions on the loaded logs.
    3. Returns a consolidated dictionary used by the GUI to populate the dashboard.
    """
    logs = load_logs(file_path)
    return {
        "total": len(logs),
        "total_messages": get_total_messages(logs),
        "success_rate": get_success_rate(logs),
        "failures": get_failure_count(logs),
        "avg_duration": get_average_duration(logs),
        "throughput": get_messages_per_minute(logs)
    }

