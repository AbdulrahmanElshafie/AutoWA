# Analytics System

## Overview
The Analytics Module (`analyzer.py`) consumes the `execution_log.jsonl` stream to calculate runtime KPIs for the WhatsApp automation application. Because it processes `.jsonl` files iteratively, it features low-memory, O(1) space footprint processing compared to loading fully serialized traditional JSON.

## Core Features
- **File Parsing:** `load_logs(file_path)` parses raw JSON-Lines to dictionaries.
- **KPI Generation:** Extracts aggregate values:
  - Total Messages sent
  - Processing Throughput (msg/min) calculated per-session, including averages across all sessions, current session, and last session.
  - Success Rates (successful / total actions)
  - Average execution time per cycle.

## Integration
This module provides a pure-dictionary return object (`get_full_analytics`) designed specifically for presentation through the `gui_integration_example.py` frontend tabs.
