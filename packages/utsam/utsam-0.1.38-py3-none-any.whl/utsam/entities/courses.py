from typing import Optional
from pydantic import BaseModel


class Course(BaseModel):
    course_id: str
    course_code: int
    course_name: str
    course_abbrev: str

    def __hash__(self):
        return hash((self.course_code))