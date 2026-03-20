"""
helpers.py

This module contains helper functions used across the GUI application for configuration
management, time conversion, execution time estimation, table refreshing, and loading
instructions.

This file works together with the GUI and event-handling code, allowing the app to:
- Persist user settings between sessions.
- Convert user-input time values to seconds for internal use.
- Estimate execution time for batch operations.
- Update the GUI elements dynamically without blocking the interface.
- Display instructions to the user if needed.
"""


import json
import os
import math
from logger import log_function

CONFIG_FILE = "config/config.json"
MESSAGES_FILE = "config/messages.json"

# Default configuration structure to use if config.json is missing or empty
default_config = {
    "sheet_file": "",
    "time_profiles": {},
    "doc_dir": "",
    "fixed_doc_path": "",
    "browsers": [],
    "batch_size": 5,
    "msg_wait_min": 5.0,
    "msg_wait_max": 10.0,
    "batch_wait_min": 10.0,
    "batch_wait_max": 20.0
    }

@log_function
def load_config():
    """
    Load the configuration from CONFIG_FILE (config.json).

    Returns:
        dict: The configuration dictionary loaded from the file.
              If the file does not exist, returns a copy of default_config.
    """
    # Checks if the config file exists.
    if os.path.exists(CONFIG_FILE):
        # Reads JSON from the file if it exists.
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Returns default_config if the file is missing.
    return default_config.copy()

@log_function
def save_config(cfg):
    """
    Save the given configuration dictionary to CONFIG_FILE.

    - Serializes the dictionary as JSON with indentation and UTF-8 encoding.
    - Ensures Arabic text and special characters are correctly saved (ensure_ascii=False).

    Parameters:
        cfg (dict): The configuration dictionary to save.

    Returns:
        None
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

@log_function
def load_messages():
    """
    Load the message templates from MESSAGES_FILE.
    """
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@log_function
def save_messages(msgs):
    """
    Save the given messages dictionary to MESSAGES_FILE.
    """
    if not os.path.exists(os.path.dirname(MESSAGES_FILE)):
        os.makedirs(os.path.dirname(MESSAGES_FILE))
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, indent=4, ensure_ascii=False)

@log_function
def to_seconds(val, unit):
    """
    Convert a value with a time unit to seconds.

    Parameters:
        val (float or str): The numeric time value.
        unit (str): The time unit, can be 'ms' (milliseconds), 'm' (minutes), or anything else (assumed seconds).

    Returns:
        float: The equivalent time in seconds.
               Returns 0 if conversion fails.
    """
    try:
        # Convert val to float.
        v = float(val)
        # Divide by 1000 if unit is milliseconds
        if unit == "ms":
            return v / 1000
        # Multiply by 60 if unit is minutes.
        if unit == "m":
            return v * 60
        # Return the value as-is if unit is seconds or unknown.
        return v
    except:
        # Return 0 on any error
        return 0

@log_function
def estimate_time(actual_rows, batch_size, msg_wait, batch_wait, num_accounts=1):
    """
    Estimate the total execution time for sending messages in batches.

    Parameters:
        actual_rows (int/str): Total number of records/messages to send.
        batch_size (int/str): Number of messages per batch.
        msg_wait (float/str): Delay between individual messages in seconds.
        batch_wait (float/str): Delay between batches in seconds.
        num_accounts (int): Number of selected WhatsApp accounts to run in cycle.

    Returns:
        str: Estimated execution time as a string, e.g., "12.5 minutes".
    """
    # Validate the values sent are numbers
    try:
        actual_rows = int(actual_rows)
        batch_size = int(batch_size)
        msg_wait = float(msg_wait)
        batch_wait = float(batch_wait)
    except:
        return "0 minutes"

    # Calculate the number of messages sent per round (rows_per_round)
    # as the minimum of actual_rows or batch_size * num_accounts
    rows_per_round = min(actual_rows or 1, batch_size * num_accounts) if actual_rows else batch_size * num_accounts # number of rows sent per round for all batches in the round
    # Calculate the number of rounds needed to send all rows.
    rounds = math.ceil(actual_rows/(rows_per_round)) 
    # Short delay: time between individual messages in the round
    short_time_per_msg = (rows_per_round - 1) * msg_wait # short time delay per each msg
    # Long delay: time between rounds
    long_time_per_round = (rounds - 1) * batch_wait # long time delay per each round
    # Total time = base time (rows_per_round * 60) + short delays + long delays
    total_time_in_seconds = rows_per_round * 60 + short_time_per_msg + long_time_per_round # total time
    
    # If any parameter conversion fails, return "0 minutes"
    return f"{total_time_in_seconds / 60:.1f} minutes"

@log_function
def refresh_total_count(window, df):
    """
    Update the total record/message count on the GUI without displaying the table.

    Parameters:
        window (sg.Window): The FreeSimpleGUI window object to update.
        df (pandas.DataFrame): The DataFrame containing the records/messages.

    Returns:
        None
    """
    # Uses a global variable 'total_rows_count' for external access if needed.
    global total_rows_count
    # Calculates the number of rows in the DataFrame.
    total_rows_count  = len(df)
    # Updates the GUI element '-TOTAL_COUNT-' to reflect the current total.
    window["-TOTAL_COUNT-"].update(f"Total Messages: {total_rows_count }")

    
def load_instructions(file_path="gui\\instructions.txt"):
    """
    Load the instructions text from a file.

    Parameters:
        file_path (str): Path to the instructions text file (default: "gui\\instructions.txt").

    Returns:
        str: Contents of the instructions file.
             If file is missing, returns "Instructions file not found."
    """
    try:
        # Tries to open the file with UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as f:
            # Returns its content as a string
            return f.read()
    except FileNotFoundError:
        # Handles FileNotFoundError gracefully by returning a default message.
        return "Instructions file not found."
