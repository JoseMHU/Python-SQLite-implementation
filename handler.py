import sqlite3 as sql
from typing import Any


class Db:
    def __init__(self, db_path: str) -> None:
        self.__db_name = db_path
    
    def __call__(self, func) -> Any:
        def wrapper():
            conn = sql.connect(self.__db_name)
            cursor = conn.cursor()
            try:
                func(cursor=cursor)
                conn.commit()
                conn.close()
            except Exception as e:
                conn.rollback()
                conn.commit()
                conn.close()
                raise e
        return wrapper
    
    def create_table(self, table_name: str, columns: list[tuple]) -> None:
        @self
        def create_table(cursor):
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            columns_str = ", ".join(f"{name} {types}" for name, types in columns)
            query = f"CREATE TABLE {table_name} ({columns_str})"
            cursor.execute(query)
        create_table()

    def insert_rows(self, values: list[tuple], table_name) -> None:
        @self
        def insert_rows(cursor):
            columns_num = ", ".join(f"?" for _ in values[0])
            instruction = f"INSERT INTO {table_name} VALUES ({columns_num})"
            cursor.executemany(instruction, values)
        insert_rows()

    def manual_query(self, query: str) -> None:
        @self
        def manual_query(cursor):
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)
        manual_query()
