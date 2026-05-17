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
    """
    Captures and saves a full-screen snapshot for review when a UI element fails to match.
    
    Logic Flow:
    1. Generates a unique filename using the element's name and the current timestamp.
    2. Uses pyautogui to capture the current screen state.
    3. Saves the screenshot into the REVIEW_QUEUE_DIR.
    4. Logs the event and returns the filepath for reference.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{element_name}_{timestamp}.png"
    filepath = os.path.join(REVIEW_QUEUE_DIR, filename)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    # Log failure event
    print(f"Captured failure snapshot for {element_name} at {filepath}")
    return filepath

def list_pending_recoveries() -> list:
    """
    Lists all failed elements waiting for user review in the queue.
    
    Logic Flow:
    1. Checks if the REVIEW_QUEUE_DIR exists.
    2. Iterates through all PNG files in the directory.
    3. Parses the filename to extract the base element name (stripping the timestamp).
    4. Gathers file metadata (modification time) to sort the queue.
    5. Returns a list of dictionaries containing recovery details, sorted by newest first.
    """
    recoveries = []
    if not os.path.exists(REVIEW_QUEUE_DIR):
        return recoveries
        
    for file in os.listdir(REVIEW_QUEUE_DIR):
        if file.endswith(".png"):
            filepath = os.path.join(REVIEW_QUEUE_DIR, file)
            parts = file.split("_")
            # Reconstruct the element name by omitting the timestamp parts
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
    """
    Deletes a specific recovery screenshot from the review queue.
    
    Logic Flow:
    1. Verifies the file exists at the given filepath.
    2. Removes the file from the filesystem.
    3. Returns True if successful, False otherwise.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def save_cropped_image_to_icon(cropped_img, snapshot_path: str, target_icon: str) -> bool:
    """
    Saves a pre-cropped PIL Image into the target icon directory and removes
    the original snapshot from the review queue.
    
    Logic Flow:
    1. Ensures the target directory for the specific icon name exists.
    2. Generates a new timestamped filename.
    3. Saves the in-memory cropped PIL Image to the filesystem.
    4. Removes the original failure snapshot since it has been successfully processed.
    """
    target_dir = os.path.join(ICONS_DIR, target_icon)
    os.makedirs(target_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filepath = os.path.join(target_dir, f"{target_icon}_{timestamp}.png")

    try:
        cropped_img.save(new_filepath)
        delete_recovery(snapshot_path)
        print(f"Saved cropped image for {target_icon} to {new_filepath}")
        return True
    except Exception as e:
        print(f"Error while saving cropped image: {e}")
        return False

# ----------------------------------------------------
# Icons Management Methods
# ----------------------------------------------------

def list_icons() -> list:
    """
    Lists all icon directories located in the ICONS_DIR.
    
    Logic Flow:
    1. Checks if the main icons directory exists.
    2. Iterates over its contents and filters for subdirectories.
    3. Returns a sorted list of folder names representing the known icons.
    """
    if not os.path.exists(ICONS_DIR):
        return []
    
    dirs = [d for d in os.listdir(ICONS_DIR) if os.path.isdir(os.path.join(ICONS_DIR, d))]
    return sorted(dirs)

def list_icon_images(icon_name: str) -> list:
    """
    Returns a list of image paths for a specific icon.
    
    Logic Flow:
    1. Builds the path to the specific icon's directory.
    2. Validates that the directory exists.
    3. Scans for files ending with .png or .PNG and collects their full paths.
    4. Returns the sorted list of image file paths.
    """
    target_dir = os.path.join(ICONS_DIR, icon_name)
    if not os.path.exists(target_dir):
        return []
        
    images = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith(".png") or f.endswith(".PNG")]
    return sorted(images)

def delete_icon_image(filepath: str) -> bool:
    """
    Deletes an image from an icon folder.
    
    Logic Flow:
    1. Checks if the specific image file exists.
    2. Removes the file from the filesystem to clean up.
    3. Returns True on success, False otherwise.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
