import csv
from typing import List
from .job_model import ContactJob, MessageMode, DocMode, JobStatus

def load_jobs(csv_path: str) -> List[ContactJob]:
    """
    Load jobs from a CSV file.
    """
    jobs: List[ContactJob] = []
    
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse required fields
            number = row.get("number", "").strip()
            if not number:
                continue # Skip completely empty rows
                
            raw_msg_mode = row.get("message_mode", "").strip()
            try:
                message_mode = MessageMode(raw_msg_mode)
            except ValueError:
                message_mode = raw_msg_mode # Keep as string for validator to catch later or handle gracefully
                
            raw_doc_mode = row.get("doc_mode", "").strip()
            try:
                doc_mode = DocMode(raw_doc_mode)
            except ValueError:
                doc_mode = raw_doc_mode
                
            # Parse optional fields
            contact_name = row.get("contact_name", "").strip() or None
            message_text = row.get("message_text", "").strip() or None
            message_key = row.get("message_key", "").strip() or None
            doc_path = row.get("doc_path", "").strip() or None
            
            # Status defaults to pending if missing
            raw_status = row.get("status", "").strip()
            if raw_status:
                try:
                    status = JobStatus(raw_status)
                except ValueError:
                    status = JobStatus.FAIL # Invalid statuses are treated as failed or handled elsewhere
            else:
                status = JobStatus.PENDING
                
            status_message = row.get("status_message", "").strip() or None
            
            job = ContactJob(
                number=number,
                message_mode=message_mode,
                doc_mode=doc_mode,
                contact_name=contact_name,
                message_text=message_text,
                message_key=message_key,
                doc_path=doc_path,
                status=status,
                status_message=status_message
            )
            jobs.append(job)
            
    return jobs

def save_jobs(csv_path: str, jobs: List[ContactJob]) -> None:
    """
    Save jobs back to a CSV file.
    """
    if not jobs:
        return
        
    fieldnames = [
        "number", "contact_name", "message_mode", "message_text", 
        "message_key", "doc_mode", "doc_path", "status", "status_message"
    ]
    
    with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job.to_dict())
