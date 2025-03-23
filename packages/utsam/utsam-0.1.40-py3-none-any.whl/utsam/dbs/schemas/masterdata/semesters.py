from dataclasses import dataclass

@dataclass
class PgSemestersTable:
    name: str = "semesters"
    semester_id: str = 'semester_id'
    semester_name: str = 'semester_name'
    semester_abbrev2: str = 'semester_abbrev2'
    semester_abbrev3: str = 'semester_abbrev3'
