from typing import Any, Dict, Tuple
from tinydb import TinyDB, Query
import os
from .s3_storage import get_database, S3Storage


class MydbS3():
    
    def __init__(self, bucket_name, file_database):
        
        self.db =  TinyDB(
            bucket=bucket_name,
            file=file_database,
            storage=S3Storage
        )
        
    def save(self, data: Dict[Any, Any], table: str = '_default') -> None:
        try:
            database = self.db
            table_insert = database.table(table)
            table_insert.insert(data)
        except Exception as err:
            raise Exception(f"Error: insert in DB {str(err)}") from err
    
    def all(self, table: str = '_default'):
        try:
            database = self.db
            table_reference = database.table(table)
            return table_reference.all()
        except Exception as err:
            raise Exception(f"Error retrieving data from DB: {str(err)}") from err

    

def save(data: Dict[Any, Any], table: str = '_default') -> None:
    try:
        database = get_database()
        table_insert = database.table(table)
        table_insert.insert(data)
    except Exception as err:
        raise Exception(f"Error: insert in DB {str(err)}") from err
    
def insert_tinydb(data: Dict[Any, Any], table: str = '_default') -> None:
    try:
        database = get_database()
        table_insert = database.table(table)
        table_insert.insert(data)
    except Exception as err:
        raise Exception(f"Error: insert in DB {str(err)}") from err

def get_all_data_tinydb(table: str = '_default'):
    try:
        database = get_database()
        table_reference = database.table(table)
        return table_reference.all()
    except Exception as err:
        raise Exception(f"Error retrieving data from DB: {str(err)}") from err

def get_all_data_env(table: str = '_default'):
    try:
        database = get_database()
        table_reference = database.table(table)
        Project = Query()
        result = table_reference.search((Project.environment.exists()) & (Project.environment != ""))
        for item in result:
            item['doc_id'] = table_reference.get(doc_id=item.doc_id).doc_id
        return result
    except Exception as err:
        raise Exception(f"Error retrieving and filtering data from DB: {str(err)}") from err

def get_project_data_tinydb(project_name: str, table: str = '_default'):
    try:
        database = get_database()
        table_reference = database.table(table)
        Project = Query()
        return table_reference.search(Project.project == project_name)
    except Exception as err:
        raise Exception(f"Error retrieving and filtering data from DB: {str(err)}") from err


def convert_time_to_h_m_s(time_execution) -> str:
    hours, remainder = divmod(int(time_execution), 3600)
    minutes, seconds = divmod(remainder, 60)

    return "{:.0f}h {:.0f}min {:.2f}s".format(hours, minutes, seconds)


def register_call_enpoint(endpoint: str,
                          payload: Dict[Any, Any] = None) -> Tuple[Dict[Any, Any], str]:
    if payload is None:
        payload = {}
    return ({
        **payload
    }, "called_endpoint")