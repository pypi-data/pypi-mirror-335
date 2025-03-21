from sqlalchemy import create_engine
from pathlib import Path

from utsam.bases.params import SemesterParams, _CACHE_


def create_pg_engine(
    database_type: str,
    username: str,
    password: str,
    host: str,
    port: str,
    database_name: str,
    echo = False
    ):
    # Create a connection string
    connection_string = f'{database_type}://{username}:{password}@{host}:{port}/{database_name}'

    # Create a database engine
    return create_engine(connection_string, pool_size=10, max_overflow=0, echo=echo)

import os
import pandas as pd


def load_data(table_name, engine, load_cache=True, col_name='', filter_value=''):
    Path(_CACHE_).mkdir(parents=True, exist_ok=True)
    file_path = f"{_CACHE_}/{table_name}.csv"
    if load_cache and os.path.isfile(file_path):
        print(f"loading cache from {file_path}")
        return pd.read_csv(file_path)

    filter_condition = ''
    if col_name and filter_value:
        filter_condition = f"WHERE {col_name} = '{filter_value}'"

    df = pd.read_sql(
        f"SELECT * FROM {table_name} {filter_condition};",
        engine
    )
    print(f"writing cache to {file_path}")
    df.to_csv(file_path, index=False)
    return df
