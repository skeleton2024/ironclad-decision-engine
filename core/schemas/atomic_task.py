from typing import List
from pydantic import BaseModel

class AtomicTask(BaseModel):
    id: str
    name: str
    duration_estimate: float
    dependencies: List[str] = []
