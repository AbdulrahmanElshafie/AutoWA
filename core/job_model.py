from dataclasses import dataclass
from enum import Enum
from typing import Optional

class MessageMode(str, Enum):
    FIXED = "fixed"
    TEMPLATE = "template"
    DOC_ONLY = "doc_only"

class DocMode(str, Enum):
    NONE = "none"
    FIXED = "fixed"
    VARIABLE = "variable"

class JobStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAIL = "fail"

@dataclass
class ContactJob:
    number: str
    message_mode: MessageMode
    doc_mode: DocMode
    contact_name: Optional[str] = None
    message_text: Optional[str] = None
    message_key: Optional[str] = None
    doc_path: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    status_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "contact_name": self.contact_name or "",
            "message_mode": self.message_mode.value if isinstance(self.message_mode, MessageMode) else self.message_mode,
            "message_text": self.message_text or "",
            "message_key": self.message_key or "",
            "doc_mode": self.doc_mode.value if isinstance(self.doc_mode, DocMode) else self.doc_mode,
            "doc_path": self.doc_path or "",
            "status": self.status.value if isinstance(self.status, JobStatus) else self.status,
            "status_message": self.status_message or ""
        }
