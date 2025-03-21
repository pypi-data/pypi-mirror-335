from typing import Optional
from pydantic import BaseModel


class Employee(BaseModel):
    employee_id: str
    employee_first_name: str
    employee_last_name: str
    staff_id: int

    def __hash__(self):
        return hash((self.staff_id))