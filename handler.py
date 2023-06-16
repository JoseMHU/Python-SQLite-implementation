import sqlite3 as sql
from typing import Any


class Db:
    def __init__(self, db_path:str) -> None:
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
    
    def create_table(self, table_name:str, columns:list[tuple]) -> None:
        @self
        def create_table(cursor):
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            columns_str = ", ".join(f"{name} {types}" for name, types in columns)
            query = f"CREATE TABLE {table_name} ({columns_str})"
            cursor.execute(query)
        create_table()

    def insert_rows(self, values:list[tuple], table_name:str) -> None:
        @self
        def insert_rows(cursor):
            columns_num = ", ".join(f"?" for _ in values[0])
            query = f"INSERT INTO {table_name} VALUES ({columns_num})"
            cursor.executemany(query, values)
        insert_rows()

    def delete_rows(self, filter_field:str, filter_value:list[str], table_name:str) -> None:
        @self
        def delete_rows(cursor):
            columns_num = ", ".join(f"?" for _ in filter_value)
            query = f"DELETE FROM {table_name} WHERE {filter_field} IN ({columns_num})"
            cursor.execute(query, filter_value)
        delete_rows()

    def delete_table(self, table_name:str) -> None:
        @self
        def delete_table(cursor):
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        delete_table()

    def update_row(self, field_value:str, new_value, filter_field:str, filter_value, table_name:str) -> None:
        if type(new_value) == str:
                new_value = "'" + new_value + "'"
        if type(filter_value) == str:
            filter_value = "'" + filter_value + "'"
        @self
        def update_row(cursor):
            query = f"UPDATE {table_name} SET {field_value} = {new_value} WHERE {filter_field} = {filter_value}"
            cursor.execute(query)
        update_row()

    def manual_query(self, query:str) -> None:
        @self
        def manual_query(cursor):
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)
        manual_query()
