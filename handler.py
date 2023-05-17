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


if __name__ == "__main__":
    # test
    
    test_db = Db("./test.db")
    test_db.create_table(table_name="fabricante", columns=[("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                                                           ("nombre", "TEXT")])
    
    test_db.create_table(table_name="producto", columns=[("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                                                         ("nombre", "TEXT"),
                                                         ("precio", "REAL"),
                                                         ("id_fabricante", "INTEGER NOT NULL"),
                                                         ("FOREIGN KEY (id_fabricante) REFERENCES fabricante(id)", "")])
    
    test_db.insert_rows(values=[(1, "Asus"),
                                (2, "Lenovo"),
                                (3, "Hewlett-Packard"),
                                (4, 'Samsung'),
                                (5, 'Seagate'),
                                (6, 'Crucial'),
                                (7, 'Gigabyte'),
                                (8, 'Huawei'),
                                (9, 'Xiaomi')],
                        table_name="fabricante")
    
    test_db.insert_rows(values=[(1, 'Disco duro SATA3 1TB', 86.99, 5),
                                (2, 'Memoria RAM DDR4 8GB', 120, 6),
                                (3, 'Disco SSD 1 TB', 150.99, 4),
                                (4, 'GeForce GTX 1050Ti', 185, 7),
                                (5, 'GeForce GTX 1080 Xtreme', 755, 6),
                                (6, 'Monitor 24 LED Full HD', 202, 1),
                                (7, 'Monitor 27 LED Full HD', 245.99, 1),
                                (8, 'Portátil Yoga 520', 559, 2),
                                (9, 'Portátil Ideapd 320', 444, 2),
                                (10, 'Impresora HP Deskjet 3720', 59.99, 3),
                                (11, 'Impresora HP Laserjet Pro M26nw', 180, 3)],
                        table_name="producto")
    
    test_db.manual_query(query="""
    SELECT p.nombre, p.precio, f.nombre
    FROM producto AS p
    INNER JOIN fabricante AS f ON f.id = p.id_fabricante
    """)
