from utsam.dbs.schemas.masterdata.grades import PgGradesTable
from utsam.bases.params import _SELECT_

def get_score(grades_df, grade, finetuning, na_value=_SELECT_):
    if grade == na_value:
        return 0
    temp_df = grades_df.copy()
    temp_df.set_index(PgGradesTable.grade_abbrev, inplace=True)
    grade_min = temp_df.at[grade, PgGradesTable.grade_min]
    grade_max = temp_df.at[grade, PgGradesTable.grade_max]
    return grade_min + (grade_max - grade_min) * finetuning / 100


def get_grade(grades_df, score):
    temp_df = grades_df.copy()
    min_grade_mask = temp_df[PgGradesTable.grade_min] <= score
    max_grade_mask = temp_df[PgGradesTable.grade_max] > score
    
    grade = temp_df.loc[min_grade_mask & max_grade_mask, PgGradesTable.grade_abbrev].values
    if len(grade) > 0:
        return grade[0]
    return None