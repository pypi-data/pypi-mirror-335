from dataclasses import dataclass

@dataclass
class PgStudentsTable:
    name: str = "students"
    student_id: str = 'student_id'
    canvas_student_id: str = 'canvas_student_id'
    student_name: str = 'student_name'
    student_email: str = 'student_email'
    student_status: str = 'student_status'
    group_id: str = 'group_id'
    canvas_group_id: str = 'canvas_group_id'
    group_name: str = 'group_name'
