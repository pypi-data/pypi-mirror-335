from dataclasses import dataclass

@dataclass
class PgEmployeesTable:
    name: str = "employees"
    employee_id: str = 'employee_id'
    employee_first_name: str = 'employee_first_name'
    employee_last_name: str = 'employee_last_name'
    staff_id: str = 'staff_id'