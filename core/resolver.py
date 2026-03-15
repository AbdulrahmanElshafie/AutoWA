import random
import os
from typing import Optional, Dict, Any
from .job_model import ContactJob, MessageMode, DocMode

def resolve_message(job: ContactJob, templates: Dict[str, Any]) -> Optional[str]:
    """
    Resolves the final message text for a job.
    """
    if job.message_mode == MessageMode.DOC_ONLY:
        return None
        
    if job.message_mode == MessageMode.FIXED:
        msg = job.message_text or ""
    elif job.message_mode == MessageMode.TEMPLATE:
        key = job.message_key
        if not key or key not in templates:
            raise ValueError("template_not_found")
            
        template = templates[key]
        if not template.get("enabled", True):
            raise ValueError("template_disabled")
            
        variants = template.get("variants", [])
        if not variants:
            raise ValueError("template_not_found")
            
        msg = random.choice(variants)
    else:
        return None
        
    # Replace placeholders
    if "{contact_name}" in msg:
        msg = msg.replace("{contact_name}", job.contact_name or "")
        
    return msg

def resolve_document(job: ContactJob, config: Dict[str, Any]) -> Optional[str]:
    """
    Resolves the final document path for a job.
    """
    if job.doc_mode == DocMode.NONE:
        return None
        
    if job.doc_mode == DocMode.FIXED:
        fixed_path = config.get("fixed_doc_path")
        if not fixed_path:
            raise ValueError("document_not_found")
        doc_path = fixed_path
    elif job.doc_mode == DocMode.VARIABLE:
        if not job.doc_path:
            raise ValueError("document_not_found") # conceptually schema missing_doc_path catches this, but just in case
        doc_path = job.doc_path
    else:
        return None
        
    # Optional check if the path is valid could happen here or in the runner.
    # The taxonomy states "document path invalid" maps to "document_not_found".
    if not os.path.exists(doc_path):
        raise ValueError("document_not_found")
        
    return doc_path
