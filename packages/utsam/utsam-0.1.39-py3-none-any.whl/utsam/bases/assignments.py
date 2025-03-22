import os
import time
import json
from pathlib import Path
import pandas as pd
import altair as alt
from sqlalchemy import create_engine, MetaData, Table, and_, update
from sqlalchemy.sql import column
from pydantic import BaseModel


from utsam.bases.params import SemesterParams, _LOGS_, ZSCORE_COL
from utsam.bases.criterias import Criteria
from utsam.bases.tutors import AssignmentCriteriaMarkingTutor
from utsam.dbs.schemas.masterdata.students import PgStudentsTable
from utsam.dbs.schemas.masterdata.criterias import PgAssignmentCriteriasTable
from utsam.dbs.schemas.masterdata.employees import PgEmployeesTable
from utsam.dbs.schemas.masterdata.assignments import PgAssignmentsTable
from utsam.dbs.schemas.transactions.assignment_criteria_student_scores import PgAssignmentCriteriaStudentScoresTable


class AssignmentModel(BaseModel):
    course_code: int
    semester: int
    year: float
    assignment: str
    assignment_id: str

    @property
    def session(self):
        return f"{self.year}-{self.semester}" if self.semester else self.year


class Assignment:
    def __init__(
        self,
        course_code: int,
        semester: str,
        year: str,
        assignment: str,
        assignment_id: str,
    ):
        self.course_code: int = course_code
        self.semester: int = semester
        self.year: float = year
        self.assignment: str = assignment
        self.session = f"{self.year}-{self.semester}" if self.semester else self.year
        self.assignment_id = assignment_id


class AssignmentDir(Assignment):
    def __init__(
        self,
        course_code: int,
        semester: str,
        year: str,
        assignment: str,
        assignment_id: str,
    ):
        super().__init__(
            course_code = course_code,
            semester = semester,
            year = year,
            assignment = assignment,
            assignment_id = assignment_id,
        )
        self.at_path = None
        self.data_folder = 'data'
        self.data_raw_folder = '0-raw'
        self.data_int_folder = '1-interim'
        self.data_final_folder = '2-final'
        self.data_path = None
        self.raw_path = None
        self.interim_path = None
        self.final_path = None
        self.seed = (int(self.year) * 10) + 1 if self.semester == SemesterParams.autumn else 2

    def set_paths(self):
        self.at_path = Path(os.getcwd())
        self.data_path = self.at_path / self.data_folder
        self.raw_path = self.data_path / self.data_raw_folder
        self.interim_path = self.data_path / self.data_int_folder
        self.final_path = self.data_path / self.data_final_folder

        for item in [self.raw_path, self.interim_path, self.final_path]:
            item.mkdir(parents=True, exist_ok=True)

    #def set_colab(self):
    #    self.at_path = Path(f'content/MyDrive/{course}/{session}/Assignments/{assignment}')
    #    from google.colab import drive
    #
    #    drive.mount('./content')


class AssignmentMarking(AssignmentDir):
    def __init__(
        self,
        course_code: int,
        semester: str,
        year: str,
        assignment: str,
        assignment_id: str,
        criterias_df: pd.DataFrame,
        all_marks_df: pd.DataFrame,
    ):
        super().__init__(
            course_code = course_code,
            semester = semester,
            year = year,
            assignment = assignment,
            assignment_id = assignment_id,
        )
        self.criterias_df = criterias_df.copy()
        self.criteria_ids: dict = {}
        self.criteria_dict: dict = {}
        self.criteria_tutor_dict: dict = {}
        self.all_marks_df = all_marks_df.copy()
        self.tutor_names = list(self.all_marks_df[PgEmployeesTable.employee_first_name].unique())
        self.score = 0
        self.grade = None
        self.all_new_marks_df: pd.DataFrame = None
        self.new_score_col = f'new_{PgAssignmentCriteriaStudentScoresTable.criteria_student_score}'
        self.weighted_score_col = f'weighted_{PgAssignmentCriteriaStudentScoresTable.criteria_student_score}'
        self.new_weighted_score_col = f'new_{self.weighted_score_col}'
        self.set_paths()
        self.grouping_cols = [
            PgAssignmentsTable.assignment_id,
            PgStudentsTable.group_id,
            PgStudentsTable.student_id,
            PgStudentsTable.student_name,
            PgEmployeesTable.employee_first_name,
        ]
        self.student_marks: pd.DataFrame = None

    @property
    def n_criterias(self):
        return len(self.criteria_ids)
        
    def filter_at(self):
        criteria_mask = self.criterias_df[PgAssignmentsTable.assignment_id].astype('str') == str(self.assignment_id)
        self.criterias_df = self.criterias_df[criteria_mask]

    def set_at_criterias(self):
        self.filter_at()
        self.criteria_ids = {i: crit_id for i, crit_id in enumerate(self.criterias_df[PgAssignmentCriteriasTable.criteria_id].unique())}
        self.criteria_dict = {k: Criteria(criteria_id=crit_id) for k, crit_id in self.criteria_ids.items()}
        self.criteria_tutor_dict = {k: None for k, _ in self.criteria_ids.items()}

    def set_at_tutor_criterias(self):
        self.set_at_criterias()

        for i, crit_id in self.criteria_ids.items():
            tutor_crit_list = []

            for tutor_name in self.tutor_names:
                tutor_crit = AssignmentCriteriaMarkingTutor(
                    assignment_id=self.assignment_id,
                    criteria_id=crit_id,
                    tutor_first_name=tutor_name,
                    all_marks_df=self.all_marks_df,
                )
                tutor_crit.standardise(new_mean=75, new_std=15)

                tutor_crit_list.extend([tutor_crit])

            self.criteria_tutor_dict[i] = tutor_crit_list

    def get_all_marks(self):
        all_marks_list = []
        for _, crit in self.criteria_tutor_dict.items():
            for tutor in crit:
                all_marks_list.extend([tutor.tutor_marks_df])
        self.all_new_marks_df = pd.concat(all_marks_list, axis=0)


    def standardise_tutor_criteria(self, new_mean=85, new_std=5):
        self.set_at_tutor_criterias()
        for i, tutor_crit_marks in self.criteria_tutor_dict.items():
            for tutor_marks in tutor_crit_marks:
                tutor_marks.standardise(new_mean=new_mean, new_std=new_std)
        self.get_all_marks()

    def find_tutor_rank_by_name(self, tutor_name):
        return self.tutor_names.index(tutor_name)

    def plot_hist_by_criteria_tutor(self, criteria_rank, tutor_rank, marks_type='raw', employee_col_name='employee_first_name', bins=20):
        crit_df = self.criteria_tutor_dict.get(criteria_rank)[tutor_rank].tutor_marks_df.copy().reset_index(False)
        col_name = PgAssignmentCriteriaStudentScoresTable.criteria_student_score if marks_type == 'raw' else self.new_score_col
        crit_desc = crit_df[PgAssignmentCriteriasTable.criteria_desc].unique()[0]
        tutor_name = crit_df[PgEmployeesTable.employee_first_name].unique()[0]

        return alt.Chart(crit_df, title=f'Histogram of {marks_type} marks by {tutor_name} for {crit_desc}').mark_bar(
            opacity=0.3,
            binSpacing=0
        ).encode(
            alt.X(f'{col_name}:Q', bin = alt.BinParams(maxbins=bins)),
            alt.Y('count()'),
            alt.Color(f'{employee_col_name}:N')
        )
    
    def plot_criteria_hist_by_tutor(self, criteria_rank, marks_type='raw', employee_col_name='employee_first_name', bins=20):
        crit_df = self.all_marks_for_criteria(criteria_rank=criteria_rank)
        col_name = 'criteria_student_score' if marks_type == 'raw' else self.new_score_col
        crit_desc = crit_df[PgAssignmentCriteriasTable.criteria_desc].unique()[0]

        return alt.Chart(crit_df, title=f'Histogram of {marks_type} marks for {crit_desc}').mark_bar(
            opacity=0.3,
            binSpacing=0
        ).encode(
            alt.X(f'{col_name}:Q', bin = alt.BinParams(maxbins = 20)),
            alt.Y('count()', stack=None),
            facet=alt.Facet(f'{employee_col_name}:N', columns=1),
            tooltip=[
                f'{employee_col_name}:N', 
                alt.Tooltip(f'{col_name}:Q', bin = alt.BinParams(maxbins=bins)),
                'count()',
            ],
        ).resolve_axis(
            x='independent',
            y='independent',
        ).properties(
            width=600,
            height=250
        )

    def plot_at_marks_hist_by_tutor(self, marks_type='raw',employee_col_name='employee_first_name', bins=20):
        col_name = PgAssignmentCriteriaStudentScoresTable.criteria_student_score if marks_type == 'raw' else self.new_score_col

        return alt.Chart(self.student_marks, title=f'Histogram of {marks_type} marks by tutor').mark_bar(
            opacity=0.3,
            binSpacing=0
        ).encode(
            alt.X(f'{col_name}:Q', bin = alt.BinParams(maxbins=20)),
            alt.Y('count()'),
            facet=alt.Facet(f'{employee_col_name}:N', columns=1),
            tooltip=[
                f'{employee_col_name}:N', 
                alt.Tooltip(f'{col_name}:Q', bin = alt.BinParams(maxbins=bins)),
                'count()',
            ],
        ).resolve_axis(
            x='independent',
            y='independent',
        ).properties(
            width=600,
            height=250
        )
            
    def all_marks_for_criteria(self, criteria_rank):
        all_marks_list = []
        for tutor in self.criteria_tutor_dict.get(criteria_rank):
            all_marks_list.extend([tutor.tutor_marks_df])
        return pd.concat(all_marks_list, axis=0)


    def plot_hist_by_criteria(self, criteria_rank, marks_type='raw', employee_col_name='employee_first_name', bins=20):
        crit_df = self.all_marks_for_criteria(criteria_rank=criteria_rank)
        col_name = 'criteria_student_score' if marks_type == 'raw' else self.new_score_col

        return alt.Chart(crit_df, title=f'Histogram of {marks_type} marks').mark_bar(
            opacity=0.3,
            binSpacing=0
        ).encode(
            alt.X(f'{col_name}:Q', bin = alt.BinParams(maxbins=bins)),
            alt.Y('count()'),
            alt.Color(f'{employee_col_name}:N'),
            column=f'{PgAssignmentCriteriasTable.criteria_desc}:N'
        )

    def plot_hists(self, marks_type='raw', employee_col_name=PgEmployeesTable.employee_first_name, bins=20):
        col_name = PgAssignmentCriteriaStudentScoresTable.criteria_student_score if marks_type == 'raw' else self.new_score_col

        return alt.Chart(self.all_new_marks_df, title=f'Histogram of {marks_type} marks').mark_bar(
            opacity=0.3,
            binSpacing=0
        ).encode(
            alt.X(f'{col_name}:Q', bin = alt.BinParams(maxbins = 20)),
            alt.Y('count()', stack=None),
            alt.Color(f'{employee_col_name}:N'),
            facet=alt.Facet(f'{PgAssignmentCriteriasTable.criteria_desc}:N', columns=1),
            tooltip=[
                f'{employee_col_name}:N', 
                alt.Tooltip(f'{col_name}:Q', bin = alt.BinParams(maxbins=bins)),
                'count()',
            ],
        ).resolve_axis(
            x='independent',
            y='independent',
        ).properties(
            width=600,
            height=250
        )

    def reset_score_and_grade(self):
        self.score = 0
        self.grade = None

    def set_score_and_grade(self):
        if len(self.all_new_marks_df) > 0:
            self.reset_score_and_grade()

            result_cols = [PgAssignmentCriteriaStudentScoresTable.criteria_student_score, self.new_score_col]
            temp_df = self.all_new_marks_df.copy()

            for col_name in result_cols:
                temp_df[col_name] = temp_df[col_name] * temp_df[PgAssignmentCriteriasTable.criteria_weight]

            self.student_marks = temp_df.groupby(self.grouping_cols).agg({col_name:'sum' for col_name in result_cols}).reset_index().sort_values([PgStudentsTable.student_name])

    def standardise_criteria_by_tutor(self, tutor_name, new_mean=85, new_std=5):
        # Todo: standardise with specifc mean and std for a single tutor
        pass

    def to_dict(self):
        if len(self.criteria_dict) > 0:
            return {
                "student_id": self.student_id,
                "student_name": self.student_name,
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
        logs_paths = Path.cwd() / _LOGS_ / self.tutor_name
        logs_paths.mkdir(parents=True, exist_ok=True)
        json_data = self.to_dict()
        json_file_name = f'{logs_paths}/{self.assignment.course_code}-{self.assignment.year}{self.assignment.semester}-{self.assignment.assignment}_{self.student_id}_{time.time()}.json'
        try:
            with open(json_file_name, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        except:
            print(f"Can not write log file into {logs_paths}. Please save locally this output as a json file")
            print(json.dumps(json_data, indent=4))
        finally:
            return json_file_name

    def to_sql(self):
        json_data = self.to_dict()

        update_stmt = (
            update(user_table)
            .where(user_table.c.id == address_table.c.user_id)
            .where(address_table.c.email_address == "patrick@aol.com")
            .values(
                {
                    user_table.c.fullname: "Pat",
                    address_table.c.email_address: "pat@aol.com",
                }
            )
        )
        print(update_stmt)
