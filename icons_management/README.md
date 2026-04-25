# Self-Healing UI Recovery System

## Overview
Due to changing UI elements in WhatsApp and browsers (dark/light mode shifting, icon updates, scaling anomalies), this module (`ui_recovery.py`) acts to freeze, capture, and restore UI elements gracefully.

## Workflow
1. **Detection:** When `pyautogui.locateOnScreen` fails to match an existing asset natively in the app, a `UIElementNotFound` exception forces a snapshot.
2. **Snapshot Creation:** `save_failure_snapshot("element_name")` executes a full screenshot dumped into `assets/review_queue/`. 
3. **Queue Processing:** The `list_pending_recoveries()` function exposes all failed items awaiting user inspection.
4. **Resolution (`replace_ui_asset`):** When the user isolates and approves a correctly cropped new asset natively on the frontend:
   - The original/existing icon is retired recursively to `assets/history/element_name_v_YYYYMMDD_HHMM.png`.
   - The newly cropped view is injected as the baseline expectation.

## Core Dependencies
Uses strictly `pyautogui` for screen scraping and standard `shutil` mechanisms avoiding heavyweight external Computer Vision environments (e.g. OpenCV).
