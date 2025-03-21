from typing import Optional
import uuid
from pydantic import BaseModel


class AssignmentCriteria(BaseModel):
    criteria_id: str
    assignment_id: str
    criteria_desc: str
    criteria_weight: float

    def __hash__(self):
        return hash((self.criteria_desc, self.assignment_id))
