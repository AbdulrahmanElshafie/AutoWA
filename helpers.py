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
from gui.helpers import save_config
from gui.layout import config
import os
from core.runner import execute_jobs
import math
from logger import log_function
import gui.events as events
from gui.helpers import load_messages
import random

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
        "-BATCH_SIZE-": "Batch Size",
        "-MSG_WAIT_MIN-": "Msg Wait (sec)",
        "-MSG_WAIT_MAX-": "Msg Wait (sec)",
        "-BATCH_WAIT_MIN-": "Batch Wait (min)",
        "-BATCH_WAIT_MAX-": "Batch Wait (min)",
        "-PROFILE-": "Timing Profile",
    }
    error_msg = "Please fill the field: "
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
        sg.popup("Please enter valid numeric values in time wait and batch fields.")
        return False
    
    # Ensure minimums are less than maximums
    if float(values["-MSG_WAIT_MIN-"]) >= float(values["-MSG_WAIT_MAX-"]):
        sg.popup("Minimum message wait time must be less than the maximum limit.")
        return False

    if float(values["-BATCH_WAIT_MIN-"]) >= float(values["-BATCH_WAIT_MAX-"]):
        sg.popup("Minimum batch wait time must be less than the maximum limit.")
        return False

    # 1. if the msg txt only, make sure the txt box has a value
    if values.get("-MSG_FIXED-") and not values.get("-FIXED_TXT-", "").strip():
        sg.popup("Please enter text for the fixed message.")
        return False
        
    # 2. if the msg is a tmp make sure a tmp is used
    if values.get("-MSG_TEMPLATE-") and not values.get("-SEL_MSG_TEMPLATE-"):
        sg.popup("Please select a message template.")
        return False
        
    # 3. if a tmp without random then a tmp and a variation must be chosen
    if values.get("-MSG_TEMPLATE-") and not values.get("-CHK_RANDOM_VAR-") and not values.get("-SEL_VARIANT-"):
        sg.popup("Please select a template variant or enable random variation.")
        return False
        
    # 4. if const doc is chosen then a path must be provided
    if values.get("-DOC_FIXED-") and not values.get("-FIXED_DOC_IN-", "").strip():
        sg.popup("Please specify a document path for the fixed document mode.")
        return False
        
    # 5. if a variable doc is picked then the doc_path must be provided
    if values.get("-DOC_VAR-"):
        csv_file = values.get("-SHEET-") or config.get("sheet_file")
        if csv_file and os.path.exists(csv_file):
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)
                if "doc_path" not in df.columns:
                    sg.popup("The CSV file must contain a 'doc_path' column when Variable Document mode is selected.")
                    return False
            except Exception:
                pass

    # 6. no msg without txt or doc, at least one should be chosen
    if values.get("-MSG_DOC_ONLY-") and values.get("-DOC_NONE-"):
        sg.popup("You must select either a message to send or a document to send.")
        return False

    return True

@log_function
def run_execution(values, window):
    """
    Main orchestrator for the execution process.
    Prepares the job data based on GUI selections and passes it to the core execution engine.

    Parameters:
    - values (dict): GUI input values containing message modes, document settings, etc.
    - window (sg.Window): The active GUI window for progress updates.

    Logic:
    1. Validates the selected paths and parses the execution delays.
    2. Reads the jobs from the input CSV file.
    3. Resolves the final message content for each row (including template processing and \{contact_name\} substitution).
    4. Resolves the document paths for each row.
    5. Strips away temporary/intermediate metadata from the CSV to match the core engine schema.
    6. Calls the backend execution engine (`execute_jobs`) which maintains the actual process.
    7. Broadcasts the final completion status back to the PySimpleGUI event loop.
    """
    excel_file_path = config.get("sheet_file")
    if not excel_file_path or not os.path.exists(excel_file_path):
        sg.popup("Input data file not found.")
        events.running = False
        window.write_event_value("-THREAD DONE-", ("ERROR", 0, 0, 0, None))
        return

    # Pass GUI execution parameters to the backend
    try:
        config["batch_size"] = int(values.get("-BATCH_SIZE-", 5))
        config["msg_wait_min"] = float(values.get("-MSG_WAIT_MIN-", 5))
        config["msg_wait_max"] = float(values.get("-MSG_WAIT_MAX-", 10))
        config["batch_wait_min"] = float(values.get("-BATCH_WAIT_MIN-", 10))
        config["batch_wait_max"] = float(values.get("-BATCH_WAIT_MAX-", 20))
        config["browsers"] = values.get("-BROWSERS-", ["Default Browser"])
        save_config(config)
    except Exception as e:
        sg.popup(f"Failed to save execution configuration: {str(e)}")
        events.running = False
        window.write_event_value("-THREAD DONE-", ("ERROR", 0, 0, 0, None))
        return

    result = {}

    try:

        df = pd.read_csv(excel_file_path)
        
        # We need contact_name to exist before replacing strings
        if "contact_name" not in df.columns:
            df["contact_name"] = ""
            
        # Resolve Message
        if values.get("-MSG_FIXED-"):
            msg_text = values.get("-FIXED_TXT-", "")
            # Apply {contact_name} to fixed messages as well, for consistency
            df["message"] = df["contact_name"].apply(
                lambda name: msg_text.replace("{contact_name}", str(name) if pd.notna(name) else "")
            )
        elif values.get("-MSG_TEMPLATE-"):
            template_key = values.get("-SEL_MSG_TEMPLATE-", "")
            messages_dict = load_messages()
            template = messages_dict.get(template_key, {})
            variants = template.get("variants", [])
            
            if not variants:
                sg.popup(f"No variants found for template '{template_key}'.")
                events.running = False
                window.write_event_value("-THREAD DONE-", ("ERROR", 0, 0, 0, None))
                return
                
            is_random = values.get("-CHK_RANDOM_VAR-", False)
            selected_variant = values.get("-SEL_VARIANT-", "")
            
            def resolve_template_msg(name):
                if is_random or not selected_variant:
                    msg = random.choice(variants)
                else:
                    msg = selected_variant
                return msg.replace("{contact_name}", str(name) if pd.notna(name) else "")
                
            df["message"] = df["contact_name"].apply(resolve_template_msg)
            
        elif values.get("-MSG_DOC_ONLY-"):
            df["message"] = ""
            
        # Resolve Document
        if values.get("-DOC_NONE-"):
            df["doc_path"] = ""
        elif values.get("-DOC_FIXED-"):
            fixed_doc = values.get("-FIXED_DOC_IN-", "")
            df["doc_path"] = fixed_doc
        elif values.get("-DOC_VAR-"):
            if "doc_path" not in df.columns:
                df["doc_path"] = ""
                
        # Clean up old columns if they exist
        for col in ["message_mode", "message_text", "message_key", "doc_mode"]:
            if col in df.columns:
                df = df.drop(columns=[col])
                
        # Fill missing schemas required columns
        for col in ["number", "status", "status_message"]:
            if col not in df.columns:
                df[col] = "" if col != "status" else "pending"
                
        # Re-save the overriden definitions back so the engine reads them!
        df.to_csv(excel_file_path, index=False)
        total_rows = len(df)
    except Exception as e:
        sg.popup(f"An error occurred loading job execution settings: {str(e)}")
        events.running = False
        window.write_event_value("-THREAD DONE-", ("ERROR", 0, 0, 0, None))
        return

    start_time = time.time()
    
    try:
        result['stats'] = execute_jobs(excel_file_path, window=window)
    except Exception as e:
        result['error'] = str(e)
    
    if 'stats' in result:
        stats = result['stats']
        successfully_sent = stats.get("success", 0)
        failed_sent = stats.get("fail", 0)
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
