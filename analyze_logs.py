import re
from collections import defaultdict
from datetime import datetime

LOG_FILE = "logs/error.log"   # <-- change to your log file path


ERROR_HEADER_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ERROR \| EXCEPTION in (?P<func>\w+)"
)
DURATION_RE = re.compile(r"duration=(\d+\.\d+)s")
EXCEPTION_RE = re.compile(r"(\w+Error|\w+Exception): (.+)")


def normalize_error(msg: str) -> str:
    """
    Normalize errors so similar ones are grouped together
    """
    if "ImageNotFoundException" in msg:
        icon = re.findall(r"ايكونة: (.+)", msg)
        return f"ImageNotFoundException::{icon[0] if icon else 'UNKNOWN'}"

    if "UnboundLocalError" in msg:
        return "UnboundLocalError::bug"

    if "FailSafeException" in msg:
        return "PyAutoGUI::FailSafeException"

    if "ValueError" in msg and "invalid literal for int" in msg:
        return "ValueError::InvalidPhoneNumber"

    return msg.split(":")[0]


def priority(score):
    if score >= 100:
        return "P0 🔥 (Critical)"
    if score >= 40:
        return "P1 🚨 (High)"
    if score >= 10:
        return "P2 ⚠️ (Medium)"
    return "P3 ℹ️ (Low)"


errors = defaultdict(lambda: {
    "count": 0,
    "functions": set(),
    "total_duration": 0.0,
    "first_seen": None,
    "last_seen": None,
})

current_error = None
current_msg = ""

with open(LOG_FILE, encoding="utf-8", errors="ignore") as f:
    for line in f:
        header = ERROR_HEADER_RE.search(line)
        if header:
            if current_error:
                key = normalize_error(current_msg)
                data = errors[key]
                data["count"] += 1
                data["functions"].add(current_error["func"])
                data["total_duration"] += current_error["duration"]
                data["first_seen"] = min(data["first_seen"], current_error["ts"]) if data["first_seen"] else current_error["ts"]
                data["last_seen"] = max(data["last_seen"], current_error["ts"]) if data["last_seen"] else current_error["ts"]

            current_error = {
                "ts": datetime.strptime(header["ts"], "%Y-%m-%d %H:%M:%S"),
                "func": header["func"],
                "duration": 0.0,
            }
            current_msg = ""

        dur = DURATION_RE.search(line)
        if dur and current_error:
            current_error["duration"] = float(dur.group(1))

        exc = EXCEPTION_RE.search(line)
        if exc:
            current_msg += exc.group(0) + " "

    # flush last
    if current_error:
        key = normalize_error(current_msg)
        data = errors[key]
        data["count"] += 1
        data["functions"].add(current_error["func"])
        data["total_duration"] += current_error["duration"]
        data["first_seen"] = current_error["ts"]
        data["last_seen"] = current_error["ts"]


# ------------------ REPORT ------------------

print("\n===== ERROR INSIGHTS REPORT =====\n")

ranked = []
for err, d in errors.items():
    impact_score = d["count"] * max(1, d["total_duration"])
    ranked.append((impact_score, err, d))

ranked.sort(reverse=True)

for score, err, d in ranked:
    print(f"Error Type : {err}")
    print(f"Priority   : {priority(score)}")
    print(f"Occurrences: {d['count']}")
    print(f"Functions  : {', '.join(d['functions'])}")
    print(f"Time Lost  : {d['total_duration']:.2f}s")
    print(f"First Seen : {d['first_seen']}")
    print(f"Last Seen  : {d['last_seen']}")
    print("-" * 50)
