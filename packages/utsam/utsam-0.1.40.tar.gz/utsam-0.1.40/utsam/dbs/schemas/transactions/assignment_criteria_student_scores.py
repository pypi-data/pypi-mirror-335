from dataclasses import dataclass

@dataclass
class PgAssignmentCriteriaStudentScoresTable:
    name: str = "assignment_criteria_student_scores"
    criteria_student_score_id: str = 'criteria_student_score_id'
    criteria_student_score: str = 'criteria_student_score'
    criteria_student_score_comments: str = 'criteria_student_score_comments'
    criteria_student_mark: str = 'criteria_student_mark'
    criteria_grade_abbrev: str = 'criteria_grade_abbrev'
    criteria_grade_desc: str = 'criteria_grade_desc'

