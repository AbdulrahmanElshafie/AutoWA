from typing import Tuple, List, Dict, Optional
from .job_model import ContactJob, JobStatus

def validate_job(job: ContactJob) -> Tuple[bool, Optional[str]]:
    """
    Validates a single job based on schema rules.
    Returns (is_valid, error_code).
    """
    if not job.message and not job.doc_path:
        return False, "missing_content"
        
    return True, None

def validate_jobs(jobs: List[ContactJob]) -> Dict[str, int]:
    """
    Validates a list of jobs, updating their status inline if validation fails.
    Returns a summary of the validation.
    """
    stats = {
        "total": len(jobs),
        "valid": 0,
        "invalid": 0
    }
    
    for job in jobs:
        is_valid, error = validate_job(job)
        if not is_valid:
            job.status = JobStatus.FAIL
            job.status_message = error
            stats["invalid"] += 1
        else:
            stats["valid"] += 1
            
    return stats
