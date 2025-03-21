from dataclasses import dataclass

@dataclass
class PgAssignmentStudentScoresTable:
    name: str = "assignment_student_scores"
    assignment_student_score: str = 'assignment_student_score'
    assignment_grade_abbrev: str = 'assignment_grade_abbrev'
    assignment_grade_desc: str = 'assignment_grade_desc'
    assignment_student_score_comments: str = 'assignment_student_score_comments'
