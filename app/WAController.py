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
    
    # Base path for all UI image assets
    base_path = "C:\\Users\\PC\\Desktop\\Scripts_Updates\\New Script\\assets\\"
    
    """
    =====================
    ==accounts/browsers==
    =====================
    1: chrome
    2: ms edge
    """

    # Mapping WhatsApp account index to browser executable
    accounts = {
            1: "", # default browser (chrome)
            2: "msedge.exe" # to open edge
        }
    
    # Browser-specific UI icons (zoom, reset zoom, maximize)
    browser_icons = {
        1: ["Zoom", "Reset Zoom", "Maximise Tab"],
        2: ["Zoom MS", "Reset Zoom MS", "Maximise Tab MS"]
    }
    controller = None

    def __init__(self, profile):
        """
        Initialize the WhatsApp controller.

        Internally creates a GuiController instance that handles
        all desktop interaction.

        Args:
            profile (int):
                Index of the timing profile to use.
        """
        self.controller = GuiController(profile)
    
    @log_function
    def get_msg(self, name, sending_type='permit'):
        """
        Select a random predefined message template.

        Message pools vary depending on the sending type
        (permit or seglat).

        Args:
            name (str):
                Recipient name used in some message templates.
            sending_type (str, optional):
                Type of message to send.
                Supported values:
                - 'permit'
                - 'seglat'
                Defaults to 'permit'.

        Returns:
            str:
                Randomly selected message text.
        """
        msgs = []
        if sending_type == 'permit':
            # Permit-related message templates
            msgs = [
                "مرفق لكم التصريح الإلكتروني للسفر. التصريح متاح حالياً على منظومة الجوزات في جميع منافذ الجمهورية. حمل النسخة الإلكترونية على هاتفك أو مطبوعة أثناء المغادرة يغنيك عن استلام النسخة الورقية. يجب تقديم التصريح لموظف الجوازات عند الطلب فقط. لأي استفسارات أو تواصل، يرجى الاتصال على 01023207441 أو 0222610314 أو 0224042264، أو المراسلة عبر البريد الإلكتروني oad@mod.gov.eg. نحن متواجدون لخدمتكم 24/7 طوال الأسبوع. هذا التصريح لا يعفي من مسؤولية الالتزام بأي استدعاء. إدارة شئون ضباط القوات المسلحة تتمنى لك زيارة الرابط التالي: https://officersaffairs.mod.gov.eg\nتنبيه هام: يتم استخراج نموذج 53 وملؤه عن طريق الموقع الإلكتروني دون الحاجة للتوجه لإدارة شئون ضباط القوات المسلحة.",

                "مرفق تصريح السفر الإلكتروني الخاص بكم - التصريح موجود حاليا على منظومة الجوزات بجميع منافذ الجمهورية - وجود النسخة الإلكترونية من تصريح السفر معك (على المحمول أو مطبوعة ) أثناء المغادرة يغنيك عن استلامك للنسخة الورقية - يقدم التصريح الإلكتروني لموظف الجوازات في حالة الطلب فقط - للتواصل معنا أو للاستفسارات 01023207441 أو 0222610314 أو 0224042264 أو للمراسلة على البريد الالكتروني (oad@mod.gov.eg) نحن معك على مدار الاسبوع / 24 ساعة - هذا التصريح لا يعفيك من مسئولية التخلف عن الإستدعاء - إدارة شئون ضباط القوات المسلحة تتمنى لك زيارة الرابط التالى: https://officersaffairs.mod.gov.eg.....تنبيه هااااام...يتم استخراج نموذج 53 تعبئة عن طريق الموقع الالكترونى دون الحاجة الى التوجه الى مقر ادارة شئون ضباط ق.م",

                f"السيد/ {name} اليكم تصريح السفر الخاص بكم",

                f"السيد/ {name} اليكم تصريح السفر",

                "اليكم تصريح السفر الخاص بكم",

                "مرفق اليكم تصريح السفر",

                "تم الانتهاء من عمل التصريح الخاص بكم",

                "تصريح السفر الخاص بكم",

                f"السيد/ {name} تم الانتهاء من عمل تصريحكم للسفر ",

                "تم الانتهاء من عمل تصريح حضراتكم",

                "تم ارسال تصريح السفر الخاص بحضراتكم",

                f"السيد/ {name} تم ارسال تصريح السفر الخاص بكم",

                "مرفق اليكم تصريح السفر الخاص بحضراتكم",

                "   ",

                "مرفق الي حضراتكم تصريح السفر",

                f"السيد/ {name} مقدم اليكم تصريح السفر",

                "اليكم تصريح السفر الخاص بكم",

                "مرفق تصريح السفر الخاص بكم",

                "مرفق لحضرتك تصريح السفر الخاص بكم",

                "مرفق تصريح السفر",
                
                "تصريح السفر مرفق لكم",

                "اليكم تصريح السفر الخاص بكم ",

                "تصريح السفر الخاص بحضرتك يا فندم ",
            ]  
        elif sending_type == 'seglat':
            # Seglat message templates
            msgs = [
                "تم الانتهاء من عمل النموذج الخاص بكم برجاء التوجه للسجلات العسكرية لاستخراج الخدمة",

                "تم الانتهاء من عمل نموذح 53 برجاء التوجه للسجلات العسكرية لاستخراج الخدمة",

                "مرفق اليكم نموذج 53 تعبئة يمكنكم التوجه الي السجلات العسمكرية لعمل الشهادة",

                "نموذج 53 تعبئة",

                "مقدم اليكم نموذج 53 تعبئة الخاص بكم",

                "برجاء طباعة النموذج ثم التوجه لأقرب مكتب سجلات عسكرية لاستخراج شهادة انهاء الخدمة",
            ]

        return random.choice(msgs)
    
    @log_function
    def reset_zoom(self, account):
        """
        Reset browser zoom level for a given account.

        Uses browser-specific zoom and reset icons.

        Args:
            account (int):
                WhatsApp account / browser identifier.
        """
        icons = self.browser_icons[account]
        self.controller.find_click(self.base_path + icons[0], 0.9, False)
        self.controller.find_click(self.base_path + icons[1], 0.9, False)

    @log_function
    def maximise_tab(self, account):
        """
        Maximize the browser tab for better UI consistency.
        
        Uses browser-specific zoom and reset icons.

        Args:
            account (int):
                WhatsApp account / browser identifier.
        """
        self.controller.find_click(self.base_path + self.browser_icons[account][2], 0.9, False)

    @log_function
    def open_wa(self, wa_account):
        """
        Open WhatsApp Web in the specified browser.

        The method:
        - Launches the browser
        - Maximizes the tab
        - Resets zoom
        - Waits for WhatsApp UI to load

        Args:
            wa_account (int):
                WhatsApp account / browser identifier.
        """
        
        # Get the browser used for the call
        account = self.accounts[wa_account]

        # Open WhatsApp Web via PowerShell
        powershell_command = f'powershell -Command "Start-Process {account} \'https://web.whatsapp.com/\'"'       
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
    def extract_officer_id(self, name):
        # Get the officer ID in case of a permit/serglat or request ID in case of a msg 
        request_id_match = re.search(r"\(\s*(\d+)\s*\)", name)
        officer_name = request_id_match.group(1) if request_id_match else name

        return officer_name

    @log_function
    def add_contact(self, num, name):
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
                    return True, "تم فتح الشات"
                return False, "رقم بدون واتساب"

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
                # Get the officer ID in case of a permit/serglat or request ID in case of a msg 
                officer_name = self.extract_officer_id(name)
                # Type the name for the contact
                self.controller.type(officer_name)
                # Save the contact 
                self.controller.find_click(self.base_path + "Save Contact")
                return True, "تمت إضافة الرقم"
            else:
                return False, "رقم بدون واتساب"
        except Exception as e:
            return False, "فشل إضافة الرقم بسبب خطأ غير متوقع - تفحص صور الايكونات"
        
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
    def check_file(self, officer_id, type='permit'):
        """
        Check if a document exists for sending.

        The directory is selected based on document type.

        Args:
            officer_id (str):
                Document identifier (filename without extension - officer id).
            type (str, optional):
                Document type ('permit' or 'seglat').

        Returns:
            str or None:
                Full path to the document if it exists, otherwise None.
        """
        # Load the configurations to get the paths for the docs folders
        from gui.helpers import load_config
        config = load_config()

        # Load the docs folder based on the document type
        if type=='permit':
            docs_dir = config.get("permits_dir").replace('/', '\\')
        elif type=='seglat':
            docs_dir = config.get("seglat_dir").replace('/', '\\')

        # Create the document path
        permit_path = os.path.join(docs_dir, officer_id + ".pdf")

        # Check if the document exists and return it
        if os.path.exists(permit_path):
            return permit_path
        
        return None
    
    @log_function
    def send_content(self, content, name, doc_type=None):
        """
        Send a message or message with an attached document.

        If doc_type is provided:
        - A predefined message is generated
        - A document is attached and sent

        Otherwise:
        - A plain text message is sent

        Args:
            content (str):
                Message text or document identifier.
            name (str):
                Recipient name.
            doc_type (str, optional):
                Document type ('permit' or 'seglat' or None).

        Returns:
            tuple (bool, str):
                Success status and descriptive message.
        """
        try:
            # Find the msg box in the chat
            self.controller.find_click(self.base_path + "Msg Bar", 0.7)

            # auto decide which type is the document
            # if no name => seglat
            # if a name with a 14 chars number => officer id => permit else msg
            officer_id = self.extract_officer_id(content)
            if not doc_type:
                if name == "nan" and len(officer_id) == 14:
                    doc_type = "seglat"
                else:
                    if len(officer_id) == 14:
                        doc_type = "permit"
                    else:
                        doc_type = "msg"


            # Prepare message text and type it
            msg = self.get_msg(name, doc_type) if doc_type != "msg" else name + " " + content
            self.controller.copy_paste(msg)

            # If a document is attached
            if doc_type != "msg":
                # Check the existence of the document
                permit_path = self.check_file(content, doc_type)

                # If found a valid document path then attach it to the msg
                if permit_path:

                    # Find the add attachemes icon
                    self.controller.find_click(self.base_path + "Add Doc", 0.9)
                    # Add add a document
                    self.controller.find_click(self.base_path + "Doc")
                    # Type the document path in the filename box
                    self.controller.type(permit_path)
                    # Click enter to choose the file and another enter to send the msg
                    self.controller.click_enter()
                    # Wait till the msg is successfully sent to the officer
                    self.controller.wait(self.base_path + "File Sent", 15)
                else:
                    return False, "المستند غير موجود في المجلد المقدم"

            else:
                # Click enter to send the text msg directly
                self.controller.click_enter()

            return True, "تم إرسال المحتوى بنجاح"
        except Exception as e:
            return False, "فشل إرسال المحتوى بسبب خطأ غير متوقع"

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
    def send(self, number: str, message: str, document: str) -> tuple[bool, str]:
        """
        Send a resolved message and document to a given number.
        This provides a unified interface for the Core Engine, 
        independent of internal resolution logics.
        """
        try:
            # Attempt to add/search for contact
            # We pass an empty name as contact naming may not be needed for direct send from core
            success, _ = self.add_contact(number, "")
            if not success:
                return False, "whatsapp_not_detected"

            # Find the msg box in the chat
            if not self.controller.wait(self.base_path + "Msg Bar", 3):
                return False, "whatsapp_not_detected"
            
            self.controller.find_click(self.base_path + "Msg Bar", 0.7)

            # Type out the text message if any
            if message:
                self.controller.copy_paste(message)

            # Attach a document if requested
            if document:
                self.controller.find_click(self.base_path + "Add Doc", 0.9)
                self.controller.find_click(self.base_path + "Doc")
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

            return True, ""
        except Exception as e:
            return False, "send_failure"