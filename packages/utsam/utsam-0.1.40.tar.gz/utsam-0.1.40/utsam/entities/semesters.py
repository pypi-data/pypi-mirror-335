from typing import Optional
from pydantic import BaseModel


class Semester(BaseModel):
    semester_id: str
    semester_name: str
    semester_abbrev2: str
    semester_abbrev3: str

    def __hash__(self):
        return hash((self.semester_name))