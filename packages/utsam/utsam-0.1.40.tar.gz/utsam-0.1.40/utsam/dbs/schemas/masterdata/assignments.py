from dataclasses import dataclass

@dataclass
class PgAssignmentsTable:
    name: str = "assignments"
    assignment_id: str = 'assignment_id'
    assignment_name: str = 'assignment_name'
    assignment_abbrev: str = 'assignment_abbrev'
