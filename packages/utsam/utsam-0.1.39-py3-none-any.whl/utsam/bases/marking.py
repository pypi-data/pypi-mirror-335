import pickle
import uuid
from sqlalchemy import MetaData, Table, and_, update
from sqlalchemy.sql import column

from utsam.dbs.postgres import PgTable
from utsam.dbs.schemas.transactions.assignment_criteria_student_scores import PgAssignmentCriteriaStudentScoresTable
from utsam.dbs.schemas.masterdata.criterias import PgAssignmentCriteriasTable
from utsam.dbs.schemas.masterdata.students import PgStudentsTable
from utsam.dbs.schemas.transactions.assignment_subcriteria_student_scores import PgAssignmentSubcriteriaStudentScoresTable
from utsam.dbs.schemas.masterdata.subcriterias import PgAssignmentSubcriteriasTable


class AssignmentCriteriaStudentScoresTable(PgTable):
    def __init__(
        self,
        criteria_json: dict,
        student_id: int,
        user_name: str = None,
        password: str = None,
        host: str = None,
        db_name: str = None,
        port: str = '5432',
        schema: str = "public",
        engine = None
    ):
        super().__init__(
            table_name = PgAssignmentCriteriaStudentScoresTable.name,
            user_name = user_name,
            password = password,
            host = host,
            db_name = db_name,
            port = port,
            engine = engine
        )
        self.criteria_json = criteria_json
        self.student_id = student_id
        self.criteria_id = None
        self.criteria_desc: str = None
        self.criteria_grade_desc = None
        self.weight = 0
        self.score = 0
        self.comments = None

        self.sql_statement = None
        self.where_dict = None
        self.where_filters = None
        self.extract_json()

    def extract_json(self):
        self.criteria_id = self.criteria_json.get('criteria_id')
        self.criteria_desc = self.criteria_json.get('criteria_desc')
        self.weight = self.criteria_json.get('weight')
        self.score = self.criteria_json.get('score')
        self.comments = self.criteria_json.get('comments')
        self.where_dict = {
            PgAssignmentCriteriasTable.criteria_id: self.criteria_id ,
            PgStudentsTable.student_id: self.student_id
        }
        self.where_filters = [column(key) == value for key, value in self.where_dict.items()]

    def generate_upsert_sql(self):
        if len(self.select_table(where_dict=self.where_dict)) > 0:
            self.sql_statement = self.generate_update_sql()
        else:
            self.sql_statement = self.generate_insert_sql()

    def generate_update_sql(self):
        return (
            self.table.update()
            .where(and_(*self.where_filters))
            .values(
                {
                    PgAssignmentCriteriaStudentScoresTable.criteria_student_score: self.score,
                    PgAssignmentCriteriaStudentScoresTable.criteria_student_score_comments: self.comments,
                }
            )
        )

    def generate_insert_sql(self):
        return (
            self.table.insert()
            .values(
                {
                    PgAssignmentCriteriaStudentScoresTable.criteria_student_score_id: str(uuid.uuid4()), 
                    PgAssignmentCriteriasTable.criteria_id: self.criteria_id, 
                    PgStudentsTable.student_id: self.student_id,
                    PgAssignmentCriteriaStudentScoresTable.criteria_student_score: self.score,
                    PgAssignmentCriteriaStudentScoresTable.criteria_student_score_comments: self.comments,
                }
            )
        )

    def upsert_marking(self):
        #self.create_marking_df()
        self.generate_upsert_sql()
        try:
            print(self.sql_statement)
            self.execute_sql(sql_statement=self.sql_statement)
        except Exception as e:
            print(f"Error when writing to database: {e}")
        

class AssignmentSubcriteriaStudentScoresTable(PgTable):
    def __init__(
        self,
        subcriteria_json: dict = None,
        student_id: int = None,
        user_name: str = None,
        password: str = None,
        host: str = None,
        db_name: str = None,
        port: str = '5432',
        schema: str = "public",
        engine = None
    ):
        super().__init__(
            table_name = PgAssignmentSubcriteriaStudentScoresTable.name,
            user_name = user_name,
            password = password,
            host = host,
            db_name = db_name,
            port = port,
            engine = engine
        )
        self.subcriteria_json = subcriteria_json
        self.student_id = student_id
        self.subcriteria_id = None
        self.subcriteria_desc: str = None
        self.subcriteria_grade_desc = None
        self.weight = 0
        self.score = 0
        self.comments = None
        self.sql_statement = None
        self.where_dict = None
        self.where_filters = None
        self.extract_json()

    def extract_json(self):
        self.subcriteria_id = self.subcriteria_json.get('subcriteria_id')
        self.subcriteria_desc = self.subcriteria_json.get('subcriteria_desc')
        self.weight = self.subcriteria_json.get('weight')
        self.score = self.subcriteria_json.get('score')
        self.comments = self.subcriteria_json.get('comments')
        self.where_dict = {
            PgAssignmentSubcriteriasTable.subcriteria_id: self.subcriteria_id,
            PgStudentsTable.student_id: self.student_id
        }
        self.where_filters = [column(key) == value for key, value in self.where_dict.items()]

    def generate_upsert_sql(self):
        if len(self.select_table(where_dict=self.where_dict)) > 0:
            self.sql_statement = self.generate_update_sql()
        else:
            self.sql_statement = self.generate_insert_sql()

    def generate_update_sql(self):
        return (
            self.table.update()
            .where(and_(*self.where_filters))
            .values(
                {
                    PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score: self.score,
                    PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score_comments: self.comments,
                }
            )
        )

    def generate_insert_sql(self):
        return (
            self.table.insert()
            .values(
                {
                    PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score_id: str(uuid.uuid4()), 
                    PgAssignmentSubcriteriasTable.subcriteria_id: self.subcriteria_id, 
                    PgStudentsTable.student_id: self.student_id,
                    PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score: self.score,
                    PgAssignmentSubcriteriaStudentScoresTable.subcriteria_student_score_comments: self.comments,
                }
            )
        )

    def upsert_marking(self):
        #self.create_marking_df()
        self.generate_upsert_sql()
        try:
            print(self.sql_statement)
            self.execute_sql(sql_statement=self.sql_statement)
        except Exception as e:
            print(f"Error when writing to database: {e}")

        #try:
        #    for table in ['assignment_marking_criteria_student_scores_view', 'assignment_marking_subcriteria_student_scores_view', 'assignment_marking_detailed_student_scores_view']
        #    sql_statement = f"REFRESH MATERIALIZED VIEW {table};"
        #    print(sql_statement)
        #    self.execute_sql(sql_statement=sql_statement)
        #except Exception as e:
        #    print(f"Error when refreshing materialized view: {e}")