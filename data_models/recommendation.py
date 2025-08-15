from pydantic import BaseModel
from typing import List

class Recommendation(BaseModel):
    jobs: List[str]
    skills: List[str]