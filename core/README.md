# Core Execution Engine

The `core` module is the foundation backend orchestrating your WhatsApp automation tasks asynchronously without enforcing direct UI locks.

## Key Files & Architecture

- **`runner.py`**: The main execution engine. It defines `execute_jobs`, looping over the entire dataset, managing multi-account switching, injecting natural delays to avoid bans, and making the underlying automation calls to `WAController.py`.
- **`job_model.py`**: A minimal data structure representing a single logical outbound transaction (`ContactJob`).
- **`job_loader.py`**: The bridge between physical storage (`CSV` files) and the Python models. Automatically rewrites statuses post-execution.
- **`validator.py`**: Enforces rules (e.g., stopping execution on empty payloads where both messages and docs are missing) before initializing the driver.

## Usage Note
The `core` is entirely decoupled from the PySimpleGUI components. It communicates with the UI purely through a passed `window` parameter (for event pumping) but can easily run headlessly in scripts.
