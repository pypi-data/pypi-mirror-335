from dataclasses import dataclass

@dataclass
class PgAssignmentSubcriteriaStudentScoresTable:
    name: str = "assignment_subcriteria_student_scores"
    subcriteria_student_score_id: str = 'subcriteria_student_score_id'
    subcriteria_student_score: str = 'subcriteria_student_score'
    subcriteria_student_score_comments: str = 'subcriteria_student_score_comments'
    subcriteria_student_mark: str = 'subcriteria_student_mark'
    subcriteria_grade_abbrev: str = 'subcriteria_grade_abbrev'
    subcriteria_grade_desc: str = 'subcriteria_grade_desc'
