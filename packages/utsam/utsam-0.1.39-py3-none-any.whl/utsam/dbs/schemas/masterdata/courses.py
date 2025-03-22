from dataclasses import dataclass

@dataclass
class PgCoursesTable:
    name: str = "courses"
    course_id: str = 'course_id'
    course_code: str = 'course_code'
    course_name: str = 'course_name'
    course_abbrev: str = 'course_abbrev'