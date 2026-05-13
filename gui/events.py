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
from icons_management.logic import list_icons, list_icon_images, delete_icon_image, list_pending_recoveries, delete_recovery, save_recovery_to_icon, crop_snapshot, save_cropped_image_to_icon
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

    # --- Integration Handlers for Tracking Systems ---
    if event == '-REFRESH_ANALYTICS-':
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
        logs = load_logs("logs/execution_log.jsonl")
        health = get_system_health(logs)
        score = health['score']
        status = health['status']
        color = health['color'] 
        window['-HEALTH_STATUS-'].update(status, text_color=color)
        window['-HEALTH_SCORE-'].update(str(score))

        # Build display list and a lookup for full log-enriched details
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
        selected = values['-ALERTS-'][0]
        detail = alert_details.get(selected, 'No additional details available.')
        window['-ALERT_DETAIL-'].update(detail)
        return None

    elif event == '-REFRESH_ICONS-':
        icons = list_icons()
        window['-ICON_DIR_LIST-'].update(values=icons)
        window.write_event_value('-RELOAD_RECOVERY_QUEUE-', None)
        return None

    elif event == '-ICON_DIR_LIST-' and values['-ICON_DIR_LIST-']:
        icon_name = values['-ICON_DIR_LIST-'][0]
        imgs = list_icon_images(icon_name)
        window['-ICON_IMG_LIST-'].update(values=imgs)
        count = len(imgs)
        color = 'yellow' if count < 3 or count > 5 else 'green'
        window['-ICON_COUNT_STATUS-'].update(f'Count: {count} (Recommended 3-5)', text_color=color)
        return None

    elif event == '-ICON_IMG_LIST-' and values['-ICON_IMG_LIST-']:
        img_path = values['-ICON_IMG_LIST-'][0]
        try:
            # Fit image into fixed 300x200 box with letterboxing (black background)
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
        if values['-ICON_IMG_LIST-']:
            delete_icon_image(values['-ICON_IMG_LIST-'][0])
            window.write_event_value('-ICON_DIR_LIST-', None)
        return None

    elif event == '-RELOAD_RECOVERY_QUEUE-':
        queue = list_pending_recoveries()
        display_list = [f"{item['element_name']} - {item['snapshot_path']}" for item in queue]
        window['-RECOVERY_LIST-'].update(display_list)
        
        icons = list_icons()
        if icons:
            window['-SAVE_TARGET_ICON-'].update(values=icons, value=icons[0])
        return None

    elif event == '-RECOVERY_LIST-' and values['-RECOVERY_LIST-']:
        selection = values['-RECOVERY_LIST-'][0]
        path = selection.split(" - ")[-1]
        try:
            with Image.open(path) as img:
                w, h = img.size
                crop_state['img_w'] = w
                crop_state['img_h'] = h
                crop_state['path'] = path
                # Keep a PIL copy of the scaled image as the initial 'crnt' state
                # so the very first crop can push it onto the undo stack
                img_resized = img.resize((600, 400), Image.Resampling.LANCZOS)
                bio = io.BytesIO()
                img_resized.save(bio, format='PNG')
                bio.seek(0)
                full_pil = Image.open(bio).copy()  # detached PIL Image

            # Cache bytes for fast redraw, and PIL for undo state
            bio2 = io.BytesIO()
            full_pil.save(bio2, format='PNG')
            crop_state['full_bio'] = bio2.getvalue()
            crop_state['crnt'] = full_pil   # first crop will push this to undo_stack
            crop_state['crnt_bio'] = None   # no crop preview yet — drag uses full_bio

            graph = window['-CROP_GRAPH-']
            graph.erase()
            graph.draw_image(data=crop_state['full_bio'], location=(0, 0))
            # Full reset for the new image
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

    elif event == '-CROP_GRAPH-':  # Mouse button pressed / dragging
        mouse = values['-CROP_GRAPH-']
        if mouse == (None, None): return None

        graph = window['-CROP_GRAPH-']

        if crop_state['drag_start'] is None:
            # First contact: record the start of the drag
            crop_state['drag_start'] = mouse
        else:
            # Dragging: restore the current background cleanly, then redraw rect
            # Use cached crnt_bio if a crop preview is active, else the full image
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

    elif event == '-CROP_GRAPH-+UP':  # Mouse button released — finalise box
        mouse = values['-CROP_GRAPH-']
        if crop_state['drag_start'] is None or mouse == (None, None):
            return None

        graph = window['-CROP_GRAPH-']
        pt1 = crop_state['drag_start']
        pt2 = mouse

        top_left = (min(pt1[0], pt2[0]), max(pt1[1], pt2[1]))
        bottom_right = (max(pt1[0], pt2[0]), min(pt1[1], pt2[1]))

        # Draw the final confirmed box — do NOT reset the background here
        # so that any active crop preview is preserved
        if crop_state['rect_id']:
            graph.delete_figure(crop_state['rect_id'])
        crop_state['rect_id'] = graph.draw_rectangle(top_left, bottom_right, line_color='red')

        # Store confirmed box and reset drag
        crop_state['box'] = (pt1, pt2)
        crop_state['drag_start'] = None
        return None

    elif event == '-CROP_RECOVERY-':
        # Crop: compute the crop region, update crnt, push old crnt to undo_stack
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

        # Adjust display coords by removing the black bar offsets
        thumb_min_x = max(0, min_x - x_off)
        thumb_max_x = min(thumb.width, max_x - x_off)
        thumb_min_y = max(0, min_y - y_off)
        thumb_max_y = min(thumb.height, max_y - y_off)

        # Check if the crop is completely outside the actual image
        if thumb_min_x >= thumb_max_x or thumb_min_y >= thumb_max_y:
            sg.popup('Crop region is outside the image.')
            return None

        # Scale coordinates from thumbnail size to actual crnt size
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

        # Push current crnt to undo stack (if there is one); clear redo stack
        if crop_state['crnt'] is not None:
            crop_state['undo_stack'].append(crop_state['crnt'])
        crop_state['redo_stack'].clear()

        # Update crnt and show the new crop in the graph
        crop_state['crnt'] = new_crop
        _render_crop_preview(window, new_crop)

        # Enable Undo (we have something to go back to); disable Redo (no forward)
        window['-UNDO_CROP-'].update(disabled=not crop_state['undo_stack'])
        window['-REDO_CROP-'].update(disabled=True)
        return None

    elif event == '-UNDO_CROP-':
        # Undo: push crnt to redo_stack, pop undo_stack into crnt
        if crop_state['undo_stack']:
            crop_state['redo_stack'].append(crop_state['crnt'])
            crop_state['crnt'] = crop_state['undo_stack'].pop()
            _render_crop_preview(window, crop_state['crnt'])
            window['-UNDO_CROP-'].update(disabled=not crop_state['undo_stack'])
            window['-REDO_CROP-'].update(disabled=False)
        return None

    elif event == '-REDO_CROP-':
        # Redo: push crnt to undo_stack, pop redo_stack into crnt
        if crop_state['redo_stack']:
            crop_state['undo_stack'].append(crop_state['crnt'])
            crop_state['crnt'] = crop_state['redo_stack'].pop()
            _render_crop_preview(window, crop_state['crnt'])
            window['-UNDO_CROP-'].update(disabled=False)
            window['-REDO_CROP-'].update(disabled=not crop_state['redo_stack'])
        return None

    elif event == '-CROP_SAVE_RECOVERY-':
        # Save: write the current crnt image to the icon folder
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
            # Full reset after successful save
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
