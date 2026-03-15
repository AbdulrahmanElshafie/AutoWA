from typing import Tuple, List, Dict, Optional
from .job_model import ContactJob, MessageMode, DocMode, JobStatus

def validate_job(job: ContactJob) -> Tuple[bool, Optional[str]]:
    """
    Validates a single job based on schema rules.
    Returns (is_valid, error_code).
    """
    # 1. Unknown message mode
    if not isinstance(job.message_mode, MessageMode):
        return False, "invalid_message_mode"
        
    # rule: message_mode = fixed AND message_text empty
    if job.message_mode == MessageMode.FIXED and not job.message_text:
        return False, "missing_message_text"
        
    # rule: message_mode = template AND message_key empty
    if job.message_mode == MessageMode.TEMPLATE and not job.message_key:
        return False, "missing_message_key"
        
    # rule: doc_mode = variable AND doc_path empty
    if job.doc_mode == DocMode.VARIABLE and not job.doc_path:
        return False, "missing_doc_path"
        
    # rule: message_mode = doc_only AND doc_mode = none
    if job.message_mode == MessageMode.DOC_ONLY and job.doc_mode == DocMode.NONE:
        # The schema categorizes this case as invalid.
        # Although not explicitly mapped in error_taxonomy, lacking a doc when doc_only is selected
        # implies a missing document path or invalid conceptual state. We use missing_doc_path as appropriate fallback.
        return False, "missing_doc_path"
        
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
