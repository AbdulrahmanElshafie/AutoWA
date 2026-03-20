import csv
from typing import List
from .job_model import ContactJob, JobStatus

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
                
            # Parse optional fields
            contact_name = row.get("contact_name", "").strip() or None
            message = row.get("message", "").strip() or None
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
                contact_name=contact_name,
                message=message,
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
        "number", "contact_name", "message", "doc_path", "status", "status_message"
    ]
    
    with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job.to_dict())
