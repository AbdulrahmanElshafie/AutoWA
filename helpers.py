"""
helpers.py

This module provides utility functions to validate GUI inputs, handle Excel data,
and execute the main WhatsApp messaging workflow through WAController.

Responsibilities:
- Input validation:
    - Ensure required fields are filled.
    - Check numeric and logical constraints for batch and wait times.
- Excel handling:
    - Save execution results to Excel safely.
- Execution workflow:
    - Read the input Excel sheet containing officer/contact data.
    - Determine document/message type to send.
    - Interact with WAController to send messages/documents.
    - Track progress, estimated time, and rounds left in the GUI.
    - Handle batching, random delays, and account switching.
    - Safely handle exceptions, GUI closure, and pausing/resuming.

Functions:
- validate_inputs(value): Validate GUI input fields.
- save_excel(df): Save the DataFrame to an Excel file with Arabic headers.
- run_execution(values, window): Run the main WhatsApp sending process.
"""


import FreeSimpleGUI as sg
import pandas as pd
import time
import random
from gui.layout import config
import os
try:
    from core.runner import execute_jobs
except ImportError:
    def execute_jobs(csv_path):
        return {"total": 0, "success": 0, "failed": 0}
import math
from logger import log_function
import gui.events as events

@log_function
def validate_inputs(values):
    """
    Validate user input from the GUI before starting execution.

    Parameters:
    - values (dict): Dictionary of GUI input values keyed by element keys.

    Returns:
    - bool: True if inputs are valid, False otherwise.

    Logic:
    - Ensures all required fields are filled.
    - Checks that numeric fields are numbers and within logical bounds:
      - MSG_WAIT_MIN < MSG_WAIT_MAX
      - BATCH_WAIT_MIN < BATCH_WAIT_MAX
    - Shows popups for errors and returns False on validation failure.
    """
    required_fields = {
        "-BATCH_SIZE-": "حجم الدفعة",
        "-MSG_WAIT_MIN-": "انتظار الرسالة (ث)",
        "-MSG_WAIT_MAX-": "انتظار الرسالة (ث)",
        "-BATCH_WAIT_MIN-": "انتظار الدفعة (ث)",
        "-BATCH_WAIT_MAX-": "انتظار الدفعة (ث)",
        "-PROFILE-": "ملف التوقيت",
    }
    error_msg = "الرجاء ملء الحقل: "
    valid = True
    
    # Check the existence of of values for the required fields
    for key, value in required_fields.items():
        if not values.get(key):
            error_msg += f"{value} - "
            valid = False

    if not valid:
        sg.popup(error_msg)
        return valid
    
    # Check numeric fields for valid numeric input
    try:
        int(values["-BATCH_SIZE-"])
        float(values["-MSG_WAIT_MIN-"])
        float(values["-MSG_WAIT_MAX-"])
        float(values["-BATCH_WAIT_MIN-"])
        float(values["-BATCH_WAIT_MAX-"])
    except ValueError:
        sg.popup("الرجاء إدخال أرقام صالحة في حقول الانتظار وحجم الدفعة.")
        return False
    
    # Ensure minimums are less than maximums
    if float(values["-MSG_WAIT_MIN-"]) >= float(values["-MSG_WAIT_MAX-"]):
        sg.popup("الحد الأدني لحقل انتظار الرسائل يجب أن يكون أقل من الحد الأقصي")
        return False

    if float(values["-BATCH_WAIT_MIN-"]) >= float(values["-BATCH_WAIT_MAX-"]):
        sg.popup("الحد الأدني لحقل انتظار الدفعة يجب أن يكون أقل من الحد الأقصي")
        return False

    return True

@log_function
def run_execution(values, window):
    excel_file_path = config.get("sheet_file")
    if not excel_file_path or not os.path.exists(excel_file_path):
        sg.popup("ملف الإدخال غير موجود")
        events.running = False
        window.write_event_value("-THREAD DONE-", ("ERROR", 0, 0, 0, None))
        return

    result = {}
    import threading
    def target():
        try:
            result['stats'] = execute_jobs(excel_file_path)
        except Exception as e:
            result['error'] = str(e)

    try:
        df = pd.read_csv(excel_file_path)
        total_rows = len(df)
    except:
        total_rows = 1

    window["-PROGRESS-"].update(current_count=0, max=total_rows)

    start_time = time.time()
    t = threading.Thread(target=target, daemon=True)
    t.start()

    while t.is_alive():
        if not events.running:
            break
            
        time.sleep(1)
        try:
            df = pd.read_csv(excel_file_path)
            if 'status' in df.columns:
                processed = len(df[df['status'] != 'pending'])
                # avoid taking NaN as processed if not correctly stored. We consider success or fail as processed
            else:
                processed = 0
            
            window["-PROGRESS-"].update(current_count=processed)
            window["-PROGRESS_TEXT-"].update(f"{processed} / {total_rows}")
        except:
            pass

    t.join(timeout=1.0)
    
    if 'stats' in result:
        stats = result['stats']
        successfully_sent = stats.get("success", 0)
        failed_sent = stats.get("failed", 0)
        pending_sent = stats.get("total", total_rows) - successfully_sent - failed_sent
        if not events.running and pending_sent > 0:
            status = "PAUSED"
        else:
            status = "DONE"
    else:
        successfully_sent = failed_sent = pending_sent = 0
        status = "ERROR"

    events.running = False
    window["-PAUSE-"].update(disabled=True)
    window["-EXECUTE-"].update(disabled=False)
    
    window.write_event_value("-THREAD DONE-", (status, successfully_sent, pending_sent, failed_sent, None))


@log_function
def create_notification(text, duration=5, *args):
    # Get screen width and height
    screen_width, screen_height = sg.Window.get_screen_size()

    # Define the layout for the window
    layout = [
        [sg.Text(text, size=(30, 1), justification='center', font=16)],
        [sg.Text("", size=(10, 1), key="countdown", justification='center', font=('bold', 20))],
        [sg.Button("Dismiss", size=(10, 1), key="Dismiss")]
    ]
    
    # If additional widgets are passed, add them to the layout
    for widget in args:
        if isinstance(widget, str):  # If it's a string, make sure it's converted to sg.Text
            widget = sg.Text(widget)
        if isinstance(widget, sg.Element):  # Check if widget is a valid PySimpleGUI element
            layout.insert(-1, [widget])  # Insert widgets before the "Dismiss" button
        else:
            raise ValueError(f"Invalid widget type: {type(widget)}. Must be a string or PySimpleGUI Element.")

    
    # Create the window (finalize=True ensures window is fully created)
    notification_window = sg.Window(
        "Notification", layout, 
        alpha_channel=0.5,  # Transparency
        finalize=True,
        no_titlebar=True,
        keep_on_top=True,
        grab_anywhere=True,
        element_justification='c'
    )

    # Calculate the window size after it's been created
    window_width, window_height = notification_window.size

    # Calculate the optimal position so the window fits on screen
    x_position = max(screen_width - window_width - 20, 0)  # 20px padding from the edge
    y_position = max(screen_height - window_height - 20, 0)  # 20px padding from the edge

    # Move the window to the calculated position
    notification_window.move(x_position, y_position)

    # Ensure window is displayed before any event handling
    notification_window.TKroot.update()

    # Set the window to close after a specific duration or when the Dismiss button is clicked
    start_time = time.time()  # Get the current time
    end_time = start_time + duration  # Calculate end time
    
    while True:
        event, values = notification_window.read(timeout=100)  # timeout in ms

        # Calculate remaining time
        remaining_time = int(end_time - time.time())
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        
        # Update the countdown text
        notification_window["countdown"].update(f"{minutes:02}:{seconds:02}")
        
        # If user clicks "Dismiss" or window is closed
        if event == sg.WIN_CLOSED or event == "Dismiss":
            break
        
        # Check if the timeout duration has passed
        if time.time() >= end_time:
            break
        
    notification_window.close()
