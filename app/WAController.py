"""
WAController.py

This module contains the WhatsApp-specific automation logic built on top of
the generic GUI controller (GuiController).

WAController is responsible for:
- Opening and closing WhatsApp Web
- Managing browser-specific UI differences
- Adding and deleting contacts
- Preparing and sending messages and documents
- Handling WhatsApp UI workflows using image-based automation

All low-level desktop interactions are delegated to GuiController.
"""

from .Controller import GuiController
import random
import os
import subprocess
import time
import re
from logger import log_function

class WAController:
    """
    WhatsApp automation controller.

    This class orchestrates WhatsApp Web workflows by combining:
    - High-level WhatsApp logic (contacts, messages, files)
    - Low-level GUI automation provided by GuiController

    It is browser-aware and supports multiple WhatsApp accounts
    by mapping them to different browsers.
    """
    
    # Base path for all UI image assets (relative to this file)
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets") + os.sep
    
    """
    =====================
    ==accounts/browsers==
    =====================
    """

    # Mapping WhatsApp account index/name to browser executable
    accounts = {
        "Default Browser": "",
        "Chrome": "chrome.exe",
        "Edge": "msedge.exe",
        # "Firefox": "firefox.exe",
        # "Brave": "brave.exe",
        # "Opera": "opera.exe",
    }
    
    # Browser-specific UI icons (zoom, reset zoom, maximize)
    browser_icons = {
        "Default Browser": ["Zoom", "Reset Zoom", "Maximise Tab"],
        "Chrome": ["Zoom", "Reset Zoom", "Maximise Tab"],
        "Edge": ["Zoom MS", "Reset Zoom MS", "Maximise Tab MS"],
        # "Firefox": ["Zoom", "Reset Zoom", "Maximise Tab"],
        # "Brave": ["Zoom", "Reset Zoom", "Maximise Tab"],
        # "Opera": ["Zoom", "Reset Zoom", "Maximise Tab"],
    }
    # controller = None

    def __init__(self, profile, browser="Default Browser"):
        """
        Initialize the WhatsApp controller.

        Internally creates a GuiController instance that handles
        all desktop interaction.

        Args:
            profile (str or int):
                Index/Name of the timing profile to use.
            browser (str):
                Name of the browser to automate (maps to self.accounts and self.browser_icons).
        """
        self.browser = browser
        self.controller = GuiController(profile)
    
    @log_function
    def reset_zoom(self, account=None):
        """
        Reset browser zoom level for a given account.

        Uses browser-specific zoom and reset icons.

        Args:
            account (int or str, optional):
                WhatsApp account / browser identifier. Defaults to self.browser.
        """
        if account is None or account not in self.browser_icons:
            account = self.browser
        
        icons = self.browser_icons[account]
        self.controller.find_click(self.base_path + icons[0], 0.9, False)
        self.controller.find_click(self.base_path + icons[1], 0.9, False)

    @log_function
    def maximise_tab(self, account=None):
        """
        Maximize the browser tab for better UI consistency.
        
        Uses browser-specific zoom and reset icons.

        Args:
            account (int or str, optional):
                WhatsApp account / browser identifier. Defaults to self.browser.
        """
        if account is None or account not in self.browser_icons:
            account = self.browser
            
        self.controller.find_click(self.base_path + self.browser_icons[account][2], 0.9, False)

    @log_function
    def open_wa(self, wa_account=None):
        """
        Open WhatsApp Web in the specified browser.

        The method:
        - Launches the browser
        - Maximizes the tab
        - Resets zoom
        - Waits for WhatsApp UI to load

        Args:
            wa_account (int or str, optional):
                WhatsApp account / browser identifier. Defaults to self.browser.
        """
        
        # Get the browser used for the call
        if wa_account is None or wa_account not in self.accounts:
            wa_account = self.browser
            
        account = self.accounts[wa_account]

        # Open WhatsApp Web via PowerShell
        executable_str = account if account else "msedge" if self.browser == "Edge" else "chrome" if self.browser == "Chrome" else "start"
        
        if executable_str == "start":
            powershell_command = f'powershell -Command "Start-Process \'https://web.whatsapp.com/\'"'
        else:
            powershell_command = f'powershell -Command "Start-Process {executable_str} \'https://web.whatsapp.com/\'"'
            
        subprocess.run(powershell_command, shell=True)

        # Wait till the command is executed 
        time.sleep(3)

        # Reset the browser tab and zoom 
        self.maximise_tab(wa_account)        
        self.reset_zoom(wa_account)
        
        # Wait until WhatsApp main UI appears
        self.controller.wait(self.base_path + "WA", confidence=0.5)
        
    @log_function
    def close_wa(self):
        """
        Close the WhatsApp Web tab.
        """
        self.controller.close_tab()
        time.sleep(5)

    @log_function
    def add_contact(self, num, contact_name):
        """
        Add or open a WhatsApp contact.

        Behavior depends on the phone number format:
        - international numbers are searched directly
        - Non-International numbers are added as new contacts

        Args:
            num (str):
                Phone number to add or search.
            name (str):
                Contact name (used when saving new contact).

        Returns:
            tuple (bool, str):
                Success status and descriptive message stating the results for the add/search attempt.
        """
        
        """
        TODO: Add handling all numbers across the globe 
        STEPS: 
            1. Detect the country using the code in the number
            2. Pick the country
            3. Type the number
            4. The rest is the same
        """
        try:
            # Click the new chat icon to view the add & ssearch number options
            self.controller.find_click(self.base_path + "New Chat")
            
            # Handle international numbers
            if num[0] != '1':
                # Type the number in the search box to find it on WA
                self.controller.type(num)

                # Wait for the results to be shown and if the number is on WA open a chat with it
                if self.controller.wait(self.base_path + "Number Search Result", confidence=0.6):
                    # Open the chat with the number 
                    self.controller.find_click(self.base_path + "Number Search Result", confidence=0.6)
                    return True, "Chat opened"
                return False, "Number not on WhatsApp"

            # Add new contact flow
            # Click add a new contact
            self.controller.find_click(self.base_path + "New Contact", 0.95)            
            # Find the phone number box
            self.controller.find_click(self.base_path + "Phone", 0.9)
            # Type the phone number 
            self.controller.type(num)
            # Check if the number has a valid WA account
            if self.controller.wait(self.base_path + "Valid WA Num", 10):
                # Find the name box 
                self.controller.find_click(self.base_path + "Name", 0.9)
                # Type the name for the contact
                self.controller.copy_paste(contact_name)
                # Save the contact 
                self.controller.find_click(self.base_path + "Save Contact")
                return True, "Number added"
            else:
                return False, "Number not on WhatsApp"
        except Exception as e:
            return False, "Failed to add number - unexpected error. Check icon images."
        
    @log_function
    def delete_contact(self):
        """
        Delete the currently open WhatsApp contact.
        """
        
        # Click the contact info bar
        self.controller.find_click(self.base_path + "Contact Bar", 0.5)
        # Click on the contact edit icon
        self.controller.find_click(self.base_path + "Edit Contact", 0.7)
        # Click on the delete contact icon
        self.controller.find_click(self.base_path + "Delete Contact", 0.7)
        # Click confirm delete
        self.controller.find_click(self.base_path + "Delete Contact Confirm")
    
    @log_function
    def close_chat(self):
        """
        Close the currently open chat.
        """
        self.controller.click_esc()

    @log_function
    def reset_wa(self):
        """
        Return WhatsApp UI to the main chats screen.
        """
        # Find and click the chats icon
        self.controller.find_click(self.base_path + "WA Chats", 0.7, False)

    @log_function
    def check_doc(self, doc_path: str) -> bool:
        """
        Check if a document exists at the given path.
        """
        return os.path.exists(doc_path)

    @log_function
    def send(self, number: str, contact_name:str, message: str, document: str) -> tuple[bool, str]:
        """
        Send a resolved message and document to a given number.
        This provides a unified interface for the Core Engine, 
        independent of internal resolution logics.
        """
        try:
            # Attempt to add/search for contact
            # We pass an empty name as contact naming may not be needed for direct send from core
            success, msg = self.add_contact(number, contact_name)
            if not success:
                return False, "whatsapp_not_detected"

            # Find the msg box in the chat
            if not self.controller.wait(self.base_path + "Msg Bar", 3):
                return False, "whatsapp_not_detected"

            # Type out the text message if any
            if message:
                self.controller.find_click(self.base_path + "Msg Bar", 0.7)
                self.controller.copy_paste(message)

            # Attach a document if requested
            if document:
                if not self.check_doc(document):
                    return False, "doc_not_found"
                
                self.controller.find_click(self.base_path + "Add Doc", 0.9)
                self.controller.find_click(self.base_path + "Doc")
                document = document.replace("/", "\\")
                self.controller.type(document)
                
                # Send the document
                self.controller.click_enter()
                
                # Wait till the msg is successfully sent
                if not self.controller.wait(self.base_path + "File Sent", 15):
                    return False, "send_failure"
            else:
                if message:
                    # Send just the text
                    self.controller.click_enter()
                    
            self.delete_contact()
            self.reset_wa()

            return True, ""
        except Exception as e:
            return False, "send_failure"