import pandas as pd

from utsam.bases.params import ZSCORE_COL
from utsam.dbs.schemas.masterdata.criterias import PgAssignmentCriteriasTable
from utsam.dbs.schemas.masterdata.subcriterias import PgAssignmentSubcriteriasTable
from utsam.dbs.schemas.transactions.assignment_criteria_student_scores import PgAssignmentCriteriaStudentScoresTable
from utsam.dbs.schemas.masterdata.assignments import PgAssignmentsTable
from utsam.dbs.schemas.masterdata.employees import PgEmployeesTable
from utsam.dbs.schemas.masterdata.students import PgStudentsTable


class AssignmentCriteriaMarkingTutor:
    def __init__(
        self,
        assignment_id: str,
        criteria_id: str,
        tutor_first_name: int,
        all_marks_df: pd.DataFrame,
        zscore_name: str = ZSCORE_COL
    ):
        self.assignment_id = assignment_id
        self.criteria_id = criteria_id
        self.tutor_first_name = tutor_first_name
        self.all_marks_df = all_marks_df.copy()
        self.zscore_name = zscore_name
        self.assignment_mask = None
        self.criteria_mask = None
        self.tutor_mask = None
        self.tutor_marks_df: pd.DataFrame = None
        self.tutor_mean: float = None
        self.tutor_std: float = None
        
    def filter_marks(self):
        self.assignment_mask = self.all_marks_df[PgAssignmentsTable.assignment_id].astype('str') == str(self.assignment_id)
        self.criteria_mask = self.all_marks_df[PgAssignmentCriteriasTable.criteria_id].astype('str') == str(self.criteria_id)
        self.tutor_mask = self.all_marks_df[PgEmployeesTable.employee_first_name] == self.tutor_first_name
        self.tutor_marks_df = self.all_marks_df[self.assignment_mask & self.criteria_mask & self.tutor_mask].copy()

    def get_students_ids(self):
        if len(self.tutor_marks_df) > 0:
            return list(set(self.tutor_marks_df[PgStudentsTable.student_id].sort_values().unique()))
        return []
        
    def compute_zscore(self):
        self.tutor_mean = self.tutor_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_score].mean()
        self.tutor_std = self.tutor_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_score].std(ddof=0)
        self.tutor_marks_df[self.zscore_name] = (self.tutor_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_score] - self.tutor_mean) / self.tutor_std

    def calculate_new_score(self, new_mean, new_std):
        self.tutor_marks_df[f"new_{PgAssignmentCriteriaStudentScoresTable.criteria_student_score}"] = self.tutor_marks_df[self.zscore_name] * new_std + new_mean
        self.tutor_marks_df[f"new_{PgAssignmentCriteriaStudentScoresTable.criteria_student_score}"].clip(lower=0, upper=100, inplace=True)

    def standardise(self, new_mean, new_std):
        self.filter_marks()
        self.compute_zscore()
        self.calculate_new_score(new_mean=new_mean, new_std=new_std)