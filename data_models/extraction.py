from pydantic import BaseModel
from typing import List, Optional

class ResumeExtractedData(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    skills: List[str]
    education: List[str]
    experience: List[str]
    raw_text: str