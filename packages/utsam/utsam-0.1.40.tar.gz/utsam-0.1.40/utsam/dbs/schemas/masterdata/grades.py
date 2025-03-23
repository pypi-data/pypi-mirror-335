from dataclasses import dataclass

@dataclass
class PgGradesTable:
    name: str = "grades"
    grade_abbrev: str = 'grade_abbrev'
    grade_name: str = 'grade_name'
    grade_desc: str = 'grade_desc'
    grade_min: str = 'grade_min'
    grade_max: str = 'grade_max'