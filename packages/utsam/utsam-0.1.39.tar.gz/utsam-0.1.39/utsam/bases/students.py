import time
import json
from pathlib import Path
import pendulum
import pandas as pd
from sqlalchemy import update


from utsam.bases.params import _SELECT_, _LOGS_
from utsam.dbs.schemas.masterdata.employees import PgEmployeesTable
from utsam.dbs.schemas.masterdata.students import PgStudentsTable
from utsam.dbs.schemas.masterdata.assignments import PgAssignmentsTable
from utsam.dbs.schemas.masterdata.criterias import PgAssignmentCriteriasTable
from utsam.dbs.schemas.masterdata.subcriterias import PgAssignmentSubcriteriasTable
from utsam.dbs.schemas.transactions.assignment_criteria_student_scores import PgAssignmentCriteriaStudentScoresTable
from utsam.dbs.schemas.transactions.assignment_subcriteria_student_scores import PgAssignmentSubcriteriaStudentScoresTable

from utsam.bases.grades import get_grade


def get_groups_by_employee(employee, data):
    if employee == _SELECT_:
        return [_SELECT_]
    employees_mask = data[PgEmployeesTable.employee_first_name] == employee
    temp_df = data.loc[employees_mask, ]
    if len(temp_df) > 0:
        return [_SELECT_] +  sorted(list(temp_df[PgStudentsTable.group_name].astype(str).unique()))
    return [_SELECT_]

def get_students_ids_by_employee_and_group(employee, group_name, data):
    if employee == _SELECT_:
        return [_SELECT_]
    employees_mask = data[PgEmployeesTable.employee_first_name] == employee
    group_mask = data[PgStudentsTable.group_name] == group_name
    temp_df = data.loc[employees_mask & group_mask, ]
    if len(temp_df) > 0:
        return [_SELECT_] +  sorted(list(temp_df[PgStudentsTable.student_id].astype(str).unique()))
    return [_SELECT_]

def get_students_ids_by_employee(employee, data):
    if employee == _SELECT_:
        return [_SELECT_]
    employees_mask = data[PgEmployeesTable.employee_first_name] == employee
    temp_df = data.loc[employees_mask, ]
    if len(temp_df) > 0:
        return [_SELECT_] +  sorted(list(temp_df[PgStudentsTable.student_id].astype(str).unique()))
    return [_SELECT_]
    
def get_student_name(student_id, data):
    if student_id == _SELECT_:
        return None
    student_mask = data[PgStudentsTable.student_id] == int(student_id)
    temp_df = data.loc[student_mask, ]
    student_name = temp_df[PgStudentsTable.student_name].values
    if len(student_name) > 0:
        return student_name[0]
    return None


class StudentMarking:
    def __init__(
        self,
        student_id,
        student_name,
        tutor_name,
        assignment,
        grades_df: pd.DataFrame,
        engine,
    ):
        self.student_id = student_id
        self.student_name = student_name
        self.tutor_name = tutor_name
        self.assignment = assignment
        self.grades_df = grades_df.copy()
        self.criteria_dict: dict = {}
        self.score = 0
        self.grade = None
        self.engine = engine

    def print(self):
        print(f"Final Mark for '{self.student_name}' ({self.student_id}) = {self.score} ({self.grade})")
    
    def reset_score_and_grade(self):
        self.score = 0
        self.grade = None

    def append_criteria(self, criteria):
        self.criteria_dict[criteria.criteria_id] = criteria

    def set_score_and_grade(self):
        if len(self.criteria_dict) > 0:
            self.reset_score_and_grade()
            print("--------- Criterias ---------")
            for criteria_id, crit in self.criteria_dict.items():
                print(f"{criteria_id} -> crit.score: {crit.score} ({type(crit.score)})")
                print(f"{criteria_id} -> crit.weight: {crit.weight} ({type(crit.weight)})")

            self.score = sum([crit.score * crit.weight for _, crit in self.criteria_dict.items()])
            self.grade = get_grade(self.grades_df, self.score)
            print("\n--------- Assignment ---------")
            print(f"score: {self.score} ({type(self.score)})")
            print(f"grade: {self.grade} ({type(self.grade)})")


    def to_dict(self):
        if len(self.criteria_dict) > 0:
            return {
                PgStudentsTable.student_id: self.student_id,
                PgStudentsTable.student_name: self.student_name,
                "tutor_name": self.tutor_name,
                "course_code": self.assignment.course_code,
                "semester": self.assignment.semester,
                "year": self.assignment.year,
                "assignment": self.assignment.assignment,
                "grade": self.grade,
                "score": self.score,
                #"comments": self.comments,
                "criterias": {crit_id: crit.to_dict() for crit_id, crit in self.criteria_dict.items()}
            }

    def to_json(self):
        logs_path = Path.cwd() / _LOGS_ / self.tutor_name
        student_path = logs_path / self.student_id
        student_path.mkdir(parents=True, exist_ok=True)

        now = pendulum.now("Australia/Sydney")
        date_str = now.to_w3c_string().replace("+", "_")
        json_file_name = f'{student_path}/{self.assignment.course_code}-{self.assignment.year}{self.assignment.semester}-{self.assignment.assignment}_{self.student_id}_{date_str}.json'
        
        json_data = self.to_dict()

        try:
            with open(json_file_name, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4, default=str)
        except:
            print(f"Can not write log file into {student_path}. Please save locally this output as a json file")
            print(json.dumps(json_data, indent=4, default=str))
        finally:
            return json_file_name


class AssignmentMarkingStudent:
    def __init__(
        self,
        assignment_id: str,
        student_id: int,
        all_marks_df: pd.DataFrame,
        grades_df: pd.DataFrame,
    ):
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.all_marks_df = all_marks_df.copy()
        self.grades_df = grades_df.copy()
        self.assignment_mask = None
        self.student_mask = None
        self.student_marks_df: pd.DataFrame = None
        self.group_name: str = None
        self.score: float = 0
        self.grade: str = None
        self.student_name: str = None
        self.assignment_abbrev: str = None

    def reset_score_and_grade(self):
        self.score = 0
        self.grade = None

    def filter_marks(self):
        self.assignment_mask = self.all_marks_df[PgAssignmentsTable.assignment_id].astype('str') == str(self.assignment_id)
        self.student_mask = self.all_marks_df[PgStudentsTable.student_id] == int(self.student_id)
        self.student_marks_df = self.all_marks_df[self.assignment_mask & self.student_mask].copy()
        self.student_marks_df = self.student_marks_df.sort_values(by=[PgAssignmentCriteriasTable.criteria_desc], ascending=True).reset_index()
        if len(self.student_marks_df) > 0:
            self.student_name = self.student_marks_df.at[0, PgStudentsTable.student_name]
            self.group_name = self.student_marks_df.at[0, PgStudentsTable.group_name]
            self.assignment_abbrev = self.student_marks_df.at[0, PgAssignmentsTable.assignment_abbrev]

    def set_score_and_grade(self):
        self.filter_marks()
        if len(self.student_marks_df) > 0:
            self.reset_score_and_grade()
            self.student_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_mark] = self.student_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_score] * self.student_marks_df[PgAssignmentCriteriasTable.criteria_weight]
            self.score = (self.student_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_mark]).sum()
            self.grade = get_grade(self.grades_df, self.score)

    def display_student_marks(self):
        self.set_score_and_grade()
        print(f"#################### {self.student_name} ({self.student_id}) - {self.group_name} ####################\n")

        if self.grade:
            print(f"MARK FOR {self.assignment_abbrev}: {self.score} ({self.grade})\n")

            for row_id in range(len(self.student_marks_df)):
                print("---------------------------------------------------------------------------\n")
                print(f"CRITERIA '{self.student_marks_df.at[row_id, PgAssignmentCriteriasTable.criteria_desc]}'")
                print(f"Score: {self.student_marks_df.at[row_id, PgAssignmentCriteriaStudentScoresTable.criteria_student_score]} ({get_grade(self.grades_df, self.student_marks_df.at[row_id, PgAssignmentCriteriaStudentScoresTable.criteria_student_score])})")
                print(f"Comments:\n{self.student_marks_df.at[row_id, PgAssignmentCriteriaStudentScoresTable.criteria_student_score_comments]}")
        else:
            print("No grade found in database for this student")


class AssignmentSubcriteriaMarkingStudent:
    def __init__(
        self,
        assignment_id: str,
        student_id: int,
        all_marks_df: pd.DataFrame,
        grades_df: pd.DataFrame,
    ):
        self.assignment_id = assignment_id
        self.student_id = student_id
        self.all_marks_df = all_marks_df.copy()
        self.grades_df = grades_df.copy()
        self.assignment_mask = None
        self.student_mask = None
        self.student_marks_df: pd.DataFrame = None
        self.group_name: str = None
        self.score: float = 0
        self.grade: str = None
        self.student_name: str = None
        self.assignment_abbrev: str = None

    def reset_score_and_grade(self):
        self.score = 0
        self.grade = None

    def filter_marks(self):
        self.assignment_mask = self.all_marks_df[PgAssignmentsTable.assignment_id].astype('str') == str(self.assignment_id)
        self.student_mask = self.all_marks_df[PgStudentsTable.student_id] == int(self.student_id)
        self.student_marks_df = self.all_marks_df[self.assignment_mask & self.student_mask].copy()
        self.student_marks_df = self.student_marks_df.sort_values(by=[PgAssignmentSubcriteriasTable.subcriteria_desc], ascending=True).reset_index()
        if len(self.student_marks_df) > 0:
            self.student_name = self.student_marks_df.at[0, PgStudentsTable.student_name]
            self.group_name = self.student_marks_df.at[0, PgStudentsTable.group_name]
            self.assignment_abbrev = self.student_marks_df.at[0, PgAssignmentsTable.assignment_abbrev]


    def set_score_and_grade(self):
        self.filter_marks()
        if len(self.student_marks_df) > 0:
            self.reset_score_and_grade()
            self.student_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_mark] = self.student_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_score] * self.student_marks_df[PgAssignmentCriteriasTable.criteria_weight]
            self.score = (self.student_marks_df[PgAssignmentCriteriaStudentScoresTable.criteria_student_mark]).sum()
            self.grade = get_grade(self.grades_df, self.score)

    def display_student_marks(self):
        self.set_score_and_grade()
        print(f"########## {self.student_name} ({self.student_id}) - {self.group_name} ##########\n")

        if len(self.student_marks_df) > 0:
            print(f"\tMARK FOR {self.assignment_abbrev}: {self.score} ({self.grade})\n")

            crit_ids_list = self.student_marks_df[PgAssignmentCriteriasTable.criteria_id].unique()
            subcrit_ids_list = self.student_marks_df[PgAssignmentSubcriteriasTable.subcriteria_id].unique()

            for crit_id in crit_ids_list:
                crit_mask = self.student_marks_df[PgAssignmentCriteriasTable.criteria_id] == crit_id
                crit_desc = self.student_marks_df.loc[crit_mask, PgAssignmentCriteriasTable.criteria_desc].drop_duplicates()
                print("=============================================================")
                print("=")
                print(f"=  CRITERIA '{crit_desc[0]}'")
                print("=")
                print("=============================================================\n")
                
                for subcrit_id in subcrit_ids_list:
                    subcrit_mask = self.student_marks_df[PgAssignmentSubcriteriasTable.subcriteria_id] == subcrit_id
                    row_id = self.student_marks_df.index.get_loc(self.student_marks_df[subcrit_mask].index[0])
                    subcrit_desc = self.student_marks_df.at[row_id, PgAssignmentSubcriteriasTable.subcriteria_desc]

                    print(f"SUBCRITERIA '{subcrit_desc}'\n")
                    print(f"  -> {self.student_marks_df.at[row_id, PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score]} ({get_grade(self.grades_df, self.student_marks_df.at[row_id, PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score])})\n")
                    print(f"  -> {self.student_marks_df.at[row_id, PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score_comments]}")
                    print("-------------------------------\n")
        else:
            print("No grade found in database for this student")
