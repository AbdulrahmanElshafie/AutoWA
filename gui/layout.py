"""
layout.py

This module defines the graphical user interface (GUI) layout for the application
using FreeSimpleGUI.

The layout is declarative and divided into logical sections (frames) that group
related controls together, such as:
- File and folder paths
- Timing / typing profiles
- Execution and batching options
- Progress tracking
- Important usage notes

This file contains:
- No business logic
- No execution code
- No event handling

It only defines *what* the GUI looks like.
"""


import FreeSimpleGUI as sg
from .helpers import load_config, load_messages

# Load persisted configuration (paths, profiles, etc.)
# This allows the GUI to preload previously saved values
config = load_config()
messages = load_messages()
template_keys = list(messages.keys())


# -------------------------------------------------------------------
# Paths Configuration Layout
# -------------------------------------------------------------------
# Allows the user to:
# - Select permits directory
# - Select seglat directory
# - Select Excel input file
# These values are later validated and saved by GUI helpers.
paths_layout = [
    # Paths selection
    [sg.Text("Data File (CSV):"), sg.Input(config.get("sheet_file") or "", key="-SHEET-"), sg.FileBrowse("Browse...", file_types=(("CSV Files", "*.csv"),))],
    # Browsers Selection
    [sg.Text("Browsers:"), sg.Listbox(["Default Browser", "Chrome", "Edge"], default_values=config.get("browsers", ["Default Browser"]), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(20, 3), key="-BROWSERS-", enable_events=True)],
    # Confirm and persist selected paths
    [sg.Button("Confirm Paths", key="-CONFIRM_PATHS-")]
]

# -------------------------------------------------------------------
# Typing / Timing Profiles Layout
# -------------------------------------------------------------------
# Allows the user to:
# - Select a typing speed profile
# - Preview profile parameters
# - Add, edit, or delete profiles
#
# Profiles control typing speed, wait times, and human-like delays
# used by the WhatsApp automation engine.
profiles_layout = [
    # Dropdown to select an existing timing profile
    [sg.Text("Typing Speed Profile:"), sg.Combo(list(config["time_profiles"].keys()), key="-PROFILE-", enable_events=True)],
    # Read-only preview of the selected profile values
    [sg.Multiline("", size=(40,4), key="-PROFILE_PREVIEW-", disabled=True)],
    # Profile management actions
    [sg.Button("Add Profile"), sg.Button("Edit Profile"), sg.Button("Delete Profile")]
]

# -------------------------------------------------------------------
# Template Manager Layout
# -------------------------------------------------------------------
# Allows the user to:
# - Add, edit, delete message templates
# - View and modify variants for a selected template
templates_layout = [
    [sg.Text("Templates:"), sg.Combo(template_keys, key="-TEMPLATE_SELECT-", enable_events=True, size=(30, 1))],
    [sg.Button("Add Template"), sg.Button("Edit Template"), sg.Button("Delete Template")],
    [sg.Text("Message Variants:")],
    [sg.Listbox(values=[], key="-VARIANTS_LIST-", size=(50, 5), enable_events=True)],
    [sg.Button("Add Variant"), sg.Button("Edit Variant"), sg.Button("Delete Variant")]
]

# -------------------------------------------------------------------
# Operations & Execution Layout
# -------------------------------------------------------------------
# This is the main control panel for execution.
# It allows the user to:
# - Select sending type (permit / seglat / message)
# - Configure delays and batch sizes
# - Start, pause, resume, or restart execution
# - Monitor progress and estimated time
ops_layout = [
    # Instructions popup
    [sg.Button("Instructions", key="-INSTRUCTIONS-")],
    # Total messages counter (calculated elsewhere)
    [sg.Text("Total Messages: 0", key="-TOTAL_COUNT-")],
    # Message Mode selection
    [sg.Text("Message Mode:")],
    [sg.Radio("Fixed Message", "MSG_MODE", key="-MSG_FIXED-", enable_events=True, default=True),
     sg.Radio("Template", "MSG_MODE", key="-MSG_TEMPLATE-", enable_events=True),
     sg.Radio("Document Only", "MSG_MODE", key="-MSG_DOC_ONLY-", enable_events=True)],
     
    # Dynamic Message Inputs (starts showing fixed message input)
    [sg.pin(sg.Column([
        [sg.Text("Fixed Message Content:")],
        [sg.Multiline("", key="-FIXED_TXT-", size=(40, 4))]
    ], key="-COL_FIXED-", visible=True))],
    
    [sg.pin(sg.Column([
        [sg.Text("Select Template:")],
        [sg.Combo(template_keys, key="-SEL_MSG_TEMPLATE-", size=(30, 1), enable_events=True)],
        [sg.Text("Select Variant (or Random):")],
        [sg.Combo([], key="-SEL_VARIANT-", size=(30, 1), enable_events=True), sg.Checkbox("Random", key="-CHK_RANDOM_VAR-", default=True, enable_events=True)]
    ], key="-COL_TEMPLATE-", visible=False))],

    # Document Mode selection
    [sg.Text("Document Mode:")],
    [sg.Radio("None", "DOC_MODE", key="-DOC_NONE-", enable_events=True, default=True),
     sg.Radio("Fixed", "DOC_MODE", key="-DOC_FIXED-", enable_events=True),
     sg.Radio("Variable (Match Contact)", "DOC_MODE", key="-DOC_VAR-", enable_events=True)],
     
    # Dynamic Document Inputs
    [sg.pin(sg.Column([
        [sg.Text("Select Fixed Document:"), sg.Input(config.get("fixed_doc_path") or "", key="-FIXED_DOC_IN-"), sg.FileBrowse("Browse...")]
    ], key="-COL_DOC_FIXED-", visible=False))],
    # Message wait time (seconds) – randomized between min & max
    [sg.Text("Msg Wait (sec):"), 
     sg.Input(key="-MSG_WAIT_MIN-", size=(5,1), enable_events=True, tooltip="Minimum", default_text=5), 
     sg.Input(key="-MSG_WAIT_MAX-", size=(5,1), enable_events=True, tooltip="Maximum", default_text=10)],
    # Batch wait time (minutes) – randomized between min & max
    [sg.Text("Batch Wait (min):"), 
     sg.Input(key="-BATCH_WAIT_MIN-", size=(5,1), enable_events=True, tooltip="Minimum", default_text=10), 
     sg.Input(key="-BATCH_WAIT_MAX-", size=(5,1), enable_events=True, tooltip="Maximum", default_text=20)],
    # Average batch size (actual size is randomized around this value)
    [sg.Text("Batch Size:"), sg.Input(key="-BATCH_SIZE-", enable_events=True, default_text=5),],
    # Per-round stats
    [sg.Text("Messages Per Round: 0", key="-TOTAL_PER_ROUND-"),
     sg.Text("Rounds Left: 0", key="-ROUNDS_LEFT-")],
    # Estimated remaining execution time
    [sg.Text("Estimated Execution Time:"), sg.Text("0 minutes", key="-EST_TIME-")],
    # Progress indicators
    [sg.Text("Progress:"), sg.Text("0 / 0", key="-PROGRESS_TEXT-")],
    # Horizontal progress bar (updated during execution)
    [sg.ProgressBar(max_value=100, orientation='h', size=(40, 20), key="-PROGRESS-")],
    # Primary execution controls
    [sg.Button("Execute / Resume", key="-EXECUTE-", size=(15, 2), button_color=("white", "green")),
     sg.Button("Refresh Data", key="-UPDATE_SHEET-", size=(15, 2)),
     sg.Button("Cancel", key="-CANCEL-", size=(15, 2), button_color=("white", "red"))],
     # Secondary execution controls
     [sg.Button("Pause", key="-PAUSE-", size=(15, 1)), 
      sg.Button("Restart", key="-RESTART-", size=(15, 1))]
]

# -------------------------------------------------------------------
# Important Notes Layout
# -------------------------------------------------------------------
important_notes_layout = [
    [sg.Multiline(
        "1- Please select the required configuration directories correctly.\n"
        "2- Ensure the Jobs Data File (CSV) is closed before starting execution.\n"
        "3- Do not forcibly close the application during processing.\n"
        "4- Validate the selected operation configurations mode.\n"
        "5- Please refrain from moving the mouse during GUI macro hooks (if any).\n"
        "6- Ensure that edge browser starts up in dark mode defaults.",
        size=(40, 6),
        disabled=True,
        no_scrollbar=True,
        font=("bold", 12)
    )]
]

# -------------------------------------------------------------------
# Left Column: Managers & Instructions
# -------------------------------------------------------------------
left_col = [
    [sg.Frame("Typing Speed Profiles", profiles_layout, font=("bold", 10))],
    [sg.Frame("Template Manager", templates_layout, font=("bold", 10))],
    [sg.Frame("Important Notes", important_notes_layout, title_color="darkred", font=("bold", 10))]
]
# -------------------------------------------------------------------
# Right Column: Main Execution Flow
# -------------------------------------------------------------------
right_col = [
    [sg.Frame("1. Settings and Paths", paths_layout, font=("bold", 10))],
    [sg.Frame("2. Operations", ops_layout, font=("bold", 10))]
]

# -------------------------------------------------------------------
# Main Window Layout (Two Columns)
# -------------------------------------------------------------------
layout = [
    [sg.Column(right_col, element_justification='c', vertical_alignment='t'), 
     sg.VSeperator(), 
     sg.Column(left_col, element_justification='c', vertical_alignment='t')]
]

