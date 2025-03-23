from typing import Optional
from pydantic import BaseModel


class Student(BaseModel):
    student_id: int
    canvas_student_id: int
    student_name: str
    student_email: str
    student_status: str

    def __hash__(self):
        return hash((self.student_id))
