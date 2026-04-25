# Monitoring & Health System

## Overview
The Monitoring Module (`health.py`) is tasked with assessing the functional health of the system during runtime. Unlike crash loops that simply end execution, the health module grades execution resilience and provides graded states (`HEALTHY`, `WARNING`, `CRITICAL`) using recent sliding windows of activity.

## Health Score Math
The system operates from a baseline score of `100` and scans the most recent log operations (sliding window size of up to 100 entries).
- **Minor Errors (-5 Penalties):** Disconnected or unclassified errors that happened singularly.
- **Repeated Errors (-15 Penalties):** Any subset sequence where the **same** error happened three or more times in a row, implying logic loops rather than one-off UI spikes.
- **Critical Errors (-40 Penalties):** Events defined in `CRITICAL_TYPES` (e.g. `FATAL_ERROR`, `BROWSER_CRASH`) heavily dock the score immediately.

## Application Use
The functions `calculate_health_score(logs)` and `get_system_health(logs)` act together to summarize isolated severity instances alongside an overall integer output. Alerts on the UI dynamically shift between green, orange, or red accordingly.
