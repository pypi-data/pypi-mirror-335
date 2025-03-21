import os
import pickle 
import json
from sqlalchemy import create_engine, MetaData, Table, and_
from sqlalchemy.sql import column
from pathlib import Path
from pydantic import BaseModel

from utsam.bases.params import _METADATA_


class PgDatabase:
    def __init__(
        self,
        user_name: str = None,
        password: str = None,
        host: str = None,
        db_name: str = None,
        port: str = '5432',
        echo = False,
        engine = None,
    ):
        self.database_type = 'postgresql'
        self.user_name = user_name
        self.password = password
        self.host = host
        self.db_name = db_name
        self.port = port
        self.connection_str = f'{self.database_type}://{self.user_name}:{self.password}@{self.host}:{self.port}/{self.db_name}'
        self.engine = engine
        self.create_engine()

    def execute_sql(self, sql_statement):
        try:
            #print(sql_statement)
            with self.engine.connect() as conn:
                if sql_statement.is_select:
                    return conn.execute(sql_statement).fetchall()
                conn.execute(sql_statement)
                conn.commit()
        except Exception as e:
            print(f"Error when writing to database: {e}")

    def create_engine(self):
        if self.engine is None:
            self.engine = create_engine(self.connection_string, pool_size=10, max_overflow=0, echo=False)


class PgTable(PgDatabase):
    def __init__(
        self,
        table_name: str = None,
        user_name: str = None,
        password: str = None,
        host: str = None,
        db_name: str = None,
        port: str = '5432',
        schema: str = "public",
        engine = None
    ):
        super().__init__(
            user_name = user_name,
            password = password,
            host = host,
            db_name = db_name,
            port = port,
            engine = engine,
        )
        self.table_name= table_name
        self.schema = schema
        self.metadata = None
        self.table = None
        self.meta_path = Path.cwd() / _METADATA_
        self.meta_file_name = f'{self.table_name}.metadata'
        self.load_metadata()

    def load_metadata(self):
        if os.path.isfile(self.meta_path / self.meta_file_name):  
            self.reload_metadata()
        else:
            self.metadata = MetaData(schema=self.schema)
            self.metadata.reflect(self.engine, only=[self.table_name])
            self.table = Table(self.table_name, self.metadata, autoload=True, autoload_with=self.engine)
            self.meta_path.mkdir(parents=True, exist_ok=True)

            temp_table = self.table.to_metadata(MetaData())
            with open(self.meta_path / self.meta_file_name, 'wb') as f:
                pickle.dump(temp_table, f)

    def reload_metadata(self):
        with open(self.meta_path / self.meta_file_name, 'rb') as f:
            self.table = pickle.load(f)
    
    def set_select_statement(self, where_dict: dict = None):
        statement = self.table.select()
        if where_dict:
            where_filters = [column(key) == value for key, value in where_dict.items()]
            statement = statement.where(and_(*where_filters))
        return statement

    def select_table(self, where_dict: dict = None):
        sql_statement = self.set_select_statement(where_dict=where_dict)
        return self.execute_sql(sql_statement=sql_statement)

    def set_insert_statement(self, records: list[BaseModel]):
        return (
            self.table.insert()
            .values([record.model_dump() for record in records])
        )

    def insert_records(self, records: list[BaseModel]):
        sql_statement = self.set_insert_statement(records=records)
        self.execute_sql(sql_statement=sql_statement)

    def set_update_statement(self, records: list[BaseModel], where_dict: dict = None):
        statement = self.table.update()
        if where_dict:
            where_filters = [column(key) == value for key, value in where_dict.items()]
            statement = statement.where(and_(*where_filters))
        return (
            statement
            .values([record.model_dump() for record in records])
        )

    def update_records(self, records: list[BaseModel], where_dict: dict = None):
        sql_statement = self.set_update_statement(records=records, where_dict=where_dict)
        self.execute_sql(sql_statement=sql_statement)

    #def set_upsert_statement(self, records: list[BaseModel], where_dict: dict = None):
    #    if len(self.select_table(where_dict=where_dict)) > 0:
    #        self.sql_statement = self.set_update_statement(records=records, where_dict=where_dict)
    #    else:
    #        self.sql_statement = self.set_insert_statement(records=records)
#
    #def upsert_records(self, records: list[BaseModel], where_dict: dict = None):
    #    sql_statement = self.set_upsert_statement(records=records, where_dict=where_dict)
    #    self.execute_sql(sql_statement=sql_statement)

def records_to_json(records):
    return json.loads(json.dumps([dict(row._mapping) for row in records], default=str))

def select_table(table_name, engine, where_dict=None, json=True):

    pg_table = PgTable(
        table_name=table_name,
        engine=engine,
    )

    records = pg_table.select_table(where_dict)
    if json:
        return records_to_json(records)
    return records
    

def insert_records(table_name, records, engine):

    pg_table = PgTable(
        table_name=table_name,
        engine=engine,
    )
    previous_len = len(pg_table.select_table())

    pg_table.insert_records(records=records)
    assert len(pg_table.select_table()) == previous_len + len(records)
    