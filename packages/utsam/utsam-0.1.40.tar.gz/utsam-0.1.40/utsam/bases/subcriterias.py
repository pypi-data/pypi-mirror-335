import pandas as pd

from utsam.bases.grades import get_score
from utsam.dbs.schemas.masterdata.subcriterias import PgAssignmentSubcriteriasTable
from utsam.dbs.schemas.masterdata.grades import PgGradesTable
from utsam.dbs.schemas.transactions.assignment_subcriteria_grade import PgAssignmentSubcriteriaGrade
from utsam.dbs.schemas.masterdata.criterias import PgAssignmentCriteriasTable


def get_subcriteria(data, criteria_id, subcriteria_id):
    criteria_mask = data[PgAssignmentCriteriasTable.criteria_id] == criteria_id
    subcriteria_mask = data[PgAssignmentSubcriteriasTable.subcriteria_id] == subcriteria_id
    print(data.loc[criteria_mask & subcriteria_mask, PgAssignmentSubcriteriasTable.subcriteria_desc].drop_duplicates().values)
    return data.loc[criteria_mask & subcriteria_mask, [PgGradesTable.grade_abbrev, PgAssignmentSubcriteriaGrade.subcriteria_grade_desc]].drop_duplicates()


class SubcriteriaMarking:
    def __init__(
        self,
        subcriteria_id: str,
        criteria_df: pd.DataFrame,
        grades_df: pd.DataFrame,
        grade: str = None,
        finetune: int = 0,
        comments: str = None,
    ):
        self.subcriteria_id = subcriteria_id
        self.criteria_df = criteria_df.copy()
        self.subcriteria_desc = None
        self.subcriteria_grade_desc = None
        self.grades_df = grades_df.copy()
        self.weight = 0
        self.grade = None
        self.finetune = None
        self.comments = None
        self.score = 0
        self.set_subcriteria()

    def set_subcriteria(self):
        subcriteria_id_mask = self.criteria_df[PgAssignmentSubcriteriasTable.subcriteria_id].astype('str') == str(self.subcriteria_id)
        subcriteria_rows = self.criteria_df.loc[subcriteria_id_mask, ]
        if len(subcriteria_rows) > 0:
            subcriteria_rows.reset_index(inplace=True)
            self.subcriteria_desc = subcriteria_rows.at[0, PgAssignmentSubcriteriasTable.subcriteria_desc]
            self.weight = subcriteria_rows.at[0, PgAssignmentSubcriteriasTable.subcriteria_weight]
            self.subcriteria_grade_desc = subcriteria_rows[[
                PgGradesTable.grade_abbrev,
                PgAssignmentSubcriteriaGrade.subcriteria_grade_desc,
                ]]
            self.subcriteria_grade_desc = self.subcriteria_grade_desc.drop_duplicates()
        else:
            print(f"No subcriteria found for {self.subcriteria_id}")

    def print(self):
        print(f"Score for '{self.subcriteria_desc}' = {self.score} ({self.grade})")

    def to_dict(self):
        return {
            "subcriteria_id": self.subcriteria_id,
            "subcriteria_desc": self.subcriteria_desc,
            "weight": self.weight,
            "grade": self.grade,
            "finetune": self.finetune,
            "comments": self.comments,
            "score": self.score,
        }

    def get_subcriteria_grade_desc(self):
        print(self.subcriteria_desc)
        return self.subcriteria_grade_desc

    def set_marking_items(self, grade, finetune, comments):
        self.grade = grade
        self.finetune = finetune
        self.comments = comments
        self.score = get_score(self.grades_df, self.grade, self.finetune)