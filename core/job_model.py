from dataclasses import dataclass
from enum import Enum
from typing import Optional

class JobStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAIL = "fail"

@dataclass
class ContactJob:
    number: str
    contact_name: Optional[str] = None
    message: Optional[str] = None
    doc_path: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    status_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "contact_name": self.contact_name or "",
            "message": self.message or "",
            "doc_path": self.doc_path or "",
            "status": self.status.value if isinstance(self.status, JobStatus) else self.status,
            "status_message": self.status_message or ""
        }
