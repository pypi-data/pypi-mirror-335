from typing import Optional
import uuid
from pydantic import BaseModel


class AssignmentSubCriteria(BaseModel):
    subcriteria_id: str
    criteria_id: str
    subcriteria_name: str
    subcriteria_desc: str
    subcriteria_weight: float

    def __hash__(self):
        return hash((self.criteria_id, self.subcriteria_name))
