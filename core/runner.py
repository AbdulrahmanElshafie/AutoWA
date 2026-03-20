from gui.helpers import load_config, load_messages
import json
import os
from typing import Dict, Any
import time
import random

from .job_loader import load_jobs, save_jobs
from .validator import validate_jobs
from .job_model import JobStatus
from logger import log_function
from app.WAController import WAController
import FreeSimpleGUI as sg

def sleep_with_events(duration: float, window=None) -> bool:
    """Sleep for duration while keeping GUI responsive. Returns True if interrupted."""
    import gui.events as events
    if not window:
        time.sleep(duration)
        return not events.running
        
    end_time = time.time() + duration
    while time.time() < end_time:
        if not events.running:
            return True
        event, values = window.read(timeout=0)
        if event in (sg.WIN_CLOSED, "-CANCEL-", "-PAUSE-"):
            events.running = False
            return True
    return False

@log_function
def execute_jobs(csv_path: str, window=None) -> Dict[str, int]:
    """
    Main entry point for the Core Engine. Orchestrates the workflow.
    
    This function:
    1. Loads and validates jobs from a CSV file.
    2. Initializes timing configurations and WAController instances for multiple browsers.
    3. Iterates through the jobs list, sending messages/docs via the active WhatsApp account.
    4. Handles batching logic: switches between WhatsApp accounts after a certain number of messages.
    5. Injects realistic wait times between messages and between account switches to avoid detection.
    6. Syncs execution progress back to the GUI without freezing the main thread.
    """
    jobs = load_jobs(csv_path)
    if not jobs:
        return {"total": 0, "success": 0, "fail": 0}
        
    validate_jobs(jobs)
    
    config = load_config()
    templates = load_messages()
    
    # Initialize controller
    # We attempt to fetch the first timing profile if any exists
    timing_profiles = config.get("time_profiles", {}) # Fixed key to match config schema (time_profiles instead of timing_profiles)
    profile = list(timing_profiles.keys())[0] if timing_profiles else None
    
    browsers = config.get("browsers", ["Default Browser"])
    if not browsers:
        browsers = ["Default Browser"]

    batch_size = int(config.get("batch_size", 5))
    msg_wait_min = float(config.get("msg_wait_min", 5))
    msg_wait_max = float(config.get("msg_wait_max", 10))
    batch_wait_min = float(config.get("batch_wait_min", 10)) * 60
    batch_wait_max = float(config.get("batch_wait_max", 20)) * 60

    controllers = [WAController(profile, browser=b) for b in browsers]
    
    stats = {
        "total": len(jobs),
        "success": 0,
        "fail": 0
    }

    current_controller_idx = 0
    controller = controllers[current_controller_idx]  # Select the first account
    controller.open_wa()                              # Launch UI/Browser for the account
    msgs_in_current_batch = 0
    
    # Initialize the GUI progress bar if a window is provided
    if window:
        window["-PROGRESS-"].update(current_count=0, max=stats["total"])
        window.read(timeout=0)
        
    for i, job in enumerate(jobs):
        import gui.events as events
        
        # Stop execution immediately if the user paused or cancelled from the GUI
        if not events.running:
            break 
            
        # Broadcast the current completion percentage back to the GUI
        if window:
            processed = stats["success"] + stats["fail"]
            window["-PROGRESS-"].update(current_count=processed)
            window["-PROGRESS_TEXT-"].update(f"{processed} / {stats['total']}")
            event, values = window.read(timeout=0)
            # Listen to user-cancellation during the loop
            if event in (sg.WIN_CLOSED, "-CANCEL-", "-PAUSE-"):
                events.running = False
                break
                
        # Skip jobs that previously failed during an earlier run
        if job.status == JobStatus.FAIL:
            stats["fail"] += 1
            continue
            
        try:
            # Send using WAController integration
            success, err_msg = controller.send(job.number, job.contact_name, job.message, job.doc_path)
            
            if success:
                job.status = JobStatus.SUCCESS
                stats["success"] += 1
            else:
                job.status = JobStatus.FAIL
                job.status_message = err_msg
                stats["fail"] += 1
                
        except ValueError as e:
            job.status = JobStatus.FAIL
            job.status_message = str(e)
            stats["fail"] += 1
        except Exception as e:
            job.status = JobStatus.FAIL
            job.status_message = f"unexpected_error: {str(e)}"
            stats["fail"] += 1

        # Determine wait intervals and account swapping logic
        # We trigger delays between tasks unless this is the very last job.
        if i < len(jobs) - 1 and job.status != JobStatus.FAIL:
            msgs_in_current_batch += 1
            if msgs_in_current_batch >= batch_size:
                # We reached our safe threshold for messages sent using this specific account.
                # Time to switch to the next configured WhatsApp account/browser profile!
                next_idx = (current_controller_idx + 1) % len(controllers) 
                is_new_round = next_idx == 0   
                
                # Close the currently active WhatsApp tab
                controller.close_wa()
                
                # Re-assign the controller to the next account and open its tab
                controller = controllers[next_idx]
                controller.open_wa()
                
                # Reset tracking so the next account gets its full batch
                msgs_in_current_batch = 0
                
                # If we've cycled completely back to the first account, it's the end of a full round.
                # Take a longer "batch wait" pause to seem completely offline.
                if is_new_round:
                    # Pause heavily using our GUI-safe sleep function. Break if user interrupts.
                    if sleep_with_events(random.uniform(batch_wait_min, batch_wait_max), window):
                        break
                else:
                    # Switched to a new account, so no delay is needed. We fire the first message instantly!
                    pass 
            else:
                # Still safely within the current account's batch size. Just wait a few seconds
                # between messages to simulate human typing delays.
                if sleep_with_events(random.uniform(msg_wait_min, msg_wait_max), window):
                    break
            
    if window:
        processed = stats["success"] + stats["fail"]
        window["-PROGRESS-"].update(current_count=processed)
        window["-PROGRESS_TEXT-"].update(f"{processed} / {stats['total']}")
        window.read(timeout=0)

    # Save the updated statuses to original CSV
    save_jobs(csv_path, jobs)
    
    return stats
