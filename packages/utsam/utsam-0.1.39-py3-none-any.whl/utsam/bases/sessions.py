from typing import Optional
from pydantic import BaseModel


class Session(BaseModel):
    session_id: str
    session_year: int
    course_id: str
    semester_id: str
    