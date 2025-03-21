from typing import Optional
from pydantic import BaseModel

class Assignment(BaseModel):
    assignment_id: str
    assignment_name: str
    assignment_abbrev: str
    session_id: str
    canvas_assignment_id: int

    def __hash__(self):
        return hash((self.assignment_abbrev, self.session_id, self.canvas_assignment_id))
