# WhatsApp Automation System ("AutoWA")

![App](https://github.com/AbdulrahmanElshafie/AutoWA/blob/stage/AutoWA.PNG)

The **AutoWA** is a powerful, professional Python-based desktop tool designed to strictly streamline mass-messaging on WhatsApp Web. Built to maximize productivity, it uses a graphical interface to easily manage contacts, dynamically template messages, and safely automate document attachments with human-like accuracy.

[![Buy Me A Book](https://img.shields.io/badge/Buy%20Me%20A%20Book-Support-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/abdulrahmanelshafie)

## 🌟 Prowess & Capabilities (Features)
- **GUI Interface (FreeSimpleGUI)**: Seamlessly dictate target output sheets, browse paths, and modify active configuration profiles.
- **Human-like Automation**: Leverages randomized typing delays, calculated batch intervals, and realistic pauses to emulate organic workflows and safely bypass immediate anti-bot detections.
- **Dynamic Messaging**: Resolve complex template placeholders (like `{contact_name}`) on the fly, optionally picking random message variants per outbound contact.
- **Document Attachments**: Easily attach and resolve individual files (like PDFs or Seglat images) explicitly per user right out of the input CSV.
- **Account Rotation**: Add massive batch limits over multiple active WhatsApp Browser sessions to distribute loads between different accounts safely.
- **Real-Time Synchronous GUI**: Visually tracks success rates, completion time estimations, and error handling seamlessly in an interactive terminal.

## ⚠️ Known Weaknesses & Constraints
- **Theme & Language Locked**: It currently only actively supports **WhatsApp Web in Dark Mode**, and resolves strictly to **English & Arabic**. To add more languages or light-mode interfaces, you must manually capture and include the matching icons for them in the `assets/` folder. The same limitation currently applies when introducing entirely new browsers not yet mapped.
- **Number Routing Constraints**: Adding contacts programmatically currently assumes **Egyptian phone numbers** exclusively. Foreign (international) numbers are texted directly without going through the native 'Save Contact' book pipeline. Support for adding varied foreign formats is scheduled for future updates!
- **Foreground Dedication**: It utilizes aggressive image-recognition (`pyautogui`). You **cannot** drastically move your mouse, cover the designated browser window, or minimize the tab while executing. The visual desktop environment essentially belongs to the bot during operations.

## 🚀 Future Roadmap & "To Do" Highlights
We are actively building toward making this system a comprehensive CRM tool. Exciting upcoming functionality includes:
- **System Health & Log Dashboards**: Dedicated UI pages to visualize execution stats, error alarms, and deep system monitoring.
- **Richer WhatsApp Interactions**: Sending live locations, injecting emojis natively, and formatting rich texts.
- **Customer Support Agent Mode**: Turning the system from a unidirectional blasting mechanism into a bidirectional response-driven WhatsApp Support Agent.
- **Foreign Number Optimization**: Deeply handling contact saving pipelines for non-Egyptian international targets.
- **Global Stylization Support**: Allowing configuration-less swapping between Dark Mode and Light Mode, and auto-fallback languages.

---

## 🛠 File Structure & Architecture
This project is beautifully organized into clear layers so the GUI, core logic, and WhatsApp automation can evolve independently without creating tight coupling.

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
- GUI Layer: handles user interaction, execution controls, and visual feedback.
- Core Layer: loads jobs, validates input, and runs the execution workflow.
- Automation Layer: performs the actual WhatsApp Web interaction.
- Configuration & Contracts: stores system rules, schemas, and API contracts.
- Data Layer: stores job input files.
- Assets Layer: stores image references used for UI detection.
- Logging & Diagnostics: stores logs and analysis helpers.

###  Project Structure:
```
.
├── app_main.pyw — Entry Point
├── core/ — Execution Engine: Handles the main system logic
├── app/ — Automation Layer: Controls WhatsApp Web via desktop automation.
├── gui/ — GUI: Handles all user interaction and execution control.
├── assets/ — UI Detection Images: Contains screenshots used for WhatsApp Web automation. Organized by UI components (Send, Chat, Contact, etc.).
├── config/ — Configuration & Templates: Stores runtime settings and reusable messages.
├── data/ — Input Data: jobs.csv → main dataset used for execution
├── contracts/ — System Interfaces for Agents: Defines how components interact.
├── schemas/ — Data Definitions: Defines structure of all inputs.
├── docs/ — System Documentation: system_contract.md → overall architecture and rules
├── logs/ — Logs: Stores runtime logs and error tracking
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
