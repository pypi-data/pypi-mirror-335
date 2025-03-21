from typing import Optional
from pydantic import BaseModel


class Session(BaseModel):
    session_id: str
    session_year: int
    course_id: str
    semester_id: str
    
    def __hash__(self):
        return hash((self.session_year, self.course_id, self.semester_id))