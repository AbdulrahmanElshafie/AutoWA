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
from analytics.analyzer import get_full_analytics, load_logs
from monitoring.health import get_system_health, get_alert_log_details
from icons_management.logic import list_icons, list_icon_images, delete_icon_image, list_pending_recoveries, delete_recovery, save_cropped_image_to_icon
from icons_management.gui import PREVIEW_W, PREVIEW_H
import base64
from PIL import Image
import io

# Global flag to indicate if the sending process is currently running
running = False  
crop_state = {
    'drag_start': None, 'rect_id': None,
    'img_w': 0, 'img_h': 0,
    'path': None,       # path to original full snapshot
    'full_bio': None,   # bytes of the scaled full image (600x400)
    'box': None,        # confirmed drag box in display coords
    'crnt': None,       # PIL Image currently shown in the graph (active crop)
    'crnt_bio': None,   # cached PNG bytes of crnt letterboxed at 600x400
    'undo_stack': [],   # stack of (pil, bio) tuples — push old crnt on Crop
    'redo_stack': [],   # stack of (pil, bio) tuples — push old crnt on Undo
}
# Maps each alert display string -> full detail message shown on click
alert_details = {}

def _render_crop_to_bytes(cropped_pil, out_bio=None):
    """
    Letterbox a cropped PIL Image into a 600x400 canvas (black bars).
    Writes PNG bytes into out_bio if provided, otherwise a new BytesIO.
    Returns the BytesIO with position at the start.
    """
    CANVAS_W, CANVAS_H = 600, 400
    thumb = cropped_pil.copy()
    thumb.thumbnail((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (CANVAS_W, CANVAS_H), (0, 0, 0))
    x_off = (CANVAS_W - thumb.width) // 2
    y_off = (CANVAS_H - thumb.height) // 2
    canvas.paste(thumb, (x_off, y_off))
    if out_bio is None:
        out_bio = io.BytesIO()
    canvas.save(out_bio, format='PNG')
    out_bio.seek(0)
    return out_bio


def _render_crop_preview(window, cropped_pil):
    """
    Render a cropped PIL Image in the 600x400 crop Graph canvas (letterboxed).
    Also updates crop_state['crnt_bio'] cache.
    """
    bio = _render_crop_to_bytes(cropped_pil)
    data = bio.read()
    crop_state['crnt_bio'] = data
    graph = window['-CROP_GRAPH-']
    graph.erase()
    graph.draw_image(data=data, location=(0, 0))



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
    Groups of related events are collected together:
    1. Application & Path Configuration
    2. Typing Speed Profiles Management
    3. Execution Planning & Estimates
    4. Message Template Management 
    5. UI Mode Visibility Toggles
    6. Execution Controls
    7. Analytics & System Health Monitoring
    8. Target Icons Management
    9. Snapshot Recovery & Image Cropping
    """

    # Uses a global variable 'running' for external access if needed. 
    global running

    # =========================================================================
    # GROUP 1: APPLICATION & PATH CONFIGURATION EVENTS
    # =========================================================================

    if event == "-CONFIRM_PATHS-":
        # Logic: Update the configuration dictionary with the paths provided in the GUI inputs.
        # This includes the default document path, the Excel sheet path, and the number of active browser instances.
        config["fixed_doc_path"] = values["-FIXED_DOC_IN-"]
        config["sheet_file"] = values["-SHEET-"]
        config["browsers"] = values["-BROWSERS-"]
        save_config(config)
        sg.popup("Paths saved successfully!") # Notify user paths saved

    elif event == "-INSTRUCTIONS-":
        # Logic: Load the text from the instructions file and display it in a scrolled popup window.
        # This provides the user with an in-app guide on how to use the application.
        instructions_text = load_instructions()
        sg.popup_scrolled(
            instructions_text,
            title="Application Instructions",
            size=(70, 20),
            font=("bold", 12)
        )   

    # =========================================================================
    # GROUP 2: TYPING SPEED PROFILES MANAGEMENT
    # =========================================================================

    elif event == "-PROFILE-":
        # Logic: When a user selects a typing speed profile from the dropdown,
        # fetch its corresponding delay values (fast, normal, slow, distracted) 
        # from the configuration and display them in the preview text box.
        name = values["-PROFILE-"]
        p = config["time_profiles"].get(name)
        if p:
            txt = "\n".join([f"{k}: {v} sec" for k,v in p.items()])
            window["-PROFILE_PREVIEW-"].update(txt)

    elif event in ("Add Profile", "Edit Profile"):
        # Logic: Open a modal window allowing the user to create a new typing speed profile
        # or edit an existing one. Validates inputs and converts time values into seconds 
        # before saving them back into the configuration file.
        if event == "Edit Profile":
            name = values["-PROFILE-"]
            if not name:
                sg.popup("Select a typing speed profile to edit.")
                return
            existing = config["time_profiles"].get(name, {})
        else:
            name = ""
            existing = {"fast": "", "normal": "", "slow": "", "distracted": ""}

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
            if event == "Edit Profile" and name != v["-N-"]:
                config["time_profiles"].pop(name, None)
            config["time_profiles"][v["-N-"]] = {
                "fast": to_seconds(v["-FAST_VAL-"], v["-FAST_UNIT-"]),
                "normal": to_seconds(v["-NORMAL_VAL-"], v["-NORMAL_UNIT-"]),
                "slow": to_seconds(v["-SLOW_VAL-"], v["-SLOW_UNIT-"]),
                "distracted": to_seconds(v["-DISTRACTED_VAL-"], v["-DISTRACTED_UNIT-"])
            }
            save_config(config)
            window["-PROFILE-"].update(values=list(config["time_profiles"].keys()), value=v["-N-"])
            txt = "\n".join([f"{k}: {v} sec" for k,v in config["time_profiles"][v["-N-"]].items()])
            window["-PROFILE_PREVIEW-"].update(txt)
        pw.close()

    elif event == "Delete Profile":
        # Logic: Delete the currently selected typing speed profile from the configuration
        # after asking the user for confirmation. It then clears the UI selection.
        name = values["-PROFILE-"]
        if not name:
            sg.popup("Select a typing speed profile to delete.")
        else:
            if sg.popup_yes_no(f"Are you sure you want to delete {name}?") == "Yes":
                config["time_profiles"].pop(name, None)
                save_config(config)
                window["-PROFILE-"].update(values=list(config["time_profiles"].keys()), value="")
                window["-PROFILE_PREVIEW-"].update("")

    # =========================================================================
    # GROUP 3: EXECUTION PLANNING & ESTIMATES
    # =========================================================================

    elif event in ("-MSG_WAIT_MIN-", "-MSG_WAIT_MAX-", "-BATCH_WAIT_MIN-", "-BATCH_WAIT_MAX-", "-BATCH_SIZE-", "-UPDATE_SHEET-", "-BROWSERS-"):
        # Logic: Whenever the user changes parameters that affect execution time (wait delays, batch sizes, browser instances)
        # or forces a sheet update, this block recalculates:
        # 1. Total records remaining in the Excel sheet.
        # 2. Estimated execution time based on average wait delays.
        # 3. Total messages processed per round and the remaining rounds to completion.
        sheet = config.get("sheet_file")
        if sheet and os.path.exists(sheet):
            df_full = pd.read_csv(sheet)
            refresh_total_count(window, df_full) 
        else:
            if event == "-UPDATE_SHEET-": 
                sg.popup("Input data file not found.")

        avg_msg_wait = 0
        avg_batch_wait = 0
        if values.get("-MSG_WAIT_MIN-") and values.get("-MSG_WAIT_MAX-"):
            avg_msg_wait = (float(values["-MSG_WAIT_MIN-"]) + float(values["-MSG_WAIT_MAX-"])) / 2
        if values.get("-BATCH_WAIT_MIN-") and values.get("-BATCH_WAIT_MAX-"):
            avg_batch_wait = ( (float(values["-BATCH_WAIT_MIN-"]) + float(values["-BATCH_WAIT_MAX-"])) / 2 ) * 60

        num_accounts = len(values.get("-BROWSERS-") or [1])

        est = estimate_time(window["-TOTAL_COUNT-"].DisplayText.split(": ")[1],
                            values.get("-BATCH_SIZE-", 5), avg_msg_wait, avg_batch_wait, num_accounts)
        window["-EST_TIME-"].update(est)
        
        try:
            batch_size = int(values.get("-BATCH_SIZE-", 5))
            total_per_round = batch_size * num_accounts
            total_rows = int(window["-TOTAL_COUNT-"].DisplayText.split(": ")[1])
            rounds_left = math.ceil(total_rows / total_per_round) if total_per_round > 0 else 0
        except:
            total_per_round = 0
            rounds_left = 0

        display_total = "More than 99" if total_per_round > 99 else str(total_per_round)
        window["-TOTAL_PER_ROUND-"].update(f"Messages Per Round: {display_total}")
        window["-ROUNDS_LEFT-"].update(f"Rounds Left: {rounds_left}")

    # =========================================================================
    # GROUP 4: MESSAGE TEMPLATE MANAGEMENT
    # =========================================================================

    elif event == "-TEMPLATE_SELECT-":
        # Logic: When a template is selected in the Template Manager, load and display 
        # all text variants associated with that template in the variants listbox.
        selected = values["-TEMPLATE_SELECT-"]
        messages = load_messages()
        if selected and selected in messages:
            variants = messages[selected].get("variants", [])
            window["-VARIANTS_LIST-"].update(values=variants)
        else:
            window["-VARIANTS_LIST-"].update(values=[])
            
    elif event == "Add Template":
        # Logic: Prompts the user for a new template code name and display title.
        # Creates a new empty template entry in the messages configuration file.
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
        # Logic: Prompts the user to modify the display title of the currently selected template.
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
        # Logic: After confirmation, deletes the entire selected template and its variants from the configuration.
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
        # Logic: Prompts the user to enter the body text for a new variant, then saves it
        # to the currently selected template and updates the UI listbox.
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
        # Logic: Prompts the user to modify the body text of an existing template variant.
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
        # Logic: After confirmation, deletes the selected variant from the template.
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

    # =========================================================================
    # GROUP 5: UI MODE VISIBILITY TOGGLES
    # =========================================================================

    elif event in ("-MSG_FIXED-", "-MSG_TEMPLATE-", "-MSG_DOC_ONLY-"):
        # Logic: Toggles the visibility of different UI columns (fixed message vs template layout)
        # depending on the user's choice of sending mode.
        window["-COL_FIXED-"].update(visible=values["-MSG_FIXED-"])
        window["-COL_TEMPLATE-"].update(visible=values["-MSG_TEMPLATE-"])
    
    elif event in ("-DOC_NONE-", "-DOC_FIXED-", "-DOC_VAR-"):
        # Logic: Toggles the visibility of the document selection UI column depending on
        # whether the user chooses to attach a fixed document or not.
        window["-COL_DOC_FIXED-"].update(visible=values["-DOC_FIXED-"])
        
    elif event == "-SEL_MSG_TEMPLATE-":
        # Logic: When a user selects a template in the main "Send Messages" tab,
        # update the specific variants dropdown to show available choices for that template.
        messages = load_messages()
        cur_t = values["-SEL_MSG_TEMPLATE-"]
        if cur_t in messages:
            window["-SEL_VARIANT-"].update(values=messages[cur_t]["variants"])
            
    elif event == "-SEL_VARIANT-":
        # Logic: If the user selects a specific variant, uncheck the 'Send Random Variant' checkbox.
        if values["-SEL_VARIANT-"]:
            window["-CHK_RANDOM_VAR-"].update(value=False)
            
    elif event == "-CHK_RANDOM_VAR-":
        # Logic: If the user checks the 'Send Random Variant' checkbox, clear the specific variant dropdown selection.
        if values["-CHK_RANDOM_VAR-"]:
            window["-SEL_VARIANT-"].update(value="")

    # =========================================================================
    # GROUP 6: EXECUTION CONTROLS
    # =========================================================================

    elif event == "-EXECUTE-":
        # Logic: Triggers the main sending loop. The calling code intercepts 'EXECUTE' 
        # to transition the application into running state.
        return 'EXECUTE'

    elif event == "-CANCEL-":
        # Logic: User clicked the cancel/exit button. Returning 'CANCEL' breaks the GUI loop.
        return "CANCEL"
        
    elif event == "-PAUSE-":
        # Logic: Pauses the sending process mid-execution. Flips the global `running` flag
        # to False so the background thread stops sending, and toggles UI button states.
        if running:
            running = False
            window["-PAUSE-"].update(disabled=True)
            window["-EXECUTE-"].update(disabled=False)
        return None

    elif event == "-RESTART-":  
        # Logic: Wipes the progress from the Excel tracking file by resetting all statuses
        # to 'pending'. This essentially forces the execution process to start over from row 1.
        if sg.popup_yes_no("Are you sure you want to restart execution from entirely scratch?")=="Yes": 
            excel_file_path = config.get("sheet_file")
            if excel_file_path and os.path.exists(excel_file_path):
                df = pd.read_csv(excel_file_path)
                if 'status' in df.columns:
                    df['status'] = 'pending'
                if 'status_message' in df.columns:
                    df['status_message'] = ''
                df.to_csv(excel_file_path, index=False)
                sg.popup("Records have been reset successfully.")
                window["-PAUSE-"].update(disabled=False)
                window["-EXECUTE-"].update(disabled=True)
                return "RESTART"
            else:
                sg.popup("Input data file not found.")
                return None

    # =========================================================================
    # GROUP 7: ANALYTICS & SYSTEM HEALTH MONITORING
    # =========================================================================

    elif event == '-REFRESH_ANALYTICS-':
        # Logic: Parses the structured execution JSON logs to compute KPI metrics like total actions, 
        # success rates, and throughput (messages per minute) and updates the analytics dashboard labels.
        stats = get_full_analytics("logs/execution_log.jsonl")
        sr = stats.get('success_rate', 0)
        total = stats.get('total', 0)
        window['-TOTAL_ACTIONS-'].update(total)
        window['-FAILURES-'].update(stats.get('failures', 0))
        window['-TOTAL_MESSAGES-'].update(stats.get('total_messages', 0))
        window['-SUCCESS_RATE-'].update(f"{sr}%")
        error_rate = 0.0 if total == 0 else round(100.0 - float(sr), 2)
        window['-ERROR_RATE-'].update(f"{error_rate}%")
        window['-AVG_DURATION-'].update(f"{stats.get('avg_duration', 0)}s")
        
        throughput_data = stats.get('throughput', {})
        if isinstance(throughput_data, dict):
            window['-THROUGHPUT_ALL-'].update(f"All Time: {throughput_data.get('avg_all', 0)} msg/m")
            window['-THROUGHPUT_CUR-'].update(f"Current Session: {throughput_data.get('avg_current_session', 0)} msg/m")
            window['-THROUGHPUT_LAST-'].update(f"Last Session: {throughput_data.get('avg_last_session', 0)} msg/m")
        else:
            window['-THROUGHPUT_ALL-'].update(f"All Time: {throughput_data} msg/m")
            window['-THROUGHPUT_CUR-'].update("Current Session: 0.0 msg/m")
            window['-THROUGHPUT_LAST-'].update("Last Session: 0.0 msg/m")
        return None
    
    elif event == '-CHECK_HEALTH-':
        # Logic: Evaluates recent operations from the logs to determine the system's "health score"
        # and categorizes any recurring errors or critical faults. Updates the health dashboard UI.
        logs = load_logs("logs/execution_log.jsonl")
        health = get_system_health(logs)
        score = health['score']
        status = health['status']
        color = health['color'] 
        window['-HEALTH_STATUS-'].update(status, text_color=color)
        window['-HEALTH_SCORE-'].update(str(score))

        alert_details.clear()
        alerts = []
        for e in health['critical_issues']:
            label = f"[CRITICAL] {e['type']}"
            alerts.append(label)
            alert_details[label] = get_alert_log_details(
                e['type'], logs,
                jsonl_path="logs/execution_log.jsonl",
                error_log_path="logs/error.log"
            )
        for e in health['repeated_issues']:
            label = f"[REPEATED] {e['type']}"
            alerts.append(label)
            alert_details[label] = get_alert_log_details(
                e['type'], logs,
                jsonl_path="logs/execution_log.jsonl",
                error_log_path="logs/error.log"
            )
        window['-ALERTS-'].update(alerts)
        window['-ALERT_DETAIL-'].update('Click an alert to view details.')
        return None

    elif event == '-ALERTS-' and values['-ALERTS-']:
        # Logic: When the user clicks on a specific alert string, fetch its underlying 
        # log details and error tracebacks and display them in the details box.
        selected = values['-ALERTS-'][0]
        detail = alert_details.get(selected, 'No additional details available.')
        window['-ALERT_DETAIL-'].update(detail)
        return None

    # =========================================================================
    # GROUP 8: TARGET ICONS MANAGEMENT
    # =========================================================================

    elif event == '-REFRESH_ICONS-':
        # Logic: Reload the list of element icons (folders) from the disk and update the UI.
        icons = list_icons()
        window['-ICON_DIR_LIST-'].update(values=icons)
        window.write_event_value('-RELOAD_RECOVERY_QUEUE-', None)
        return None

    elif event == '-ICON_DIR_LIST-' and values['-ICON_DIR_LIST-']:
        # Logic: User selected a specific icon folder. Load the image files contained inside
        # and display the total count status (recommending 3-5 variants).
        icon_name = values['-ICON_DIR_LIST-'][0]
        imgs = list_icon_images(icon_name)
        window['-ICON_IMG_LIST-'].update(values=imgs)
        count = len(imgs)
        color = 'yellow' if count < 3 or count > 5 else 'green'
        window['-ICON_COUNT_STATUS-'].update(f'Count: {count} (Recommended 3-5)', text_color=color)
        return None

    elif event == '-ICON_IMG_LIST-' and values['-ICON_IMG_LIST-']:
        # Logic: User clicked on a specific image inside the icon folder. Generates a letterboxed 
        # preview of the image fitting exactly into a fixed canvas size to prevent UI layout shifts.
        img_path = values['-ICON_IMG_LIST-'][0]
        try:
            with Image.open(img_path) as src:
                src_copy = src.copy()
            src_copy.thumbnail((PREVIEW_W, PREVIEW_H), Image.Resampling.LANCZOS)
            canvas = Image.new('RGB', (PREVIEW_W, PREVIEW_H), (0, 0, 0))
            x_off = (PREVIEW_W - src_copy.width) // 2
            y_off = (PREVIEW_H - src_copy.height) // 2
            canvas.paste(src_copy, (x_off, y_off))
            bio = io.BytesIO()
            canvas.save(bio, format='PNG')
            window['-ICON_PREVIEW-'].update(data=bio.getvalue())
        except Exception as e:
            print('Preview failed', e)
        return None

    elif event == '-DELETE_ICON_IMG-':
        # Logic: Deletes the selected image file from its parent icon folder and triggers a refresh.
        if values['-ICON_IMG_LIST-']:
            delete_icon_image(values['-ICON_IMG_LIST-'][0])
            window.write_event_value('-ICON_DIR_LIST-', None)
        return None

    # =========================================================================
    # GROUP 9: SNAPSHOT RECOVERY & IMAGE CROPPING
    # =========================================================================

    elif event == '-RELOAD_RECOVERY_QUEUE-':
        # Logic: Queries the recovery folder for full-screen snapshots where the system failed 
        # to find elements, loading them into the listbox for manual cropping.
        queue = list_pending_recoveries()
        display_list = [f"{item['element_name']} - {item['snapshot_path']}" for item in queue]
        window['-RECOVERY_LIST-'].update(display_list)
        
        icons = list_icons()
        if icons:
            window['-SAVE_TARGET_ICON-'].update(values=icons, value=icons[0])
        return None

    elif event == '-RECOVERY_LIST-' and values['-RECOVERY_LIST-']:
        # Logic: Loads the selected full-screen snapshot. Downscales it to fit the 600x400 crop graph.
        # Initializes all tracking variables in `crop_state` to start fresh with no active crop.
        selection = values['-RECOVERY_LIST-'][0]
        path = selection.split(" - ")[-1]
        try:
            with Image.open(path) as img:
                w, h = img.size
                crop_state['img_w'] = w
                crop_state['img_h'] = h
                crop_state['path'] = path
                img_resized = img.resize((600, 400), Image.Resampling.LANCZOS)
                bio = io.BytesIO()
                img_resized.save(bio, format='PNG')
                bio.seek(0)
                full_pil = Image.open(bio).copy()  

            bio2 = io.BytesIO()
            full_pil.save(bio2, format='PNG')
            crop_state['full_bio'] = bio2.getvalue()
            crop_state['crnt'] = full_pil   
            crop_state['crnt_bio'] = None   

            graph = window['-CROP_GRAPH-']
            graph.erase()
            graph.draw_image(data=crop_state['full_bio'], location=(0, 0))
            crop_state['drag_start'] = None
            crop_state['rect_id'] = None
            crop_state['box'] = None
            crop_state['crnt_bio'] = None
            crop_state['undo_stack'] = []
            crop_state['redo_stack'] = []
            window['-UNDO_CROP-'].update(disabled=True)
            window['-REDO_CROP-'].update(disabled=True)
        except Exception as e:
            print('Could not load graph preview', e)
        return None

    elif event == '-CROP_GRAPH-':  
        # Logic: Mouse movement on the crop canvas. Records the starting coordinates of a drag.
        # As the user drags, the background image is redrawn to clear the old rectangle, 
        # and a new temporary red rectangle is drawn over the current pointer position.
        mouse = values['-CROP_GRAPH-']
        if mouse == (None, None): return None

        graph = window['-CROP_GRAPH-']

        if crop_state['drag_start'] is None:
            crop_state['drag_start'] = mouse
        else:
            bg = crop_state['crnt_bio'] if crop_state['crnt_bio'] else crop_state['full_bio']
            if bg:
                graph.erase()
                graph.draw_image(data=bg, location=(0, 0))

            pt1 = crop_state['drag_start']
            pt2 = mouse
            top_left = (min(pt1[0], pt2[0]), max(pt1[1], pt2[1]))
            bottom_right = (max(pt1[0], pt2[0]), min(pt1[1], pt2[1]))
            crop_state['rect_id'] = graph.draw_rectangle(top_left, bottom_right, line_color='red')
        return None

    elif event == '-CROP_GRAPH-+UP':  
        # Logic: The user releases the mouse. Finalizes the crop rectangle coordinates,
        # redraws the static red rectangle on the canvas, and saves the points to `crop_state['box']`.
        mouse = values['-CROP_GRAPH-']
        if crop_state['drag_start'] is None or mouse == (None, None):
            return None

        graph = window['-CROP_GRAPH-']
        pt1 = crop_state['drag_start']
        pt2 = mouse

        top_left = (min(pt1[0], pt2[0]), max(pt1[1], pt2[1]))
        bottom_right = (max(pt1[0], pt2[0]), min(pt1[1], pt2[1]))

        if crop_state['rect_id']:
            graph.delete_figure(crop_state['rect_id'])
        crop_state['rect_id'] = graph.draw_rectangle(top_left, bottom_right, line_color='red')

        crop_state['box'] = (pt1, pt2)
        crop_state['drag_start'] = None
        return None

    elif event == '-CROP_RECOVERY-':
        # Logic: Translates the drawn crop rectangle coordinates from the display canvas 
        # onto the actual native dimensions of the image. Crops the image, pushes the prior 
        # state onto the undo stack, clears the redo stack, and updates the display with the new image.
        if not crop_state['box'] or crop_state['crnt'] is None:
            sg.popup('Please draw a crop box first (click and drag).')
            return None

        pt1, pt2 = crop_state['box']
        min_x = min(pt1[0], pt2[0])
        max_x = max(pt1[0], pt2[0])
        min_y = min(pt1[1], pt2[1])
        max_y = max(pt1[1], pt2[1])

        crnt_img = crop_state['crnt']
        CANVAS_W, CANVAS_H = 600, 400
        thumb = crnt_img.copy()
        thumb.thumbnail((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)
        
        x_off = (CANVAS_W - thumb.width) // 2
        y_off = (CANVAS_H - thumb.height) // 2

        thumb_min_x = max(0, min_x - x_off)
        thumb_max_x = min(thumb.width, max_x - x_off)
        thumb_min_y = max(0, min_y - y_off)
        thumb_max_y = min(thumb.height, max_y - y_off)

        if thumb_min_x >= thumb_max_x or thumb_min_y >= thumb_max_y:
            sg.popup('Crop region is outside the image.')
            return None

        scale_x = crnt_img.width / thumb.width
        scale_y = crnt_img.height / thumb.height

        orig_left   = int(thumb_min_x * scale_x)
        orig_right  = int(thumb_max_x * scale_x)
        orig_top    = int(thumb_min_y * scale_y)
        orig_bottom = int(thumb_max_y * scale_y)

        try:
            new_crop = crnt_img.crop((orig_left, orig_top, orig_right, orig_bottom))
        except Exception as e:
            print("Crop failed:", e)
            sg.popup('Crop failed. Please try again.')
            return None

        if crop_state['crnt'] is not None:
            crop_state['undo_stack'].append(crop_state['crnt'])
        crop_state['redo_stack'].clear()

        crop_state['crnt'] = new_crop
        _render_crop_preview(window, new_crop)

        window['-UNDO_CROP-'].update(disabled=not crop_state['undo_stack'])
        window['-REDO_CROP-'].update(disabled=True)
        return None

    elif event == '-UNDO_CROP-':
        # Logic: Pops the previous image state from the undo stack, pushes the current state 
        # to the redo stack, and restores the crop canvas preview to that prior state.
        if crop_state['undo_stack']:
            crop_state['redo_stack'].append(crop_state['crnt'])
            crop_state['crnt'] = crop_state['undo_stack'].pop()
            _render_crop_preview(window, crop_state['crnt'])
            window['-UNDO_CROP-'].update(disabled=not crop_state['undo_stack'])
            window['-REDO_CROP-'].update(disabled=False)
        return None

    elif event == '-REDO_CROP-':
        # Logic: Pops a previously undone state from the redo stack, pushes the current state 
        # back onto the undo stack, and restores the crop canvas preview to that state.
        if crop_state['redo_stack']:
            crop_state['undo_stack'].append(crop_state['crnt'])
            crop_state['crnt'] = crop_state['redo_stack'].pop()
            _render_crop_preview(window, crop_state['crnt'])
            window['-UNDO_CROP-'].update(disabled=False)
            window['-REDO_CROP-'].update(disabled=not crop_state['redo_stack'])
        return None

    elif event == '-CROP_SAVE_RECOVERY-':
        # Logic: Persists the actively cropped image snippet from the canvas into the chosen
        # target icon directory. On success, it resets the entire cropping state machine 
        # to prevent invalid downstream interactions and refreshes the recovery queue.
        if crop_state['crnt'] is None or not crop_state['path']:
            sg.popup('No cropped image ready. Please use the Crop button first.')
            return None

        target = values['-SAVE_TARGET_ICON-']
        if not target:
            sg.popup('Select a target icon folder.')
            return None

        if save_cropped_image_to_icon(crop_state['crnt'], crop_state['path'], target):
            sg.popup(f'Successfully saved to {target}')
            window.write_event_value('-RELOAD_RECOVERY_QUEUE-', None)
            crop_state['crnt'] = None
            crop_state['crnt_bio'] = None
            crop_state['box'] = None
            crop_state['drag_start'] = None
            crop_state['rect_id'] = None
            crop_state['full_bio'] = None
            crop_state['undo_stack'] = []
            crop_state['redo_stack'] = []
            window['-UNDO_CROP-'].update(disabled=True)
            window['-REDO_CROP-'].update(disabled=True)
            window['-CROP_GRAPH-'].erase()
        else:
            sg.popup('Error saving image.')
        return None

    elif event == '-DELETE_RECOVERY-':
        # Logic: Permanently deletes the original snapshot image from the disk, 
        # effectively dismissing the recovery item. Purges all UI crop state variables.
        if values['-RECOVERY_LIST-']:
            selection = values['-RECOVERY_LIST-'][0]
            path = selection.split(" - ")[-1]
            delete_recovery(path)
            window.write_event_value('-RELOAD_RECOVERY_QUEUE-', None)
            crop_state['drag_start'] = None
            crop_state['box'] = None
            crop_state['rect_id'] = None
            crop_state['crnt'] = None
            crop_state['crnt_bio'] = None
            crop_state['full_bio'] = None
            crop_state['undo_stack'] = []
            crop_state['redo_stack'] = []
            window['-UNDO_CROP-'].update(disabled=True)
            window['-REDO_CROP-'].update(disabled=True)
            window['-CROP_GRAPH-'].erase()
        return None

    return None
