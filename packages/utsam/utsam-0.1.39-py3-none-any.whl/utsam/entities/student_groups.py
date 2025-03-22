from typing import Optional
from pydantic import BaseModel


class StudentGroup(BaseModel):
    group_id: str
    student_id: int
    canvas_group_id: Optional[int] = None

    def __hash__(self):
        return hash((self.student_id, self.canvas_group_id))
