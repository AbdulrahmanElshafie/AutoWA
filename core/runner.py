import json
import os
from typing import Dict, Any

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
    timing_profiles = config.get("timing_profiles", {})
    profile = list(timing_profiles.keys())[0] if timing_profiles else None
    
    controller = WAController(profile)
    
    stats = {
        "total": len(jobs),
        "success": 0,
        "fail": 0
    }
    
    for job in jobs:
        if job.status == JobStatus.FAIL:
            stats["fail"] += 1
            continue
            
        try:
            msg = resolve_message(job, templates)
            doc = resolve_document(job, config)
            
            # Send using WAController integration
            success, err_msg = controller.send(job.number, msg, doc)
            
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
            
    # Save the updated statuses to original CSV
    save_jobs(csv_path, jobs)
    
    return stats
