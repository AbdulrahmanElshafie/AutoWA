import os
import shutil
import pyautogui
from PIL import Image
from datetime import datetime

class UIElementNotFound(Exception):
    def __init__(self, element_name):
        self.element_name = element_name
        super().__init__(f"UI Element not found: {element_name}")

REVIEW_QUEUE_DIR = "assets/review_queue"
HISTORY_DIR = "assets/history"
ICONS_DIR = os.path.join("assets", "icons")

# Ensure directories exist
os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

# ----------------------------------------------------
# UI Recovery Methods
# ----------------------------------------------------

def save_failure_snapshot(element_name: str) -> str:
    """Captures and saves a snapshot for review when an element fails."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{element_name}_{timestamp}.png"
    filepath = os.path.join(REVIEW_QUEUE_DIR, filename)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    # Log failure event
    print(f"Captured failure snapshot for {element_name} at {filepath}")
    return filepath

def list_pending_recoveries() -> list:
    """Lists all failed elements waiting for user review."""
    recoveries = []
    if not os.path.exists(REVIEW_QUEUE_DIR):
        return recoveries
        
    for file in os.listdir(REVIEW_QUEUE_DIR):
        if file.endswith(".png"):
            filepath = os.path.join(REVIEW_QUEUE_DIR, file)
            parts = file.split("_")
            if len(parts) >= 2:
                element_name = "_".join(parts[:-2]) if len(parts) > 2 else parts[0]
            else:
                element_name = file.replace(".png", "")
                 
            recoveries.append({
                "element_name": element_name,
                "snapshot_path": filepath,
                "timestamp": os.path.getmtime(filepath)
            })
    return sorted(recoveries, key=lambda x: x["timestamp"], reverse=True)

def delete_recovery(filepath: str) -> bool:
    """Delete a specific recovery screenshot from the queue."""
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def save_recovery_to_icon(snapshot_path: str, crop_box: tuple, target_icon: str) -> bool:
    """
    Crops the snapshot and saves it into the target icon directory.
    After successful save, deletes the snapshot from the review queue.
    crop_box should be (left, top, right, bottom).
    """
    target_dir = os.path.join(ICONS_DIR, target_icon)
    os.makedirs(target_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filepath = os.path.join(target_dir, f"{target_icon}_{timestamp}.png")

    try:
        # Perform Crop
        with Image.open(snapshot_path) as img:
            cropped_img = img.crop(crop_box)
            cropped_img.save(new_filepath)
        
        # Delete original snapshot as it was successfully processed
        delete_recovery(snapshot_path)
        print(f"Successfully cropped and saved {target_icon} to {new_filepath}")
        return True
        
    except Exception as e:
        print(f"Error while saving crop: {e}")
        return False

# ----------------------------------------------------
# Icons Management Methods
# ----------------------------------------------------

def list_icons() -> list:
    """Lists all icon directories located in the ICONS_DIR."""
    if not os.path.exists(ICONS_DIR):
        return []
    
    dirs = [d for d in os.listdir(ICONS_DIR) if os.path.isdir(os.path.join(ICONS_DIR, d))]
    return sorted(dirs)

def list_icon_images(icon_name: str) -> list:
    """Returns a list of image paths for a specific icon."""
    target_dir = os.path.join(ICONS_DIR, icon_name)
    if not os.path.exists(target_dir):
        return []
        
    images = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith(".png") or f.endswith(".PNG")]
    return sorted(images)

def delete_icon_image(filepath: str) -> bool:
    """Deletes an image from an icon folder."""
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
