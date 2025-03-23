import re
import time
from sqlalchemy import create_engine, Column, MetaData, Table, select, func, text
from sqlalchemy import Integer, String, Text, Boolean, Float, DateTime, Date, Time, LargeBinary, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus


def map_sqlite_to_mysql(sqlite_type):
    """Convert SQLite types to MySQL-compatible SQLAlchemy types."""
    sqlite_type = sqlite_type.upper().strip()

    if match := re.match(r"VARCHAR\((\d+)\)", sqlite_type):
        length = int(match.group(1))
        return String(length if length > 0 else 255)

    if match := re.match(r"(DECIMAL|NUMERIC)\((\d+),(\d+)\)", sqlite_type):
        precision, scale = map(int, match.groups()[1:])
        return Float(precision if precision > 0 else 10, scale if scale >= 0 else 2)

    mapping = {
        "INTEGER": BigInteger,
        "TEXT": Text,
        "BOOLEAN": Boolean,
        "REAL": Float,
        "BLOB": LargeBinary,
        "DATETIME": DateTime,
        "DATE": Date,
        "TIME": Time
    }

    return mapping.get(sqlite_type, String(255))



def map_mysql_to_sqlite(mysql_type):
    """Convert MySQL types to SQLite-compatible SQLAlchemy types."""
    mysql_type = mysql_type.upper().strip()

    if match := re.match(r"(VARCHAR|CHAR)\((\d+)\)", mysql_type):
        return Text

    if match := re.match(r"(DECIMAL|NUMERIC)\((\d+),(\d+)\)", mysql_type):
        return Float

    mapping = {
        "INT": Integer,
        "INTEGER": Integer,
        "TINYINT(1)": Boolean,
        "TINYINT": Integer,
        "SMALLINT": Integer,
        "MEDIUMINT": Integer,
        "BIGINT": Integer,
        "TEXT": Text,
        "VARCHAR": Text,
        "CHAR": Text,
        "BOOLEAN": Boolean,
        "FLOAT": Float,
        "DOUBLE": Float,
        "REAL": Float,
        "DECIMAL": Float,
        "NUMERIC": Float,
        "BLOB": LargeBinary,
        "LONGTEXT": Text,
        "MEDIUMTEXT": Text,
        "TINYTEXT": Text,
        "DATETIME": DateTime,
        "DATE": Date,
        "TIME": Time,
        "YEAR": Integer
    }

    return mapping.get(mysql_type, Text)



class Database:
    def __init__(self, username, password, host, port, database):
        encoded_password = quote_plus(password)
        self.engine = create_engine(
            f"mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database}",
            pool_pre_ping=True,
            pool_recycle=1800
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.tables = {
            table_name: Table(table_name, self.metadata, autoload_with=self.engine)
            for table_name in self.metadata.tables
        }

    def define_table(self, name, **columns):
        """Dynamically define a table and ensure it exists in the database.

        The first column provided will be set as the primary key.
        """
        if name in self.tables:
            return self.tables[name]

        columns_def = []
        column_items = list(columns.items())

        if not column_items:
            raise ValueError("At least one column must be provided.")
        first_col_name, first_col_type = column_items[0]
        columns_def.append(Column(first_col_name, first_col_type, primary_key=True, autoincrement=False))
        for col_name, col_type in column_items[1:]:
            columns_def.append(Column(col_name, col_type))

        new_table = Table(name, self.metadata, *columns_def)
        new_table.create(self.engine)
        self.metadata.reflect(bind=self.engine)
        self.tables[name] = new_table
        return new_table

    def insert(self, table, **data):
        """Insert a record into a table"""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        stmt = self.tables[table].insert().values(**data)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def search(self, table, **filters):
        """Search records in a table with optional filters"""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        stmt = select(self.tables[table])
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        with self.engine.connect() as conn:
            results = [dict(row._mapping) for row in conn.execute(stmt).fetchall()]
        return results

    def get(self, table, **filters):
        """Fetch a single record based on filters (like an ID)"""
        results = self.search(table, **filters)
        return results[0] if results else None

    def update(self, table, filters, updates):
        """Update records in a table"""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        stmt = self.tables[table].update()
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        stmt = stmt.values(**updates)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, table, **filters):
        """Delete records from a table"""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        stmt = self.tables[table].delete()
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def list_tables(self):
        """List all tables in the database"""
        return list(self.tables.keys())

    def bulk_insert(self, table, data_list):
        """Insert multiple records into a table efficiently."""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        with self.session.begin():
            self.session.execute(self.tables[table].insert(), data_list)

    def count_rows(self, table, **filters):
        """Count the number of rows in a table with optional filters."""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        stmt = select(func.count()).select_from(self.tables[table])
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        return self.session.execute(stmt).scalar()

    def distinct_values(self, table, column):
        """Fetch distinct values of a column."""
        if table not in self.tables or column not in self.tables[table].c:
            raise ValueError(f"Table '{table}' or column '{column}' does not exist.")
        stmt = select(self.tables[table].c[column]).distinct()
        return [row[0] for row in self.session.execute(stmt).fetchall()]

    def search_paginated(self, table, page=1, page_size=10, **filters):
        """Search records with pagination."""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        stmt = select(self.tables[table])
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        return [dict(row._mapping) for row in self.session.execute(stmt).fetchall()]

    def get_table_schema(self, table):
        """Retrieve table schema (columns and types)."""
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        return {col.name: str(col.type) for col in self.tables[table].columns}

    def ensure_table_exists(self, table):
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        return True

    def delete_table(self, table):
        """Delete a table from the database with a timeout."""
        self.ensure_table_exists(table)

        stmt = text(f"DROP TABLE IF EXISTS {table}")

        try:
            start_time = time.time()
            with self.engine.connect() as conn:
                conn.execution_options(stream_results=True)
                conn.execute(stmt)
                conn.commit()

                if time.time() - start_time > 10:
                    raise TimeoutError(f"Dropping table '{table}' is taking too long.")

            self.metadata.reflect(bind=self.engine)
            self.tables.pop(table, None)
        except Exception as e:
            print(f"Failed to drop table '{table}': {e}")

    def rename_table(self, old_name, new_name):
        """Rename an existing table."""
        self.ensure_table_exists(old_name)
        stmt = text(f"RENAME TABLE {old_name} TO {new_name}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)  # Refresh metadata
        self.tables[new_name] = self.tables.pop(old_name)  # Update internal reference

    def add_column(self, table, column_name, column_type):
        """Add a new column to a table."""
        self.ensure_table_exists(table)
        stmt = text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)  # Refresh metadata

    def drop_column(self, table, column_name):
        """Drop a column from a table."""
        self.ensure_table_exists(table)
        if column_name not in self.tables[table].c:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table}'.")
        stmt = text(f"ALTER TABLE {table} DROP COLUMN {column_name}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)  # Refresh metadata

    def replicate_local_to_online(self, local_db):
        """Replicates data from the local SQLite database to the online MySQL database."""
        for table in local_db.list_tables():
            schema = local_db.get_table_schema(table)
            converted_schema = {col: map_sqlite_to_mysql(schema[col]) for col in schema}

            self.define_table(table, **converted_schema)
            data = local_db.search(table)

            for row in data:
                self.insert(table, **row)

    def list_columns(self, table):
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        return list(self.tables[table].columns.keys())

    def get_column_type(self, table, column_name):
        """Retrieve the data type of a specific column in a table."""
        self.ensure_table_exists(table)
        if column_name not in self.tables[table].c:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table}'.")
        return str(self.tables[table].c[column_name].type)

    def edit_column_type(self, table, column_name, new_type):
        """Modify the data type of an existing column in a MySQL table."""
        self.ensure_table_exists(table)
        if column_name not in self.tables[table].c:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table}'.")

        type_mapping = {
            Integer: "INT",
            String: "VARCHAR",
            Text: "TEXT",
            Boolean: "TINYINT(1)",
            Float: "FLOAT",
            DateTime: "DATETIME",
            Date: "DATE",
            Time: "TIME",
            LargeBinary: "BLOB"
        }

        base_type = type(new_type)

        if base_type not in type_mapping:
            raise ValueError(f"Unsupported type: {new_type}. Add it to the type mapping.")

        mysql_type = type_mapping[base_type]

        if isinstance(new_type, String) and new_type.length:
            mysql_type += f"({new_type.length})"

        stmt = text(f"ALTER TABLE {table} MODIFY COLUMN {column_name} {mysql_type}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)


class LocalDatabase:
    def __init__(self, db_path="local.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.tables = {table_name: Table(table_name, self.metadata, autoload_with=self.engine) for table_name in self.metadata.tables}

    def ensure_table_exists(self, table):
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")

    def define_table(self, name, **columns):
        if name in self.tables:
            return self.tables[name]

        columns_def = []
        column_items = list(columns.items())
        if not column_items:
            raise ValueError("At least one column must be provided.")
        first_col_name, first_col_type = column_items[0]
        columns_def.append(Column(first_col_name, first_col_type, primary_key=True, autoincrement=False))
        for col_name, col_type in column_items[1:]:
            columns_def.append(Column(col_name, col_type))

        new_table = Table(name, self.metadata, *columns_def)
        new_table.create(self.engine)
        self.metadata.reflect(bind=self.engine)
        self.tables[name] = new_table
        return new_table

    def insert(self, table, **data):
        self.ensure_table_exists(table)
        stmt = self.tables[table].insert().values(**data)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def search(self, table, **filters):
        self.ensure_table_exists(table)
        stmt = select(self.tables[table])
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        with self.engine.connect() as conn:
            results = [dict(row._mapping) for row in conn.execute(stmt).fetchall()]
        return results

    def get(self, table, **filters):
        results = self.search(table, **filters)
        return results[0] if results else None

    def update(self, table, filters, updates):
        self.ensure_table_exists(table)
        stmt = self.tables[table].update()
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        stmt = stmt.values(**updates)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, table, **filters):
        self.ensure_table_exists(table)
        stmt = self.tables[table].delete()
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def list_tables(self):
        return list(self.tables.keys())

    def bulk_insert(self, table, data_list):
        self.ensure_table_exists(table)
        with self.session.begin():
            self.session.execute(self.tables[table].insert(), data_list)

    def count_rows(self, table, **filters):
        self.ensure_table_exists(table)
        stmt = select(func.count()).select_from(self.tables[table])
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        return self.session.execute(stmt).scalar()

    def distinct_values(self, table, column):
        self.ensure_table_exists(table)
        if column not in self.tables[table].c:
            raise ValueError(f"Column '{column}' does not exist in table '{table}'.")
        stmt = select(self.tables[table].c[column]).distinct()
        return [row[0] for row in self.session.execute(stmt).fetchall()]

    def search_paginated(self, table, page=1, page_size=10, **filters):
        self.ensure_table_exists(table)
        stmt = select(self.tables[table])
        for key, value in filters.items():
            stmt = stmt.where(self.tables[table].c[key] == value)
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        return [dict(row._mapping) for row in self.session.execute(stmt).fetchall()]

    def get_table_schema(self, table):
        self.ensure_table_exists(table)
        return {col.name: str(col.type) for col in self.tables[table].columns}

    def replicate_to_online(self, online_db):
        for table in self.tables:
            data = self.search(table, json=True)
            for row in data:
                online_db.insert(table, **row)

    def delete_table(self, table):
        self.ensure_table_exists(table)
        stmt = text(f"DROP TABLE IF EXISTS {table}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)
        self.tables.pop(table, None)

    def rename_table(self, old_name, new_name):
        self.ensure_table_exists(old_name)
        stmt = text(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)
        self.tables[new_name] = self.tables.pop(old_name)

    def add_column(self, table, column_name, column_type):
        self.ensure_table_exists(table)
        stmt = text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)

    def drop_column(self, table, column_name):
        self.ensure_table_exists(table)
        if column_name not in self.tables[table].c:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table}'.")
        stmt = text(f"ALTER TABLE {table} DROP COLUMN {column_name}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        self.metadata.reflect(bind=self.engine)

    def replicate_online_to_local(self, online_db):
        """Replicates data from an online MySQL database to the local SQLite database."""
        for table in online_db.list_tables():
            schema = online_db.get_table_schema(table)
            converted_schema = {col: map_mysql_to_sqlite(schema[col]) for col in schema}

            self.define_table(table, **converted_schema)
            data = online_db.search(table)

            for row in data:
                self.insert(table, **row)

    def list_columns(self, table):
        if table not in self.tables:
            raise ValueError(f"Table '{table}' does not exist.")
        return list(self.tables[table].columns.keys())

    def get_column_type(self, table, column_name):
        """Retrieve the data type of a specific column in a table."""
        self.ensure_table_exists(table)
        if column_name not in self.tables[table].c:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table}'.")
        return str(self.tables[table].c[column_name].type)

    def edit_column_type(self, table, column_name, new_type):
        """Modify the data type of an existing column in an SQLite table by recreating the table."""
        self.ensure_table_exists(table)
        if column_name not in self.tables[table].c:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table}'.")

        type_mapping = {
            Integer: "INTEGER",
            String: "TEXT",
            Text: "TEXT",
            Boolean: "INTEGER",
            Float: "REAL",
            DateTime: "TEXT",
            Date: "TEXT",
            Time: "TEXT",
            LargeBinary: "BLOB"
        }

        base_type = type(new_type)

        if base_type not in type_mapping:
            raise ValueError(f"Unsupported type: {new_type}. Add it to the type mapping.")

        sqlite_type = type_mapping[base_type]
        if isinstance(new_type, String) and new_type.length:
            sqlite_type = "TEXT"
        schema = self.get_table_schema(table)
        schema[column_name] = sqlite_type

        temp_table = f"{table}_temp"

        new_table = self.define_table(temp_table, **{col: schema[col] for col in schema})
        columns = ", ".join(schema.keys())
        stmt = text(f"INSERT INTO {temp_table} ({columns}) SELECT {columns} FROM {table}")
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

        self.delete_table(table)
        self.rename_table(temp_table, table)





