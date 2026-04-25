# WhatsApp Automation System ("AutoWA")

![App](https://github.com/AbdulrahmanElshafie/AutoWA/blob/stage/AutoWA.PNG)

The **AutoWA** is a powerful, professional Python-based desktop tool designed to strictly streamline mass-messaging on WhatsApp Web. Built to maximize productivity, it uses a graphical interface to easily manage contacts, dynamically template messages, and safely automate document attachments with human-like accuracy.

[![Buy Me A Book](https://img.shields.io/badge/Buy%20Me%20A%20Book-Support-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/abdulrahmanelshafie)

## 🌟 Prowess & Capabilities (Features)
- **GUI Interface (FreeSimpleGUI)**: Seamlessly dictate target output sheets, browse paths, and modify active configuration profiles via a multithreaded asynchronous event loop.
- **Human-like Automation**: Leverages randomized typing delays, calculated batch intervals, and realistic pauses using OpenCV template matching to safely bypass bot-detection algorithms.
- **Dynamic Messaging**: Resolve complex template placeholders (like `{contact_name}`) on the fly using the core validation engine, optionally picking random message variants per outbound contact.
- **Document Attachments**: Easily attach and resolve individual files (like PDFs or Seglat images) explicitly per user directly from the ingested CSV payload.
- **Account Rotation**: Add massive batch limits over multiple active WhatsApp Browser sessions to distribute loads between different accounts, managing state via background daemons.
- **Real-Time Synchronous GUI**: Visually tracks success rates, completion time estimations, and error handling seamlessly through inter-thread window messaging.
- **System Health & Log Dashboards**: Dedicated UI pages to visualize JSONL execution stats, error alarms, and deep system monitoring telemetry.

## ⚠️ Known Weaknesses & Constraints
- **Theme & Language Locked**: It currently only actively supports **WhatsApp Web in Dark Mode**, and resolves strictly to **English & Arabic**. To add more languages or light-mode interfaces, you must manually capture and include the matching OpenCV assets (`.PNG` UI fragments) in the `assets/` folder. The same limitation applied when introducing entirely new browsers not yet mapped.
- **Number Routing Constraints**: Adding contacts programmatically currently assumes **Egyptian phone numbers** exclusively, routing them via the WhatsApp API. Foreign (international) numbers are texted directly without going through the native 'Save Contact' book pipeline. Support for adding varied foreign routing logic is scheduled for future updates!
- **Foreground Dedication**: It utilizes aggressive image-recognition (`pyautogui`). The automation layer demands absolute focus. You **cannot** drastically move your mouse, cover the designated browser window, or minimize the tab while the core execution thread is dispatched.

## 🚀 Future Roadmap & "To Do" Highlights
We are actively building toward making this system a comprehensive CRM tool. Exciting upcoming functionality includes:
- **Richer WhatsApp Interactions**: Constructing new payload handlers for sending live locations, injecting emojis natively, and formatting rich texts.
- **Customer Support Agent Mode**: Turning the execution loop from a unidirectional broadcasting thread into a bidirectional listener (DOM parsing) for response-driven WhatsApp Support.
- **Foreign Number Optimization**: Deeply handling contact saving pipelines and regex validation for non-Egyptian international targets.
- **Global Stylization Support**: Allowing configuration-less swapping between Dark Mode and Light Mode, and auto-fallback language mapping.

---

## 🛠 File Structure & Architecture
This project is beautifully organized into clear layers so the GUI, core logic, and WhatsApp automation can evolve independently without creating tight coupling.

**Note: Please refer to the localized `README.md` file located inside each respective module directory (like `core/`, `app/`, `gui/`, `monitoring/`, `analytics/`) for deep-dive technical explanations of their internal state transitions, API contracts, and logic.**

### Architecture Overview
```
Project Root
├── GUI Layer
├── Core Layer
├── Automation Layer
├── Configuration & Contracts
├── Data Layer
├── Assets Layer
└── Logging & Diagnostics
```
### Layer Responsibilities
- GUI Layer: handles asynchronous user interaction, cross-thread execution controls, and decoupled visual feedback.
- Core Layer: manages job ingestion, schema-validates input payloads, and dispatches the main execution daemon threads.
- Automation Layer: controls strictly local UI DOM mapping and action sequences via PyAutoGUI.
- Configuration & Contracts: enforces system boundaries, JSON parameter schemas, and Markdown API contracts.
- Data Layer: persistent target ingestion schemas (CSV).
- Assets Layer: binary computer-vision references (`.PNG`) mapped to UI elements.
- Logging & Diagnostics: streams ephemeral daemon outputs and structured JSONL analysis logs.

###  Project Structure:
```
.
├── app_main.pyw — Entry Point: Initializes GUI and thread supervisors.
├── core/ — Execution Engine: Handles the main system logic, jobs, and thread dispatching. (See `core/README.md`)
├── app/ — Automation Layer: Controls WhatsApp Web strictly via desktop/DOM automation. (See `app/README.md`)
├── gui/ — GUI: Separate Layouts and Event Handlers. (See `gui/README.md`)
├── monitoring/ — Health Systems: Real-time system monitoring logic. (See `monitoring/README.md`)
├── analytics/ — Telemetry: Parses metrics into session-based throughput stats. (See `analytics/README.md`)
├── config/ — Configuration & Templates: Stores runtime settings and reusable messages.
├── contracts/ — System Interfaces for Agents: Strict markdown definitions mapping API boundaries.
├── schemas/ — Data Definitions: JSON and Markdown schemas defining state structures.
├── data/ — Input Data: jobs.csv → main dataset used for execution
├── assets/ — UI Detection Images: Contains screenshots used for OpenCV template matching.
├── docs/ — System Documentation: overall architecture and rules.
├── logs/ — Logs: Stores runtime JSONL streams and error tracking.
```

---

## ⚙️ Usage Instructions

### 1. Requirements & Setup
- Windows OS naturally.
- **Chrome** (or Edge) installed.
- Python 3.8+ with dependencies:
  ```bash
  pip install FreeSimpleGUI pandas pyautogui pyperclip opencv-python
  ```

### 2. Prepare Assets
Ensure you have perfectly cropped `.PNG` screenshots in your `assets/` folder covering the specific WhatsApp Web buttons you need to click (such as 'New Chat', 'Add Doc', 'Send', etc.). If your computer's resolution scales the browser oddly, you might need to retake the screenshots!

### 3. Launching
```bash
python app_main.pyw
```
1. **Settings / Paths**: Browse for your Target Data CSV (conforming to `schemas/jobs.schema.md`).
2. **Operations**: Select the target wait limits, batch capacities, and profile delays.
3. Write your fixed message or choose your Dynamic Template variants.
4. Hit **Execute / Resume** and let go of your mouse!

---

## 🤝 Contributing
Contributions are absolutely welcome! If you intend to:
- **Patch Core Engine**: Make sure changes in `core/ runner.py` handle custom exceptions.
- **Expand Browser/Icon Sets**: Provide clean `.PNG` files. Add references into `WAController.py`.
- **Add New Fields**: Keep `schemas/jobs.schema.md` actively updated.
