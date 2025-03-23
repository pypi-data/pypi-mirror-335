import pandas as pd

from utsam.dbs.schemas.masterdata.criterias import PgAssignmentCriteriasTable
from utsam.dbs.schemas.masterdata.subcriterias import PgAssignmentSubcriteriasTable
from utsam.bases.grades import get_grade


def get_criteria(data, criteria_id):
    criteria_mask = data[PgAssignmentCriteriasTable.criteria_id] == criteria_id
    print(data.loc[criteria_mask, PgAssignmentCriteriasTable.criteria_desc].drop_duplicates().values)
    return data.loc[criteria_mask, [PgAssignmentSubcriteriasTable.subcriteria_name, PgAssignmentSubcriteriasTable.subcriteria_desc, PgAssignmentSubcriteriasTable.subcriteria_weight]].drop_duplicates()


class Criteria:
    def __init__(
        self,
        criteria_id: str,
        criteria_desc: str = None,
    ):
        self.criteria_id: str = criteria_id
        self.criteria_desc: str = criteria_desc


class CriteriaMarking(Criteria):
    def __init__(
        self,
        criteria_id: str,
        criteria_df: pd.DataFrame,
        grades_df: pd.DataFrame,
    ):
        super().__init__(
            criteria_id = criteria_id,
        )
        self.criteria_df = criteria_df.copy()
        self.grades_df = grades_df.copy()
        self.criteria_grade_desc = None
        self.weight = 0
        self.subcriteria_dict: dict = {}
        self.score = 0
        self.grade = None
        self.comments = None
        self.set_criteria()

    def set_criteria(self):
        criteria_id_mask = self.criteria_df[PgAssignmentCriteriasTable.criteria_id].astype('str') == str(self.criteria_id)
        criteria_rows = self.criteria_df.loc[criteria_id_mask, ]
        if len(criteria_rows) > 0:
            criteria_rows.reset_index(inplace=True)
            self.criteria_desc = criteria_rows.at[0, PgAssignmentCriteriasTable.criteria_desc]
            self.weight = criteria_rows.at[0, PgAssignmentCriteriasTable.criteria_weight]
            self.criteria_grade_desc = criteria_rows[[
                PgAssignmentSubcriteriasTable.subcriteria_name,
                PgAssignmentSubcriteriasTable.subcriteria_desc,
                PgAssignmentSubcriteriasTable.subcriteria_weight,
                ]]
            self.criteria_grade_desc = self.criteria_grade_desc.drop_duplicates()
        else:
            print(f"No criteria found for {self.criteria_id}")

    def reset_score_and_grade(self):
        self.score = 0
        self.grade = None

    def set_score_and_grade(self):
        if len(self.subcriteria_dict) > 0:
            self.reset_score_and_grade()
            self.score = sum([subcrit.score * subcrit.weight for _, subcrit in self.subcriteria_dict.items()])
            self.grade = get_grade(self.grades_df, self.score)

    def set_comments(self):
        if len(self.subcriteria_dict) > 0:
            self.comments = '\n'.join([subcrit.comments for _, subcrit in self.subcriteria_dict.items()])

    def check_weights(self):
        if len(self.subcriteria_dict) > 0:
            assert sum([subcrit.weight for _, subcrit in self.subcriteria_dict.items()]) == 1, "Sum of weights doesn't equal to 1 (Missing subcriteria)"

    def print(self):
        print(f"Score for '{self.criteria_desc}' = {self.score} ({self.grade})")
        for subscrit_id, subcrit in self.subcriteria_dict.items():
            print(f"{subcrit.subcriteria_desc}: {subcrit.score} * {subcrit.weight} ({subcrit.grade})")

    def to_dict(self):
        if len(self.subcriteria_dict) > 0:
            return {
                "criteria_id": self.criteria_id,
                "criteria_desc": self.criteria_desc,
                "weight": self.weight,
                "grade": self.grade,
                "score": self.score,
                "comments": self.comments,
                "subcriterias": {subcriteria_id: subcrit.to_dict() for subcriteria_id, subcrit in self.subcriteria_dict.items()}
            }

    def get_criteria_grade_desc(self):
        print(self.criteria_desc)
        return self.criteria_grade_desc

    def append_subcriteria(self, subcriteria):
        self.subcriteria_dict[subcriteria.subcriteria_id] = subcriteria

    def set_marking_items(self):
        self.set_score_and_grade()
        self.set_comments()
