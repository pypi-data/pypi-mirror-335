from typing import Optional
from pydantic import BaseModel


class Grade(BaseModel):
    grade_abbrev: str
    grade_name: str
    grade_desc: str
    grade_min: int
    grade_max: int

    def __hash__(self):
        return hash((self.grade_abbrev))