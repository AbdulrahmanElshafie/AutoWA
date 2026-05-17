# Icons Management & UI Recovery System

## Overview
Due to changing UI elements in WhatsApp and browsers (dark/light mode shifting, icon updates, scaling anomalies), this module (`icons_management`) acts to freeze, capture, and restore UI elements gracefully. It provides both an engine to capture full-screen snapshots when elements fail to load, and a GUI tab for managing and recovering these elements.

## Features
- **Usage Icons Management:** Allows users to browse all known icons and their respective image variants inside the `assets/icons/` directory. Unwanted or obsolete variants can be easily deleted from the interface.
- **UI Recovery Queue:** When the automation engine (`Controller.py`) fails to find a specific UI element natively, it automatically saves a snapshot of the failure state. The recovery queue allows users to visually review these snapshots and crop out the new UI element.

## Workflow
1. **Detection:** When `pyautogui.locateOnScreen` fails to match an existing asset natively in the app, a `UIElementNotFound` exception forces a snapshot via `save_failure_snapshot(element_name)`.
2. **Snapshot Creation:** A full screenshot is dumped into `assets/review_queue/` with a timestamp. 
3. **Queue Processing:** The "UI Recovery Queue" tab lists all failed items awaiting user inspection.
4. **Resolution via Cropping:** The user visually draws a bounding box over the desired element within the provided canvas.
5. **Save to Icon:** Once an accurate crop is made, the user specifies the target icon name and saves it. The system handles extracting the crop using `PIL` and moves the new variant into `assets/icons/{icon_name}/`, while deleting the original failure snapshot from the review queue.

## Core Dependencies
- Uses `pyautogui` for screen scraping and creating failure snapshots.
- Uses `Pillow` (`PIL`) for extracting cropped image data.
- Standard `os` and `shutil` mechanisms are used for directory and file manipulations, avoiding heavyweight external Computer Vision environments (e.g. OpenCV).
