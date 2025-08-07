from pydantic import BaseModel
from typing import List

class FeatureOptions(BaseModel):
    features: List[str]