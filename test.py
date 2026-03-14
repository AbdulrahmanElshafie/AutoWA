from app.WAController import WAController
import random
import pandas as pd
import json
import time

excel_file_path = r"C:\\Users\\PC\\Desktop\\pdfs.xlsx" # input
df = pd.read_excel(excel_file_path, engine="openpyxl")

batch_avg_size = 2 # input
e = random.randint(-batch_avg_size + 2, (batch_avg_size + 2))
i = 0
wa_account = 2
doc_type = None # seglat, None, permit input

with open("config.json", "r") as f:
    config = json.load(f)
profile =  list(config['time_profiles'].keys())[0] # input
controller = WAController(profile)

import ctypes 
import locale
import pyautogui

def get_device_language():
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    # Get handle of the foreground window
    hwnd = user32.GetForegroundWindow()

    # Get the thread ID of that window
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)

    # Get the keyboard layout (HKL)
    hkl = user32.GetKeyboardLayout(thread_id)

    # Low word = language ID
    lang_id = hkl & 0xFFFF

    # Convert language ID to locale string
    language = locale.windows_locale.get(lang_id)

    return language

def check_device_lang():
    language = get_device_language()

    while language != "en_US":
        print("language", language)
        pyautogui.hotkey("alt", "shift")
        language = get_device_language()

check_device_lang()