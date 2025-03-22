from typing import Optional
import uuid
from pydantic import BaseModel


class AssignmentSubCriteriaGrade(BaseModel):
    subcriteria_grade_id: str
    subcriteria_id: str
    grade_abbrev: str
    subcriteria_grade_desc: str

    def __hash__(self):
        return hash((self.subcriteria_id, self.grade_abbrev))
