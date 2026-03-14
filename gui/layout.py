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
from .helpers import load_config

# Load persisted configuration (paths, profiles, etc.)
# This allows the GUI to preload previously saved values
config = load_config()


# -------------------------------------------------------------------
# Paths Configuration Layout
# -------------------------------------------------------------------
# Allows the user to:
# - Select permits directory
# - Select seglat directory
# - Select Excel input file
# These values are later validated and saved by GUI helpers.
paths_layout = [
    # Permits directory selection
    [sg.Text("مجلد التصاريح:"), sg.Input(config.get("permits_dir") or "", key="-DIR1-"), sg.FolderBrowse()],
    # Seglat directory selection
    [sg.Text("مجلد السجلات:"), sg.Input(config.get("seglat_dir") or "", key="-DIR2-"), sg.FolderBrowse()],
    # Excel sheet selection
    [sg.Text("ملف البيانات:"), sg.Input(config.get("sheet_file") or "", key="-SHEET-"), sg.FileBrowse(file_types=(("Excel", "*.xlsx;*.xls"),))],
    # Confirm and persist selected paths
    [sg.Button("تأكيد المسارات", key="-CONFIRM_PATHS-")]
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
    [sg.Text("ملف سرعة الكتابة:"), sg.Combo(list(config["time_profiles"].keys()), key="-PROFILE-", enable_events=True)],
    # Read-only preview of the selected profile values
    [sg.Multiline("", size=(40,4), key="-PROFILE_PREVIEW-", disabled=True)],
    # Profile management actions
    [sg.Button("إضافة ملف سرعة الكتابة"), sg.Button("تعديل ملف سرعة الكتابة"), sg.Button("حذف ملف سرعة الكتابة")]
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
    [sg.Button("التعليمات", key="-INSTRUCTIONS-")],
    # Total messages counter (calculated elsewhere)
    [sg.Text("عدد الرسائل: 0", key="-TOTAL_COUNT-")],
    # Message type selection (mutually exclusive)
    [sg.Radio("تلقائي", "TYPE", key="-AUTO-", default=True),
    sg.Radio("تصاريح", "TYPE", key="-TYPE_PERMIT-"),
    sg.Radio("نماذج 53 تعبئة", "TYPE", key="-TYPE_SEGLAT-"),
    sg.Radio("رسائل تواصل", "TYPE", key="-TYPE_MSG-")],
    # Message wait time (seconds) – randomized between min & max
    [sg.Text("انتظار الرسالة (ث):"), 
     sg.Input(key="-MSG_WAIT_MIN-", size=(5,1), enable_events=True, tooltip="أدني", default_text=5), 
     sg.Input(key="-MSG_WAIT_MAX-", size=(5,1), enable_events=True, tooltip="أقصي", default_text=10)],
    # Batch wait time (minutes) – randomized between min & max
    [sg.Text("انتظار الجولة (د):"), 
     sg.Input(key="-BATCH_WAIT_MIN-", size=(5,1), enable_events=True, tooltip="أدني", default_text=10), 
     sg.Input(key="-BATCH_WAIT_MAX-", size=(5,1), enable_events=True, tooltip="أقصي", default_text=20)],
    # Average batch size (actual size is randomized around this value)
    [sg.Text("حجم الدفعة:"), sg.Input(key="-BATCH_SIZE-", enable_events=True, default_text=5),],
    # Per-round stats
    [sg.Text("عدد الرسائل لكل جولة: 0", key="-TOTAL_PER_ROUND-"),
     sg.Text("الجولات المتبقية: 0", key="-ROUNDS_LEFT-")],
    # Estimated remaining execution time
    [sg.Text("الوقت المتوقع للتنفيذ:"), sg.Text("0 دقيقة", key="-EST_TIME-")],
    # Progress indicators
    [sg.Text("تقدم الإرسال:"), sg.Text("0 / 0", key="-PROGRESS_TEXT-")],
    # Horizontal progress bar (updated during execution)
    [sg.ProgressBar(max_value=100, orientation='h', size=(40, 20), key="-PROGRESS-")],
    # Primary execution controls
    [sg.Button("تنفيذ/استكمال", key="-EXECUTE-"),
     sg.Button("تحديث الملف", key="-UPDATE_SHEET-"),
     sg.Button("إلغاء", key="-CANCEL-")],
     # Secondary execution controls
     [sg.Button("إيقاف مؤقت", key="-PAUSE-"), 
      sg.Button("إعادة التنفيذ", key="-RESTART-")],

]

# -------------------------------------------------------------------
# Important Notes Layout
# -------------------------------------------------------------------
# Static, read-only instructions meant to:
# - Reduce user errors
# - Protect execution integrity
# - Prevent UI interference during automation
important_notes_layout = [
    [sg.Multiline(
        "1- تأكد من اختيار جميع المسارات بشكل صحيح\n"
        "2- تأكد من غلق ملف Excel قبل التنفيذ\n"
        "3- لا تغلق التطبيق أثناء التنفيذ\n"
        "4- تأكد من اختيار العملية الصحيحة قبل الإرسال\n"
        "5- تأكد من عدم تحريك الماوس بعد بدأ البرنامج\n"
        "6- تأكد من استخدام الوضع المظلم",
        size=(40, 6),
        disabled=True,
        no_scrollbar=True,
        font=("bold", 12)
    )]
]


# -------------------------------------------------------------------
# Main Window Layout
# -------------------------------------------------------------------
# The full GUI is composed of framed sections stacked vertically.
# Each frame represents a logical feature area of the application.
layout = [
    [sg.Frame("المسارات", paths_layout)],
    [sg.Frame("سرعات الكتابة", profiles_layout)],
    [sg.Frame("ملاحظات هامة", important_notes_layout, title_color="darkred")],
    [sg.Frame("العمليات", ops_layout)]
]

