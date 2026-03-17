import os
import json
from datetime import datetime
import pyautogui
from PIL import Image
from logger import log_function

class IconManager:
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    learn_assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "learned_assets")
    meta_path = os.path.join(learn_assets_dir, "metadata.json")

    @log_function
    def load_metadata(self,):
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    @log_function
    def save_metadata(self, data):
        os.makedirs(os.path.dirname(self.meta_path), exist_ok=True)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @log_function
    def add_icon_metadata(self, icon_name, contains_text, ar_generated):
        data = self.load_metadata()

        data.append({
            "icon": icon_name,
            "contains_text": contains_text,
            "ar_generated": ar_generated,
            "acknowledged": False
        })

        self.save_metadata(data)

    @log_function
    def capture_failure(self, icon_name):
        os.makedirs(self.learn_assets_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.join(self.learn_assets_dir, f"{icon_name}_{ts}.png")
        path = os.path.join(file_name)
        pyautogui.screenshot(path)
        self.add_icon_metadata(
                icon_name=file_name,
                contains_text=True,
                ar_generated=False
            )
        return path

    @log_function
    def learn_icon(self, original_icon_path, screenshot_path):
        """
        Save failed screenshots as candidates + register metadata.

        - Marks all icons as containing text by default
        if you don't want to perform OCR.
        - Auto-generates AR icons only for symbol icons.
        """

        icon_name = os.path.basename(original_icon_path)

        # Timestamped learned icon filename
        learned_filename = f"{icon_name}_AUTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        learned_path = os.path.join(self.assets_dir, learned_filename)

        try:
            # Save the screenshot as the learned icon
            img = Image.open(screenshot_path) # learn icon folder
            img.save(learned_path) # save to icon folder in assets

            # # ✅ Without OCR: assume contains_text = True for all new icons
            # contains_text = True

            # # 🔹 Only generate AR icon if symbol-only (here always False, so AR won't generate)
            # ar_generated = False
            # # Example: if you have a way to mark symbol icons, you can set contains_text=False and generate AR

            # # 🧾 Save metadata entry
            # self.add_icon_metadata(
            #     icon_name=learned_filename,
            #     contains_text=contains_text,
            #     ar_generated=ar_generated
            # )

        except Exception as e:
            # fail silently; can also log
            pass
