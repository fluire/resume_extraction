from pydantic import BaseModel
from typing import List, Optional

class EvaluationResult(BaseModel):
    score: float
    strengths: List[str]
    weaknesses: List[str]
    summary: Optional[str]