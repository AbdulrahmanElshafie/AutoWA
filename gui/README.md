
# WhatsApp Automation GUI

## Summary
This GUI application provides an interface to automate message sending, permits handling, and data entry tasks using pre-defined typing and timing profiles. It is designed to help users manage batch operations efficiently while simulating human-like typing behavior.  

The application uses **FreeSimpleGUI** for the GUI, **pandas** for Excel file management, and supports user-defined timing profiles for flexible automation.

---

## Features

### 1. Path Configuration
- Select directories for:
  - Permits (`permits_dir`)
  - Seglat files (`seglat_dir`)
- Choose an Excel input file (`sheet_file`)
- Save paths for future sessions.
- Validates the existence of selected files and folders.

### 2. Typing / Timing Profiles
- Manage typing speed profiles with four categories:
  - Fast
  - Normal
  - Slow
  - Distracted
- Add, edit, and delete profiles.
- Preview profile parameters in real-time.
- Automatically converts user input to seconds for consistent execution timing.

### 3. Execution and Batch Management
- Start, pause, resume, or restart execution.
- Configure batch size and randomized wait times:
  - Message wait time (seconds)
  - Batch wait time (minutes)
- Estimate total execution time based on batch settings and typing speed.
- Track progress with:
  - Total messages count
  - Messages per round
  - Remaining rounds
  - Progress bar

### 4. Instructions and Usage Notes
- Display detailed usage instructions via a popup.
- Important static notes to guide correct usage and prevent errors:
  - Close Excel before execution
  - Do not close the application during execution
  - Avoid mouse interference during automation
  - Use the dark mode for best results

---

## File Structure and Responsibilities
gui/
    ├───events.py
    ├───helpers.py
    ├───instructions.txt
    ├───layout.py


### `layout.py`
- Defines the GUI layout using **FreeSimpleGUI**.
- Composed of logical sections (frames):
  - Paths
  - Typing/Timing Profiles
  - Execution & Operations
  - Important Notes
- Preloads previously saved configuration values.
- **Does not** contain logic or event handling.

### `helpers.py`
- Provides helper functions for:
  - Loading and saving configuration (`config.json`)
  - Converting time values to seconds
  - Estimating execution time
  - Refreshing GUI record counts
  - Loading instructions from a text file
- Ensures persistence of user settings and smooth interaction between GUI and event-handling logic.

### `events.py`
- Handles all GUI events triggered by user actions.
- Functions:
  - `handle_events(event, values, window)`:
    - Updates configuration paths
    - Updates typing profile previews
    - Handles profile creation, editing, and deletion
    - Calculates estimated execution time, total per round, and rounds left
    - Manages execution flow (start, pause, cancel, restart)
    - Loads and displays instructions
- Uses `helpers.py` functions for configuration, time conversions, and data updates.

---

## Requirements

- Python 3.8+
- [FreeSimpleGUI](https://pypi.org/project/FreeSimpleGUI/)
- [pandas](https://pypi.org/project/pandas/)
- [openpyxl](https://pypi.org/project/openpyxl/) (for Excel file reading/writing)
- logger module (for function logging, optional but recommended)
- Existing Excel files and directories for permits and seglat

---

## How to Use

1. **Set Paths**
   - Open the application and select:
     - Permits directory
     - Seglat directory
     - Excel input file
   - Click **"تأكيد المسارات"** to save paths.

2. **Manage Typing Profiles**
   - Select a profile to preview timing settings.
   - Use **Add**, **Edit**, or **Delete** to manage profiles.

3. **Configure Execution**
   - Set message wait time (seconds) and batch wait time (minutes).
   - Set batch size (number of messages per batch).
   - Monitor:
     - Total messages
     - Messages per round
     - Remaining rounds
     - Estimated time
   - Click **تنفيذ/استكمال** to start.
   - Use **إيقاف مؤقت** to pause, **إلغاء** to cancel, **إعادة التنفيذ** to restart.

4. **Follow Instructions**
   - Access detailed instructions via **التعليمات** button.
   - Follow important static notes for smooth operation.

---

## Notes
- Ensure Excel input files are closed before execution.
- Avoid interacting with the GUI or moving the mouse during active automation.
- Use the dark mode in WA for optimal visibility.
