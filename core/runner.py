import json
import os
from typing import Dict, Any
import time
import random

from .job_loader import load_jobs, save_jobs
from .validator import validate_jobs
from .resolver import resolve_message, resolve_document
from .job_model import JobStatus

from app.WAController import WAController

def load_json(filepath: str) -> Dict[str, Any]:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def execute_jobs(csv_path: str) -> Dict[str, int]:
    """
    Main entry point for the Core Engine. Orchestrates the workflow.
    """
    jobs = load_jobs(csv_path)
    if not jobs:
        return {"total": 0, "success": 0, "fail": 0}
        
    validate_jobs(jobs)
    
    config = load_json("config.json")
    templates = load_json("messages.json")
    
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
    controller = controllers[current_controller_idx]
    controller.open_wa()
    msgs_in_current_batch = 0
    
    for i, job in enumerate(jobs):

        if job.status == JobStatus.FAIL:
            stats["fail"] += 1
            continue
            
        try:
            msg = resolve_message(job, templates)
            doc = resolve_document(job, config)
            
            # Send using WAController integration
            success, err_msg = controller.send(job.number, job.name, msg, doc)
            
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

        # Determine wait and sequence logic unless this is the final job completely.
        if i < len(jobs) - 1 and job.status != JobStatus.FAIL:
            msgs_in_current_batch += 1
            if msgs_in_current_batch >= batch_size:
                # Reached batch size, switch to next account
                current_controller_idx += 1
                # Close the current tab
                controller.close_wa()
                # Open the next tab
                controller = controllers[current_controller_idx]
                controller.open_wa()
                # Reset the batch counter
                msgs_in_current_batch = 0
                
                # If we've cycled through all accounts, it's the end of a round.
                if current_controller_idx >= len(controllers):
                    current_controller_idx = 0
                    time.sleep(random.uniform(batch_wait_min, batch_wait_max))
                else:
                    # Switched account, no msg delay since it's a new batch for the next account
                    pass 
            else:
                # Still within the current batch, wait before sending next msg
                time.sleep(random.uniform(msg_wait_min, msg_wait_max))
            
    # Save the updated statuses to original CSV
    save_jobs(csv_path, jobs)
    
    return stats
