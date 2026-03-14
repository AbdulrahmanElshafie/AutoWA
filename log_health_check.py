import re
import sys
from collections import defaultdict
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

LOG_FILE = "logs/error.log"

# ---------------- REGEX ----------------
ERROR_HEADER = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ERROR \| EXCEPTION in (?P<func>\w+)"
)
DURATION_RE = re.compile(r"duration=(\d+\.\d+)s")

# ---------------- ROOT CAUSE CLASSIFIER ----------------
def classify_root_cause(text: str) -> str:
    text = text.lower()

    if "imagenotfoundexception" in text:
        return "UI_AUTOMATION::IMAGE_NOT_FOUND"

    if "unboundlocalerror" in text:
        return "CODE_BUG::UNINITIALIZED_VARIABLE"

    if "failsafeexception" in text:
        return "ENVIRONMENT::PYAUTOGUI_FAILSAFE"

    if "invalid literal for int" in text:
        return "DATA::INVALID_PHONE_NUMBER"

    if "nonetype" in text:
        return "CODE_BUG::NONE_OBJECT"

    return "UNKNOWN::OTHER"

# ---------------- PARSER ----------------
errors = defaultdict(lambda: {
    "count": 0,
    "duration": 0.0,
    "functions": set(),
})

current = None
buffer = ""

with open(LOG_FILE, encoding="utf-8", errors="ignore") as f:
    for line in f:
        header = ERROR_HEADER.search(line)
        if header:
            if current:
                root = classify_root_cause(buffer)
                errors[root]["count"] += 1
                errors[root]["duration"] += current["duration"]
                errors[root]["functions"].add(current["func"])

            current = {
                "func": header["func"],
                "duration": 0.0,
            }
            buffer = ""

        dur = DURATION_RE.search(line)
        if dur and current:
            current["duration"] = float(dur.group(1))

        buffer += line

# flush last
if current:
    root = classify_root_cause(buffer)
    errors[root]["count"] += 1
    errors[root]["duration"] += current["duration"]
    errors[root]["functions"].add(current["func"])

# ---------------- DATAFRAME ----------------
df = pd.DataFrame([
    {
        "RootCause": k,
        "Occurrences": v["count"],
        "TimeLostSeconds": round(v["duration"], 2),
        "Functions": ", ".join(v["functions"]),
        "ImpactScore": v["count"] * max(1, v["duration"])
    }
    for k, v in errors.items()
]).sort_values("ImpactScore", ascending=False)

# ---------------- PARETO CHART ----------------
df["CumulativeImpact"] = df["ImpactScore"].cumsum()
df["CumulativePercent"] = 100 * df["CumulativeImpact"] / df["ImpactScore"].sum()

plt.figure(figsize=(10, 5))
plt.bar(df["RootCause"], df["ImpactScore"])
plt.plot(df["RootCause"], df["CumulativePercent"], color="red", marker="o")
plt.axhline(80, color="gray", linestyle="--")

plt.xticks(rotation=45, ha="right")
plt.ylabel("Impact Score")
plt.title("Pareto Chart – Error Root Causes")
plt.tight_layout()
plt.savefig("pareto_errors.png")
plt.close()

# ---------------- CI HEALTH CHECK ----------------
P0_THRESHOLD = 300        # critical impact
MAX_P0_ALLOWED = 0        # fail build if >0 P0 issues

df["Priority"] = pd.cut(
    df["ImpactScore"],
    bins=[-1, 10, 40, 100, float("inf")],
    labels=["P3", "P2", "P1", "P0"]
)

p0_count = (df["Priority"] == "P0").sum()

print("\n===== CI ERROR HEALTH REPORT =====\n")
print(df[["RootCause", "Priority", "Occurrences", "TimeLostSeconds", "Functions"]])

print("\nPareto chart saved as: pareto_errors.png")

if p0_count > MAX_P0_ALLOWED:
    print(f"\n❌ BUILD FAILED: {p0_count} P0 errors detected")
    sys.exit(1)

print("\n✅ BUILD PASSED: Error health acceptable")
sys.exit(0)

# ---------------- SAVE HEALTH ----------------
health_data = {
    "status": "PASS" if p0_count <= MAX_P0_ALLOWED else "FAIL",
    "p0": int((df["Priority"] == "P0").sum()),
    "p1": int((df["Priority"] == "P1").sum()),
    "p2": int((df["Priority"] == "P2").sum()),
    "p3": int((df["Priority"] == "P3").sum()),
    "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_errors": int(df["Occurrences"].sum())
}

top_errors = df.sort_values("ImpactScore", ascending=False).head(5)
health_data["top_errors"] = top_errors[["RootCause","Priority","Occurrences","TimeLostSeconds"]].to_dict(orient="records")


with open("health_report.json", "w", encoding="utf-8") as f:
    json.dump(health_data, f, indent=2)