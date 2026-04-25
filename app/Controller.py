"""
Controller.py

This module contains the main GUI automation controller built on top of
`pyautogui`. It provides reusable, high-level desktop interaction methods
such as clicking UI elements, typing text, pasting content, and waiting
for screen conditions.

All timing behavior (typing speed, mouse movement delay, waiting pauses)
is delegated to the TimeConroller helper class, allowing behavior to be
profile-driven and configurable.
"""


import pyautogui
from .helpers import TimeConroller
import time
import pyperclip
from gui.helpers import load_config
import os
from logger import log_function
import numpy as np
import ctypes 
import locale
from icons_management.logic import save_failure_snapshot

class GuiController:
    """
    High-level GUI controller responsible for interacting with the desktop
    environment using image recognition and keyboard/mouse automation.

    This class acts as an abstraction layer between:
    - Raw pyautogui calls
    - Higher-level application workflows (sending messages, navigation, etc.)

    Attributes:
        time_controller (TimeConroller):
            Instance responsible for generating timing values based on
            the selected time profile.
    """
    time_controller = None

    def __init__(self, typing_profile='01500816271'):
        """
        Initialize the GUI controller and its timing behavior.

        Loads time profiles from `config.json` and initializes a
        TimeConroller instance using the selected profile.

        Args:
            typing_profile (str, optional):
                Index of the time profile to use from config.json.
                Defaults to 01500816271.
        """
         # Load configuration file containing time profiles
        config = load_config()
        
        # Initialize time controller with selected profile
        profile = config['time_profiles'][typing_profile] if typing_profile in config['time_profiles'].keys() else config['time_profiles']["01500816271"]
        self.time_controller = TimeConroller(profile)

    @log_function
    def get_candidates(self, obj_dir):
        candidates = [obj_dir + f"\\{obj}" for obj in os.listdir(obj_dir)]
        return candidates

    @log_function
    def is_ui_stable(self, delay=2, diff_threshold=2.5):
        """
        Detects whether the UI has stabilized by comparing two screenshots.
        """
        img1 = pyautogui.screenshot()
        time.sleep(delay)
        img2 = pyautogui.screenshot()

        a1 = np.array(img1).astype("int16")
        a2 = np.array(img2).astype("int16")

        diff = np.mean(np.abs(a1 - a2))
        return diff < diff_threshold

    @log_function
    def find_click(self, obj, confidence=0.8, raise_on_fail=True, max_attemps=2, max_wait=3):
        """
        Locate an image on the screen and click its center.

        Each image is retried multiple times before moving to the next option.

        Args:
            obj (str):
                Path to the image used for screen matching.
            confidence (float, optional):
                Matching confidence threshold (0-1).
                Defaults to 0.8.
            raise_on_fail (bool, optional):
                Whether to raise an exception if the image is not found.
                Defaults to True.

        Raises:
            pyautogui.ImageNotFoundException:
                If the image cannot be found and raise_on_fail is True.
        """
        # Determine mouse movement duration from the time profile
        wait_time = self.time_controller.mouse_move()
        candidates = self.get_candidates(obj)

        entry = 0
        while not self.is_ui_stable():
            if entry == max_wait:
                break
            entry += 1
            time.sleep(1)
        for _ in range(max_attemps):
            for c in candidates:
                try:
                    # Locate the image center on the screen
                    attach_doc_x, attach_doc_y = pyautogui.locateCenterOnScreen(c, confidence=confidence, grayscale=True)
                        
                    # Move mouse smoothly and click
                    pyautogui.moveTo(attach_doc_x, attach_doc_y, wait_time, pyautogui.easeOutQuad)
                    pyautogui.click()
                    
                    # Allow UI to react after clicking
                    time.sleep(5)
                    return True
            
                except pyautogui.ImageNotFoundException as e:
                    pass
                    # Wait before retrying detection to wait the UI to finish its animation if available
            
            time.sleep(3)

        """
        screenshot = capture_failure("Timeout_" + os.path.basename(obj)) => take screenshot for revuewal
        learn_icon(obj, screenshot) => Save failed screenshots as candidates + register metadata.
        """
        # Raise error if image was not found
        if raise_on_fail:
            # If raise is provided then icon is important and has to be saved otherwise it's not
            screenshot = save_failure_snapshot(os.path.basename(obj))
            raise pyautogui.ImageNotFoundException(f'FATAL_ERROR: Unable to find icon: {os.path.basename(obj)}')

    @log_function   
    def type(self, txt):
        """
        Type text using keyboard simulation.

        Typing speed is derived from the fast timing profile
        with a capped maximum interval.

        Args:
            txt (str):
                Text to be typed.
        """
        while not self.is_ui_stable():
            break

        self.ensure_device_lang_is_en()
        pyautogui.write(txt, interval=min(self.time_controller.fast()/2.0, 0.3))

    @log_function
    def copy_paste(self, txt):
        """
        Paste text word-by-word using the clipboard.

        The text is split into words and pasted sequentially
        to simulate more natural input behavior.

        This function was made as a workaround for the fact that pyautogui doesn't type in Arabic,
        so we used the clipboard to copy and past each word and to stil simulate the typing on WA
        Args:
            txt (str):
                Text to paste into the active field.
        """
        while not self.is_ui_stable():
            break

        for word in txt.split():
            # Copy word to clipboard
            pyperclip.copy(word + " ")
            time.sleep(0.1)

            # Paste word using keyboard shortcut
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)

        # Apply a typing pause selected from the time profile
        time.sleep(self.time_controller.pick_typing()()) # use the profile times
        
    @log_function
    def click_enter(self):
        """
        Press the Enter key twice with a delay between presses.

        Used to confirm actions or send messages.
        """
        while not self.is_ui_stable():
            break
        
        pyautogui.press('enter', presses=2, interval=5)
           
    @log_function
    def click_esc(self):
        """ 
        Press the Escape key once.

        Used to close dialogs or cancel UI states.
        """
        while not self.is_ui_stable():
            break

        pyautogui.hotkey('esc')

    @log_function
    def close_tab(self):
        """
        Close the currently active tab or window using Ctrl+W.
        """
        while not self.is_ui_stable():
            break

        pyautogui.hotkey('ctrl', 'w')
    
    @log_function
    def wait(self, condition_img, max_attempts=2, max_wait=4, confidence=0.8):
        """
        Wait for a specific UI condition to appear on screen.

        The function repeatedly checks for the presence of an image.

        Args:
            condition_img (str):
                Path to the image used as a condition.
            max_attempts (int, optional):
                Number of attempts per image variant.
                Defaults to 3.

        Returns:
            bool:
                True if the image is detected, False otherwise.
        """
        candidates = self.get_candidates(condition_img)

        entry = 0
        while not self.is_ui_stable():
            if entry == max_wait:
                break
            entry += 1
            time.sleep(1)

        for _ in range(max_attempts):
            for c in candidates:
                try:
                    # Check if the image is present
                    pyautogui.locateOnScreen(c, confidence=confidence)
                    return True
                
                except pyautogui.ImageNotFoundException:
                    pass
            
            time.sleep(3)


        screenshot = save_failure_snapshot(os.path.basename(condition_img))
        # self.IconManagerController.learn_icon(condition_img, screenshot)
        return False

    @log_function
    def get_device_language(self):
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

    @log_function
    def ensure_device_lang_is_en(self):
        language = self.get_device_language()

        while language != "en_US":
            pyautogui.hotkey("alt", "shift")
            language = self.get_device_language()