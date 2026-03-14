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
from app.WAController import WAController
import os
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
def save_excel(df):
    """
    Save the given DataFrame to an Excel file on the desktop.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing execution results.

    Logic:
    - Attempts to save to a primary filename.
    - If it fails (e.g., file in use), saves to a secondary filename.
    - Columns are renamed for Arabic headers. 
    - Use openpyxl engine to handle Arabic text in the excel file
    """ 
    try:
        df.to_excel('C:\\Users\\PC\\Desktop\\pdfs.xlsx', index=False, engine="openpyxl", 
                header=['رقم الهاتف', 'اسم الضابط', 'الرقم القومي للضابط / الرسالة', 'الحالة'])
    except Exception as e:
        df.to_excel('C:\\Users\\PC\\Desktop\\pdfs res.xlsx', index=False, engine="openpyxl", 
                header=['رقم الهاتف', 'اسم الضابط', 'الرقم القومي للضابط / الرسالة', 'الحالة'])

def calculate_stats(df):
    successfully_sent = len(df[df['الحالة'] == "تم إرسال المحتوى بنجاح"])
    pending_sent = len(df[df['الحالة'].isna()])
    failed_sent = len(df[(df['الحالة'] != "تم إرسال المحتوى بنجاح") & (~df['الحالة'].isna())])

    return successfully_sent, pending_sent, failed_sent

@log_function
def run_execution(values, window):  
    """
    Main execution function to process a list of officers/messages from Excel,
    interact with WAController, and update the GUI progress.

    Parameters:
    - values (dict): GUI input values.
    - window (sg.Window): The active GUI window to update progress.

    Returns:
    - None: Updates the GUI and writes results to Excel directly.

    Logic:
    1. Validates and loads the Excel input file.
    2. Determines the document type to send based on GUI selections.
    3. Initializes WAController and sets batch and round parameters.
    4. Iterates through the DataFrame:
       - Skips rows that have already been processed.
       - Opens WA accounts as needed.
       - Sends messages or documents.
       - Updates the "الحالة" column with results.
       - Updates progress bar, estimated remaining time, and rounds left.
       - Pauses or waits based on message and batch timing parameters.
       - Handles exceptions and ensures the WAController is reset.
    5. Saves final results to Excel and updates GUI buttons and events.

    Notes:
    - Uses randomization in batch size and wait times to mimic human behavior.
    - Supports pausing/stopping through the global `events.running` flag.
    - Handles GUI closure events safely.
    """  
    # Check the existence of the input files
    excel_file_path = config.get("sheet_file")
    if not excel_file_path or not os.path.exists(excel_file_path):
        sg.popup("ملف الإدخال غير موجود")
        events.running = False
        window.write_event_value("-THREAD DONE-", ("ERROR", None, None, None, None))
        return
    
    # Read the input file
    df = pd.read_excel(excel_file_path, engine="openpyxl")
    
    # Read the kind of content to be sent (permit, seglat, msg)
    if values["-TYPE_PERMIT-"]:
        doc_type = "permit"
    elif values["-TYPE_SEGLAT-"]:
        doc_type = "seglat"
    elif values["-TYPE_MSG-"]:
        doc_type = "msg"
    else:
        doc_type = None

    # Read the typing, waiting profile
    profile_name = values["-PROFILE-"] 
    # Read the account batch size (number of msgs sent per account)
    batch_avg_size = int(values["-BATCH_SIZE-"]) 
    total_rows = len(df) # total number of rows in the input sheet
    current_count = 0 # current progress
    round_size = int(batch_avg_size) * 2 # round size for the two accounts
    rounds_left = math.ceil(total_rows / round_size) # the rounds left to send all msgs

    # Initialize GUI progress indicators
    window["-PROGRESS-"].update(current_count=0, max=total_rows)
    window["-PROGRESS_TEXT-"].update(f"0 / {total_rows}")
    window["-ROUNDS_LEFT-"].update(str(rounds_left))

    # randomize the number of msgs sent
    e = random.randint(max(1, batch_avg_size // 2), batch_avg_size + 2)
    i = 0 # track the batch progress
    wa_account = 1 # wa account/browser to use initially
    controller = WAController(profile_name) # WA controller 

    start_time = time.time()

    controller.controller.ensure_device_lang_is_en()
    for idx, row in df.iterrows():
        msg = None
        res = None
        try:
            if not events.running:  # Stop if global flag is False (Pause is clicked)
                save_excel(df)
                break

             # Skip rows already attempted to send 
            if not pd.isna(row['الحالة']):
                current_count += 1
                continue

            # Extract data from row
            phone_number = str(int(row.iloc[0])).removeprefix("20")
            name = str(row.iloc[1]) or " "
            officer_id_msg = str(int(row.iloc[2])) if not isinstance(row.iloc[2], str) else row.iloc[2]
            
            # Open WA account for batch
            if (not i) or (i % (batch_avg_size + e) == 0):
                controller.open_wa(wa_account)
            
            # Send content via WAController
            contact_added = False
            is_egyptian = phone_number.startswith(("10", "11", "12", "15"))
            try:
                # Add the officer contact or find it on WA
                res, msg = controller.add_contact(phone_number, officer_id_msg)
                # If the contact was found on WA proceed
                if res:
                    contact_added = True
                    # Send the msg to the officer
                    res, msg = controller.send_content(officer_id_msg, name, doc_type)
                    # If the numebr is not a foriegn number then it's added in the contacts
            finally:
                # then delete it after sending the msg 
                if contact_added and is_egyptian:
                    controller.delete_contact()

            # Reset the WA UI by clicking on the msgs icon
            # And close the currently opened chat
            controller.reset_wa()
            controller.close_chat()
            # Update the status of the current row to be saved later 
            # df.loc[idx, "الحالة"] = msg
            if msg is not None:
                df.loc[idx, "الحالة"] = msg
            else:
                df.loc[idx, "الحالة"] = "لم يتم التنفيذ"

            # --- Update GUI progress ---
            current_count = idx + 1
            elapsed = time.time() - start_time
            avg_per_msg = elapsed / current_count
            remaining_time_sec = avg_per_msg * (total_rows - current_count)
            rounds_left = math.ceil((total_rows - current_count) / round_size)
            est_text = f"{remaining_time_sec/60:.1f} دقيقة"
            
            window["-PROGRESS-"].update(current_count=current_count)
            window["-PROGRESS_TEXT-"].update(f"{current_count} / {total_rows}")
            window["-EST_TIME-"].update(est_text)
            window["-ROUNDS_LEFT-"].update(str(rounds_left))

            # Handle batch completion and wait
            i += 1
            if i >= (batch_avg_size + e):
                if wa_account == len(controller.accounts):
                    batch_wait = random.uniform(
                        float(values["-BATCH_WAIT_MIN-"]) * 60,
                        float(values["-BATCH_WAIT_MAX-"]) * 60
                    )
                    save_excel(df)
                    successfully_sent, pending_sent, failed_sent = calculate_stats(df)
                    window.write_event_value("-BATCH BREAK-", (successfully_sent, pending_sent, failed_sent, batch_wait))
                    time.sleep(batch_wait)

                i = 0
                e = random.randint(max(1, batch_avg_size // 2), batch_avg_size + 2)
                wa_account = wa_account % len(controller.accounts) + 1
            else:
                # Random wait between messages
                msg_wait = random.uniform(
                    float(values["-MSG_WAIT_MIN-"]),
                    float(values["-MSG_WAIT_MAX-"])
                )
                time.sleep(msg_wait)

             # Allow GUI to refresh and check for closure
            event, _ = window.read(timeout=0)
            if event == sg.WIN_CLOSED or event == "-CANCEL-":
                save_excel(df)
                break
                
    
        except Exception as exception:
            # Handle unexpected failures
            df.loc[idx, "الحالة"] = f"فشل غير متوقع - {str(exception)}"
            save_excel(df)
            # controller.close_wa()
            # controller.open_wa(wa_account)


    # Finalize execution
    events.running = False
    window["-PAUSE-"].update(disabled=True)
    window["-EXECUTE-"].update(disabled=False)
    save_excel(df)
    successfully_sent, pending_sent, failed_sent = calculate_stats(df)
    if current_count == total_rows:
        window.write_event_value("-THREAD DONE-", ("DONE", successfully_sent, pending_sent, failed_sent, None))
    else:
        window.write_event_value("-THREAD DONE-", ("PAUSED", successfully_sent, pending_sent, failed_sent, None))


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
