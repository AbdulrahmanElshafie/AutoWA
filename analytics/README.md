# Analytics Dashboard System

## Overview
The Analytics Module (`analyzer.py`) consumes the `execution_log.jsonl` stream to calculate runtime Key Performance Indicators (KPIs) for the WhatsApp automation application. By processing `.jsonl` files line-by-line iteratively, it maintains a low-memory footprint, scaling efficiently as the log file grows over multiple sessions.

## Core Features
- **File Parsing:** `load_logs(file_path)` safely parses raw JSON-Lines to dictionaries, gracefully ignoring malformed entries.
- **KPI Generation:** Extracts critical aggregate values from the log data:
  - **Total Messages:** Total count of attempted `send_message` actions.
  - **Success & Failure Rates:** Calculates the percentage of actions that resolved successfully vs failed.
  - **Processing Throughput (msg/min):** Evaluates speed dynamically across multiple sessions. Calculates the all-time average, as well as specific throughputs for the current and immediately previous sessions.
  - **Average Duration:** Computes the mean execution time per cycle.

## GUI Integration
This module exposes a consolidated dictionary object (`get_full_analytics`) specifically designed to populate the visual components in `gui.py`. The `events.py` handler captures user requests to refresh the dashboard and maps these KPI values seamlessly into the layout.
