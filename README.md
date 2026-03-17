# WhatsApp Automation System ("Communication System")

The **WhatsApp Automation System** is a professional Python-based desktop automation tool designed to streamline mass messaging on WhatsApp Web. Built with productivity and robustness in mind, it provides a feature-rich graphical interface to manage contacts, automate message delivery, and handle document attachments with human-like precision.

Leveraging image-based recognition (through `pyautogui`), the system handles complex WhatsApp Web workflows, ensuring messages reach their destination reliably while simulating natural user behavior (variable typing speeds, random delays, and batch-wise processing) to prevent detection risks. It is designed for Windows, with Chrome or Edge as supported browsers, and assumes WhatsApp Web is logged in (with dark mode).

---

## Key Features

- **GUI Interface** using FreeSimpleGUI:
  - Configure paths for Excel files, permits, and Seglat documents
  - Manage typing and timing profiles
  - Start, pause, cancel, or restart message execution
  - Visual progress and estimated completion time

- **WA Automation Backend** (`WAController`):
  - Add, search, and delete contacts dynamically
  - Send text messages and attach PDF documents
  - Support multiple WhatsApp accounts and browser profiles
  - Randomized timing profiles for human-like interactions

- **Excel Integration**:
  - Reads officer data (phone number, officer ID, etc.)
  - Tracks message status per officer
  - Saves progress periodically

- **Logging**:
  - Logs execution errors and function-level events in `logs/` directory

---

## Architecture

The system is organized in **layers** for maintainability and separation of concerns:

```text
GUI Layer (gui/)            → Handles all user interaction
├─ layout.py             → Defines GUI layout
├─ events.py             → Handles GUI events and interactions
└─ helpers.py            → Utility functions for GUI management

Business Logic Layer (helpers.py) → Validation, execution orchestration, Excel handling

Automation Layer (app/WAController.py + Controller.py)
├─ Controller.py         → Generic desktop automation (click/type/paste)
├─ WAController.py       → WhatsApp-specific workflows (add contact, send message, attach file)
└─ helpers.py            → Timing, error handling, utility functions for WA automation

Assets (assets/)            → Reference images used for WhatsApp Web image-based automation
Logs (logs/)                → Stores execution and error logs
```

---

## Workflow

1. **Configuration**
   - User selects:
     - Excel input file
     - Permits directory
     - Seglat directory
   - Optionally manages typing/timing profiles (Fast, Normal, Slow, Distracted)

2. **Validation**
   - GUI validates required fields (batch size, wait times, profile selection)
   - Numeric and logical constraints are checked (min < max for waits)

3. **Execution**
   - Execution runs in a **background thread**
   - For each officer in Excel:
     - Open WhatsApp Web in selected account/profile
     - Add contact if not already present
     - Send message and optionally attach a PDF document
     - Delete contact if required
   - Progress updates in GUI:
     - Total messages
     - Messages per batch/round
     - Estimated remaining time

4. **Batch Management**
   - Randomized message wait (`MSG_WAIT_MIN/MAX`) per message
   - Randomized batch wait (`BATCH_WAIT_MIN/MAX`) per batch
   - Multi-account rotation supported

5. **Completion**
   - GUI notifies the user on success, pause, or error
   - Excel file is updated with message status
   - Logs are written for error tracking

---

## Installation & Requirements

### System Requirements

- Windows OS (tested)
- Chrome (required) / Edge (optional)
- WhatsApp Web logged in (dark mode)
- Stable screen resolution, UI scaling 100%

### Python Requirements

- Python 3.8+
- Required packages:

```bash
pip install FreeSimpleGUI pandas openpyxl pyautogui pyperclip opencv-python
```

- Optional but recommended: `logger.py` for function-level logging

### Assets

- All images required for WhatsApp UI recognition must be placed in `assets/`
- Images must match the resolution and UI theme (dark mode, English & Arabic)
- Example structure:

```text
assets/
    ├── WA.PNG
    ├── WA AR.PNG
    ├── New Chat.PNG
    ├── New Chat AR.PNG
    ├── New Contact.PNG
    ├── New Contact AR.PNG
    ├── Phone.PNG
    ├── Phone AR.PNG
    ├── Valid WA Num.PNG
    ├── Name.PNG
    ├── Name AR.PNG
    ├── Save Contact.PNG
    ├── Contact Bar.PNG
    ├── Contact Bar AR.PNG
    ├── Edit Contact.PNG
    ├── Edit Contact AR.PNG
    ├── Delete Contact.PNG
    ├── Delete Contact Confirm.PNG
    ├── Delete Contact Confirm AR.PNG
    ├── Msg Bar.PNG
    ├── Msg Bar AR.PNG
    ├── Add Doc.PNG
    ├── Doc.PNG
    ├── Doc AR.PNG
    └── File Sent.PNG
```

- Arabic variants are suffixed with `AR.PNG`

---

## Usage Instructions

1. **Launch Application**

   ```bash
   python app_main.pyw
   ```

2. **Configure Paths**

   - Select Excel input file
   - Select Permits directory
   - Select Seglat directory
   - Click **"Confirm Paths"** to save

3. **Manage Typing/Timing Profiles**

   - Add/Edit/Delete profiles
   - Preview execution timing for selected profile

4. **Configure Execution**

   - Set batch size
   - Set message wait time (`MSG_WAIT_MIN/MAX`)
   - Set batch wait time (`BATCH_WAIT_MIN/MAX`)
   - Choose document type (`permit`, `seglat`, or `msg`)

5. **Run Execution**

   - Click **Update Sheet**
   - Click **Execute / Resume**
   - Monitor progress bar and estimated time
   - Pause with **Pause**, restart with **Restart**, or cancel with **Cancel** when needed

6. **Follow Instructions**

   - Detailed instructions accessible via **Instructions** button
   - Keep Excel file closed during execution
   - Avoid moving mouse during automation

---

## Contributing

- **Adding new document types**: Extend `WAController.send_content()`
- **New message templates**: Add in `WAController.get_msg()`
- **Browser/accounts support**: Modify `WAController.accounts` list
- **Improve image detection**: Update assets in `assets/`
- **Timing profiles**: Add or tweak human-like randomization in `helpers.py`

---

## Known Issues / Limitations

- Designed for **WhatsApp Web in dark mode**
- Windows-only tested (paths may need adjustments for Linux/macOS)
- High-volume execution may still trigger WhatsApp anti-bot detection
- UI changes in WhatsApp Web may require new screenshots in `assets/`
- GUI must not be interacted with during automation

---

## File Structure

```text
C:.
│   app_main.pyw
│   config.json
│   helpers.py
│   logger.py
│   README.md
│
├───app
│   ├── Controller.py
│   ├── helpers.py
│   ├── WAController.py
│   └── README.md
├───assets
│   └── *.PNG (WhatsApp UI reference images)
├───gui
│   ├── events.py
│   ├── helpers.py
│   ├── instructions.txt
│   ├── layout.py
│   └── README.md
├───logs
│   ├── info.log
│   └── error.log
└───__pycache__
```
