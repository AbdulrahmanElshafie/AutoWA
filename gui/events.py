"""
events.py

This module handles all GUI events for the application. It listens for user interactions
(e.g., button clicks, input changes, profile selection) and updates the GUI components 
accordingly. It also calls helper functions to load/save configuration, update UI labels,
estimate execution time, and manage execution state.

Main function:
- handle_events(event, values, window): Processes GUI events and triggers corresponding actions.

Global variables:
- running (bool): Flag indicating if execution is currently active.

Dependencies:
- FreeSimpleGUI for GUI components
- pandas for reading/updating Excel files
- os for file/path checking
- helpers for configuration, time conversion, and instructions
"""

import FreeSimpleGUI as sg
import pandas as pd
import os
from .layout import config
from .helpers import *
import math

# Global flag to indicate if the sending process is currently running
running = False  

def handle_events(event, values, window):
    """
    Handles GUI events triggered by user interactions.

    Parameters:
    - event (str): The identifier of the event triggered (button click, input change, etc.)
    - values (dict): A dictionary containing all input values from the GUI
    - window (sg.Window): The GUI window object, used to update components

    Returns:
    - 'EXECUTE' if the execution should start
    - 'CANCEL' if the operation was canceled
    - 'RESTART' if the user requests a restart
    - None for other events

    Logic:
    1. Updates paths in config when "-CONFIRM_PATHS-" is triggered.
    2. Updates profile preview when a typing speed profile is selected.
    3. Recalculates estimated time, total per round, and remaining rounds when
       batch/wait inputs or sheet updates occur.
    4. Handles adding, editing, and deleting typing speed profiles with validation.
    5. Manages execution controls: start, pause, cancel, restart.
    6. Displays instructions from a file when "-INSTRUCTIONS-" is triggered.
    """

    # Uses a global variable 'running' for external access if needed. 
    global running

    if event == "-CONFIRM_PATHS-":
        config["fixed_doc_path"] = values["-FIXED_DOC_IN-"]
        config["sheet_file"] = values["-SHEET-"]
        config["browsers"] = values["-BROWSERS-"]
        save_config(config)
        sg.popup("Paths saved successfully!") # Notify user paths saved

    # --- Update typing speed profile preview ---
    elif event == "-PROFILE-":
        name = values["-PROFILE-"]
        p = config["time_profiles"].get(name)
        if p:
            # Display profile values in multiline box
            txt = "\n".join([f"{k}: {v} sec" for k,v in p.items()])
            window["-PROFILE_PREVIEW-"].update(txt)

    # --- Recalculate estimated execution time and update counts ---
    elif event in ("-MSG_WAIT_MIN-", "-MSG_WAIT_MAX-", "-BATCH_WAIT_MIN-", "-BATCH_WAIT_MAX-", "-BATCH_SIZE-", "-UPDATE_SHEET-", "-BROWSERS-"):
        sheet = config.get("sheet_file")
        if sheet and os.path.exists(sheet):
            df_full = pd.read_csv(sheet)
            refresh_total_count(window, df_full) # Update total record count
        else:
            if event == "-UPDATE_SHEET-": # Only show popup on button click, not just writing to wait times.
                sg.popup("Input data file not found.")

        # Compute average wait times per msg and per batch
        avg_msg_wait = 0
        avg_batch_wait = 0
        if values.get("-MSG_WAIT_MIN-") and values.get("-MSG_WAIT_MAX-"):
            avg_msg_wait = (float(values["-MSG_WAIT_MIN-"]) + float(values["-MSG_WAIT_MAX-"])) / 2
        if values.get("-BATCH_WAIT_MIN-") and values.get("-BATCH_WAIT_MAX-"):
            avg_batch_wait = ( (float(values["-BATCH_WAIT_MIN-"]) + float(values["-BATCH_WAIT_MAX-"])) / 2 ) * 60

        num_accounts = len(values.get("-BROWSERS-") or [1])

        # Update estimated time label
        est = estimate_time(window["-TOTAL_COUNT-"].DisplayText.split(": ")[1],
                            values.get("-BATCH_SIZE-", 5), avg_msg_wait, avg_batch_wait, num_accounts)
        window["-EST_TIME-"].update(est)
        
        # Update total rows sent per round and rounds left
        try:
            # Calculate the total rows per round and the required rounds to finish
            batch_size = int(values.get("-BATCH_SIZE-", 5))
            total_per_round = batch_size * num_accounts
            total_rows = int(window["-TOTAL_COUNT-"].DisplayText.split(": ")[1])
            rounds_left = math.ceil(total_rows / total_per_round) if total_per_round > 0 else 0
        except:
            total_per_round = 0
            rounds_left = 0

        # Update the UI
        display_total = "More than 99" if total_per_round > 99 else str(total_per_round)
        window["-TOTAL_PER_ROUND-"].update(f"Messages Per Round: {display_total}")
        window["-ROUNDS_LEFT-"].update(f"Rounds Left: {rounds_left}")

    # --- Add or edit typing speed profile ---
    elif event in ("Add Profile", "Edit Profile"):
        if event == "Edit Profile":
            name = values["-PROFILE-"]
            if not name:
                sg.popup("Select a typing speed profile to edit.")
                return
            existing = config["time_profiles"].get(name, {})
        else:
            name = ""
            existing = {"fast": "", "normal": "", "slow": "", "distracted": ""}

        # Layout for modal input window
        layout_p = [
            [sg.Text("Name:"), sg.Input(name, key="-N-")],
            [sg.Text("Fast"), sg.Input(existing.get("fast",""), key="-FAST_VAL-"), sg.Combo(["ms","s","m"], default_value="s", key="-FAST_UNIT-")],
            [sg.Text("Normal"), sg.Input(existing.get("normal",""), key="-NORMAL_VAL-"), sg.Combo(["ms","s","m"], default_value="s", key="-NORMAL_UNIT-")],
            [sg.Text("Slow"), sg.Input(existing.get("slow",""), key="-SLOW_VAL-"), sg.Combo(["ms","s","m"], default_value="s", key="-SLOW_UNIT-")],
            [sg.Text("Distracted"), sg.Input(existing.get("distracted",""), key="-DISTRACTED_VAL-"), sg.Combo(["ms","s","m"], default_value="s", key="-DISTRACTED_UNIT-")],
            [sg.Button("Save"), sg.Button("Cancel")]
        ]
        pw = sg.Window("Typing Speed Profile", layout_p, modal=True)
        e,v = pw.read()
        if e == "Save":
            # Remove old profile name if renamed
            if event == "Edit Profile" and name != v["-N-"]:
                config["time_profiles"].pop(name, None)
            # Save profile values in seconds
            config["time_profiles"][v["-N-"]] = {
                "fast": to_seconds(v["-FAST_VAL-"], v["-FAST_UNIT-"]),
                "normal": to_seconds(v["-NORMAL_VAL-"], v["-NORMAL_UNIT-"]),
                "slow": to_seconds(v["-SLOW_VAL-"], v["-SLOW_UNIT-"]),
                "distracted": to_seconds(v["-DISTRACTED_VAL-"], v["-DISTRACTED_UNIT-"])
            }
            # Update the configs file
            save_config(config)
            # Update the selection options in the UI
            window["-PROFILE-"].update(values=list(config["time_profiles"].keys()), value=v["-N-"])
            # Refresh preview
            txt = "\n".join([f"{k}: {v} sec" for k,v in config["time_profiles"][v["-N-"]].items()])
            window["-PROFILE_PREVIEW-"].update(txt)
        pw.close()

    # --- Delete typing speed profile ---
    elif event == "Delete Profile":
        name = values["-PROFILE-"]
        # Make sure a profile is selected
        if not name:
            sg.popup("Select a typing speed profile to delete.")
        else:
            # Confirm before deletion
            if sg.popup_yes_no(f"Are you sure you want to delete {name}?") == "Yes":
                # Delete the profile
                config["time_profiles"].pop(name, None)
                save_config(config)
                # Update the UI
                window["-PROFILE-"].update(values=list(config["time_profiles"].keys()), value="")
                window["-PROFILE_PREVIEW-"].update("")

    # --- Template Manager Events ---
    elif event == "-TEMPLATE_SELECT-":
        selected = values["-TEMPLATE_SELECT-"]
        messages = load_messages()
        if selected and selected in messages:
            variants = messages[selected].get("variants", [])
            window["-VARIANTS_LIST-"].update(values=variants)
        else:
            window["-VARIANTS_LIST-"].update(values=[])
            
    elif event == "Add Template":
        messages = load_messages()
        t_name = sg.popup_get_text("New template code name (e.g. permit_msg):")
        if t_name:
            t_title = sg.popup_get_text("Template display title:")
            if t_title:
                messages[t_name] = {"title": t_title, "enabled": True, "variants": []}
                save_messages(messages)
                window["-TEMPLATE_SELECT-"].update(values=list(messages.keys()), value=t_name)
                window["-VARIANTS_LIST-"].update(values=[])

    elif event == "Edit Template":
        messages = load_messages()
        selected = values["-TEMPLATE_SELECT-"]
        if selected and selected in messages:
            t_title = sg.popup_get_text("New template display title:", default_text=messages[selected].get("title", ""))
            if t_title:
                messages[selected]["title"] = t_title
                save_messages(messages)
        else:
            sg.popup("Please select a template to edit.")

    elif event == "Delete Template":
        messages = load_messages()
        selected = values["-TEMPLATE_SELECT-"]
        if selected and selected in messages:
            if sg.popup_yes_no(f"Are you sure you want to delete the template {selected}?") == "Yes":
                messages.pop(selected)
                save_messages(messages)
                window["-TEMPLATE_SELECT-"].update(values=list(messages.keys()), value="")
                window["-VARIANTS_LIST-"].update(values=[])
        else:
            sg.popup("Please select a template to delete.")

    elif event == "Add Variant":
        messages = load_messages()
        selected = values["-TEMPLATE_SELECT-"]
        if selected and selected in messages:
            variant = sg.popup_get_text("Variant body text:")
            if variant:
                messages[selected].setdefault("variants", []).append(variant)
                save_messages(messages)
                window["-VARIANTS_LIST-"].update(values=messages[selected]["variants"])
        else:
            sg.popup("Please select a template first.")

    elif event == "Edit Variant":
        messages = load_messages()
        selected_temp = values["-TEMPLATE_SELECT-"]
        selected_vars = values["-VARIANTS_LIST-"]
        if selected_temp and selected_temp in messages and selected_vars:
            old_variant = selected_vars[0]
            new_variant = sg.popup_get_text("New variant body text:", default_text=old_variant)
            if new_variant:
                idx = messages[selected_temp]["variants"].index(old_variant)
                messages[selected_temp]["variants"][idx] = new_variant
                save_messages(messages)
                window["-VARIANTS_LIST-"].update(values=messages[selected_temp]["variants"])
        else:
            sg.popup("Please select a template and a variant to edit.")

    elif event == "Delete Variant":
        messages = load_messages()
        selected_temp = values["-TEMPLATE_SELECT-"]
        selected_vars = values["-VARIANTS_LIST-"]
        if selected_temp and selected_temp in messages and selected_vars:
            old_variant = selected_vars[0]
            if sg.popup_yes_no("Are you sure you want to delete this variant?") == "Yes":
                messages[selected_temp]["variants"].remove(old_variant)
                save_messages(messages)
                window["-VARIANTS_LIST-"].update(values=messages[selected_temp]["variants"])
        else:
            sg.popup("Please select a template and a variant to delete.")

    # --- Mode Visibility Toggles ---
    elif event in ("-MSG_FIXED-", "-MSG_TEMPLATE-", "-MSG_DOC_ONLY-"):
        window["-COL_FIXED-"].update(visible=values["-MSG_FIXED-"])
        window["-COL_TEMPLATE-"].update(visible=values["-MSG_TEMPLATE-"])
    
    elif event in ("-DOC_NONE-", "-DOC_FIXED-", "-DOC_VAR-"):
        window["-COL_DOC_FIXED-"].update(visible=values["-DOC_FIXED-"])
        
    elif event == "-SEL_MSG_TEMPLATE-":
        messages = load_messages()
        cur_t = values["-SEL_MSG_TEMPLATE-"]
        if cur_t in messages:
            window["-SEL_VARIANT-"].update(values=messages[cur_t]["variants"])
            
    elif event == "-SEL_VARIANT-":
        if values["-SEL_VARIANT-"]:
            window["-CHK_RANDOM_VAR-"].update(value=False)
            
    elif event == "-CHK_RANDOM_VAR-":
        if values["-CHK_RANDOM_VAR-"]:
            window["-SEL_VARIANT-"].update(value="")

    # --- Execute sending msgs and its controls ---
    elif event == "-EXECUTE-":
        # # Turn on the pause option
        # window["-PAUSE-"].update(disabled=False)
        # # Turn off the execution/resume option
        # window["-EXECUTE-"].update(disabled=True)
        return 'EXECUTE'

    # --- Exit the app ---
    elif event == "-CANCEL-":
        return "CANCEL"
        
    # --- Pause the sending process execution ---
    elif event == "-PAUSE-":
        if running:
            running = False
            # Turn off the pause option
            window["-PAUSE-"].update(disabled=True)
            # Turn on the execution/resume option
            window["-EXECUTE-"].update(disabled=False)
        
        return None

     # --- Restart the msgs sending process from zero ---
    
    elif event == "-RESTART-":  
        # Confirm the restart command
        if sg.popup_yes_no("Are you sure you want to restart execution from entirely scratch?")=="Yes": 
            # Get the current progress from the input file
            excel_file_path = config.get("sheet_file")
            if excel_file_path and os.path.exists(excel_file_path):
                df = pd.read_csv(excel_file_path)
                # Delete the progress and save the file
                if 'status' in df.columns:
                    df['status'] = 'pending'
                if 'status_message' in df.columns:
                    df['status_message'] = ''
                df.to_csv(excel_file_path, index=False)
                # Notify the user that the restart is ready
                sg.popup("Records have been reset successfully.")
                # Turn on the pause option
                window["-PAUSE-"].update(disabled=False)
                # Turn off the execution/resume option
                window["-EXECUTE-"].update(disabled=True)
                return "RESTART"
            
            else:
                # If the input file is not found 
                sg.popup("Input data file not found.")
                return None

    # --- Display instructions ---
    if event == "-INSTRUCTIONS-":
        # Load instructions 
        instructions_text = load_instructions()
        # Open a popup for the instructions 
        sg.popup_scrolled(
            instructions_text,
            title="Application Instructions",
            size=(70, 20),
            font=("bold", 12)
        )   


    return None
