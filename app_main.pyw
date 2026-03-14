"""
app_main.py

Main entry point for the WhatsApp Messaging GUI application ("منظومة التواصل").

Responsibilities:
- Initialize the FreeSimpleGUI window with the layout defined in gui.layout.
- Set up logging to the console for debugging and error tracking.
- Run the main event loop to:
    - Listen for GUI events (button clicks, input changes, etc.).
    - Delegate event handling to gui.events.handle_events.
    - Manage the execution of the WhatsApp messaging process in a background thread.
    - Handle thread completion events and update the user via popups.
    - Safely close the application and stop ongoing executions.
- Launch and control background execution threads for sending messages/documents.
- Validate GUI input fields before starting or restarting execution.

Global Variables:
- window (sg.Window): The FreeSimpleGUI main window object.
- exec_thread (threading.Thread | None): Reference to the currently running background execution thread.

Event Handling Logic:
- "-THREAD DONE-": Custom event triggered when run_execution finishes or is paused/error.
- sg.WIN_CLOSED: Close event; stops execution and exits the loop.
- handle_events(): Processes GUI events and returns action codes like "EXECUTE", "CANCEL", or "RESTART".
- "EXECUTE"/"RESTART": Validates inputs and starts run_execution in a separate daemon thread.
- "CANCEL": Confirms exit and stops the application.
"""

import FreeSimpleGUI as sg
from gui.layout import layout
from gui.events import handle_events
import gui.events as events
from helpers import *
from logger import enable_console_logging
import logging
import threading

# Enable console logging for errors only
enable_console_logging(level=logging.ERROR)

# Initialize the main GUI window
window = sg.Window("منظومة التواصل v1.5.1 Alpha", layout, finalize=True)

# Reference for background execution thread
exec_thread = None  # thread reference

# --- Main Event Loop ---
while True:
    # Read GUI events with a small timeout to allow periodic checks
    event, values = window.read(timeout=100)

    # --- Handle custom thread completion events ---
    if event == "-THREAD DONE-":
        status, successfully_sent, pending_send, failed_send, wait_time = values[event]  # status can be "DONE", "PAUSED", or "ERROR"
    
        # Create text for the stats
        success_text = f"تم إرسال {successfully_sent} بنجاح"
        pending_text = f"متبقي إرسال {pending_send}"
        fail_text = f"فشل إرسال {failed_send}"
        # Display different popup messages based on status
        if status == "DONE":
            sg.popup("تم الانتهاء من عملية الإرسال", success_text, pending_text, fail_text)  # Display the styled stats
        elif status == "PAUSED":
            sg.popup("تم إيقاف التنفيذ مؤقتًا", success_text, pending_text, fail_text)
        elif status == "ERROR":
            sg.popup("حدث خطأ أثناء التنفيذ")  # Notify user of execution error
        continue  # Skip further event handling

    if event == "-BATCH BREAK-":
        successfully_sent, pending_send, failed_send, wait_time = values[event] 

        # Create text for the stats
        success_text = f"تم إرسال {successfully_sent} بنجاح"
        pending_text = f"متبقي إرسال {pending_send}"
        fail_text = f"فشل إرسال {failed_send}"

        create_notification("فاصل بين الدفعات", wait_time, success_text, pending_text, fail_text)


    # --- Delegate event handling to events.py ---
    action = handle_events(event, values, window)

    # --- Handle window close event ---
    if event == sg.WIN_CLOSED:
        events.running = False # Signal any background thread to stop
        break

    # --- Handle CANCEL action ---
    if action == "CANCEL":
        if sg.popup_yes_no("هل تريد الخروج؟") == "Yes":
            events.running = False 
            break

    # --- Handle EXECUTE action ---
    elif action == "EXECUTE":
        if events.running:
            sg.popup("التنفيذ جارٍ بالفعل!") # Prevent multiple executions
        else:
            # Validate user inputs before starting
            if not validate_inputs(values):
                continue
            # Turn on the pause option
            window["-PAUSE-"].update(disabled=False)
            # Turn off the execution/resume option
            window["-EXECUTE-"].update(disabled=True)
            # Mark execution as running
            events.running = True
            # Start the main execution in a separate daemon thread
            exec_thread = threading.Thread(
                target=run_execution,
                args=(values, window),
                daemon=True
            )
            exec_thread.start()

    # --- Handle RESTART action ---
    elif action == "RESTART":
        if events.running:
            sg.popup("يرجى إيقاف التنفيذ أولاً قبل إعادة التشغيل") # Prevent restart during active execution
        else:
            # Validate user inputs before restarting
            if not validate_inputs(values):
                continue
            events.running = True
            # Start execution thread from scratch
            exec_thread = threading.Thread(
                target=run_execution,
                args=(values, window),
                daemon=True
            )
            exec_thread.start()

# --- Cleanup ---
window.close() # Close the GUI window safely