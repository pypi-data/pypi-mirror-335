from typing import Optional
from pydantic import BaseModel


class AssignmentGroup(BaseModel):
    group_id: str
    group_name: str
    assignment_id: str
    employee_id: str

    def __hash__(self):
        return hash((self.group_name, self.assignment_id, self.employee_id))
