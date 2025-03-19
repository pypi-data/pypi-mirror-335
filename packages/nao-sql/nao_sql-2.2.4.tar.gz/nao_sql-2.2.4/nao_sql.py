from pyodbc import Connection, connect
import datetime
import decimal
from nao_logger import get_nao_logger
from enum import Enum
import json

LOGGER = get_nao_logger('nao_sql')

data_type_map = {
    int: 'INTEGER',               # INTEGER in SQL for Python int
    float: 'REAL',                # REAL in SQL for Python float
    str: 'NVARCHAR(255)',         # TEXT in SQL for Python str. VARCHAR or NVARCHAR can be used in other SQL databases
    bool: 'BOOLEAN',              # BOOLEAN in SQL for Python bool (SQLite stores this as INTEGER 0 or 1)
    bytes: 'BLOB',                # BLOB in SQL for Python bytes
    datetime.date: 'DATE',        # DATE in SQL for Python datetime.date
    datetime.datetime: 'DATETIME',# DATETIME in SQL for Python datetime.datetime
    datetime.time: 'TIME',        # TIME in SQL for Python datetime.time
    decimal.Decimal: 'NUMERIC',   # NUMERIC in SQL for Python decimal.Decimal (useful for precise fixed-point arithmetic)
    list: 'TEXT',                 # Serialized list (e.g., JSON) stored as TEXT in SQL
    dict: 'TEXT',                 # Serialized dictionary (e.g., JSON) stored as TEXT in SQL
    None: 'NULL',                 # NULL in SQL for Python None
}

class ReturnMode(Enum):
    JSON=1
    ROW=2
    COLUMN=3
    VALUE=4
    DICT=5

class Database:

    def __init__(self, server:str = None, database:str = None, **kwargs):
        """Initializes a new Database object with connection details.

        This class sets up the configuration for a database connection. It allows for different
        authentication methods and can be customized further with additional keyword arguments.

        Args:
            username (str, optional): The username for database login. It's required if the login method is not 'windows_auth'.
            password (str, optional): The password for database login. It's required if the login method is not 'windows_auth'.
            server (str, optional): The server address of the database.
            database (str, optional): The name of the specific database to connect to.
            **kwargs: Additional keyword arguments for more customization.
        """
        self.username:str = kwargs.get('username')
        self.password:str = kwargs.get('password')
        self.server:str = server
        self.database:str = database

    def __str__(self) -> str:
        return self.server + '-' + self.database
    
    def login(self):
        if self.username and self.password:
            connection:Connection = self.login_sql_server_authentication(self.server, self.database, self.username, self.password)
            return connection

        else:
            connection:Connection = self.login_windows_authentication(self.server, self.database)
            return connection

    def login_windows_authentication(self, server: str,database: str) -> Connection:
        """
        Establishes a connection to a SQL Server database using provided credentials.

        :param server: The address of the SQL Server database (IP or hostname).
        :param database: The name of the database to connect to.

        :return: A pyodbc Connection object if the connection is successful, None otherwise.

        """
        connection = ('DRIVER={SQL Server};'
                f'Trusted_Connection=Yes;'
                f'SERVER={server};'
                f'DATABASE={database};')
        try:
            connection = connect(connection, timeout = 120)
            LOGGER.success('Connection Established')
            return connection
        except Exception as e:
            LOGGER.error(f'{e}')
            return None

    def login_sql_server_authentication(self, server: str, database: str, username: str, password: str) -> Connection:
        """
        Establishes a connection to a SQL Server database using provided credentials.

        :param server: The address of the SQL Server database (IP or hostname).
        :param database: The name of the database to connect to.
        :param username: The username for database authentication.
        :param password: The password for database authentication.

        :return: A pyodbc Connection object if the connection is successful, None otherwise.

        """
        connection = ('DRIVER={SQL Server};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}')
        try:
            connection = connect(connection, timeout = 120)
            LOGGER.success('Connection Established')
            return connection
        except Exception as e:
            LOGGER.critical(f'{e}')
            return None

    def select(self, table:str, distinct:bool=False, columns:list=['*'], where:str=None, order_by:str=None, return_mode=ReturnMode.DICT):
        """
        Returns a list of dictionaries that represent the rows and their columns.

        :param table[str]: Name of the table.
        :param distinct[bool]: Return distinct results
        :param columns[list]: List of columns to return
        :param where[str]: Where clause
        :param where[order by]: Columns to order by

        :return: A list[dict] that represents the queried data
        """

        # Handle * selection
        columns = '*' if columns == ['*'] else ', '.join(f'[{column}]' for column in columns)
        order_by = ', '.join(f'[{column}]' for column in order_by) if order_by else None
        
        # Build query
        query = 'SELECT '
        if distinct:
            query += 'DISTINCT '
        query += f'{columns} FROM {table}'
        if where:
            query += f' WHERE {where}'
        if order_by:
            query += f' ORDER BY {order_by}'

        # Execute query
        return self.query(query, return_mode)

    def insert(self, table:str, data:dict):
        with self.login() as connection:
            with connection.cursor() as cursor:
                # Get the columns of the data
                columns = cursor.columns(table=table)
                columns = [column.column_name for column in columns]

                # Filter the data to be inserted
                filtered_data = {}
                for key, value in data.items():
                    if key in columns:
                        filtered_data[key] = value

                # If no valid columns remain after filtering, abort the operation.
                if not filtered_data:
                    LOGGER.warning("No matching columns found in the table for the provided data.")
                    return False

                # Prepare the column names and corresponding values.
                columns = list(filtered_data.keys())
                values = list(filtered_data.values())

                try:
                    # Create placeholders for the values.
                    placeholders = ', '.join(['?' for _ in columns])
                    query = f'INSERT INTO {table} ({", ".join(columns)}) VALUES ({placeholders})'
                    cursor.execute(query, values)
                    LOGGER.success(f'{query}')
                    return filtered_data
                
                except Exception as e:
                    LOGGER.failure(f'{query}')
                    LOGGER.debug(e, exc_info=True)
                    return False

    def delete(self, table:str, pk:dict):

        # Can add checking for primary key validation
        
        if type(pk) != dict:
            raise TypeError('Primary Key must be a dictionary')
        
        with self.login() as connection:
            with connection.cursor() as cursor:

                try:
                    pk_clauses = [f"{key}='{value}'" for key, value in pk.items()]
                    where = ' AND '.join(pk_clauses)
                    query = f'DELETE FROM {table} WHERE {where}'
                    cursor.execute(query)
                    LOGGER.success(f'{query}')
                    return True
            
                except Exception as e:
                    LOGGER.failure(f'{query}')
                    LOGGER.debug(e, exc_info=True)
                    return False

    def update(self, table:str, pk:dict, values:dict):

        # Can add checking for primary key validation

        if type(pk) != dict:
            raise TypeError('Primary Key must be a dictionary')
        
        if type(values) != dict:
            raise TypeError('Values must be a dictionary')
        
        with self.login() as connection:
            with connection.cursor() as cursor:
                try:
                    pk_clauses = [f"{key}='{pk_value}'" for key, pk_value in pk.items()]
                    where = ' AND '.join(pk_clauses)

                    set_values = [f"{key}='{value}'" for key, value in values.items()]
                    set = ', '.join(set_values)

                    query = f'UPDATE {table} SET {set} WHERE {where}'
                    cursor.execute(query)
                    LOGGER.success(f'{query}')
                    return True
            
                except Exception as e:
                    LOGGER.failure(f'{query}')
                    LOGGER.debug(e, exc_info=True)
                    return False        

    def query(self, query:str, return_mode=ReturnMode.DICT, is_single_record=False):
        with self.login() as connection:
            with connection.cursor() as cursor:

                try:
                    cursor.execute(query)
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()

                    # Check no values
                    if len(rows) == 0:
                        return []

                    # Check Single Value
                    if len(rows[0]) > 1 and return_mode == ReturnMode.VALUE:
                        raise IndexError('ReturnMode.VALUE selected, but more than 1 row present')
                    
                    # # Check Row Value
                    # for row in rows:
                    #     if len(row) > 1 and return_mode == ReturnMode.COLUMN:
                    #         raise IndexError('ReturnMode.COLUMN selected, but more than 1 column present')
                        
                    # Check Return Mode
                    match return_mode:
                        case ReturnMode.VALUE:
                            LOGGER.success(f'{query}')
                            return rows[0][0]
                        
                        case ReturnMode.ROW:
                            LOGGER.success(f'{query}')
                            data = rows[0] if is_single_record else rows
                            return data
                        
                        case ReturnMode.JSON:
                            LOGGER.success(f'{query}')
                            json_dict = [dict(zip(columns, row)) for row in rows]
                            data = json_dict[0] if is_single_record else json_dict
                            return json.dumps(data, default=str)

                        case ReturnMode.COLUMN:
                            LOGGER.success(f'{query}')
                            column = [row[0] for row in rows]
                            data = column[0] if is_single_record else column
                            return data
                        
                        case ReturnMode.DICT:
                            LOGGER.success(f'{query}')
                            dict_dict = [dict(zip(columns, row)) for row in rows]
                            data = dict_dict[0] if is_single_record else dict_dict
                            return data

                        case _:
                            raise TypeError('Invalid Return Mode Selected')
                        
                except Exception as e:
                    LOGGER.failure(f'{query}')
                    LOGGER.debug(e, exc_info=True)
                    return False

    def get_definition(self, table:str) -> dict:
        with self.login() as connection:
            with connection.cursor() as cursor:
                columns = cursor.columns(table=table)
                column_info:dict = {}
                for column in columns:
                    column_info[column.column_name] = {
                        'TABLE_CAT': column.table_cat,
                        'TABLE_SCHEM': column.table_schem,
                        'TABLE_NAME': column.table_name,
                        'COLUMN_NAME': column.column_name,
                        'DATA_TYPE': column.data_type,
                        'TYPE_NAME': column.type_name,
                        'COLUMN_SIZE': column.column_size,
                        'BUFFER_LENGTH': column.buffer_length,
                        'DECIMAL_DIGITS': column.decimal_digits,
                        'NUM_PREC_RADIX': column.num_prec_radix,
                        'NULLABLE': column.nullable,
                        'REMARKS': column.remarks,
                        'COLUMN_DEF': column.column_def,
                        'SQL_DATA_TYPE': column.sql_data_type,
                        'SQL_DATETIME_SUB': column.sql_datetime_sub,
                        'CHAR_OCTET_LENGTH': column.char_octet_length,
                        'ORDINAL_POSITION': column.ordinal_position,
                        'IS_NULLABLE': column.is_nullable,
                    }
                    LOGGER.success(f'{column_info}')
                return column_info

    def get_columns(self, table:str) -> list:
        with self.login() as connection:
            with connection.cursor() as cursor:
                try:
                    results = cursor.columns(table=table)
                    columns = [column.column_name for column in results]
                    LOGGER.success(f'{columns}')
                    return columns

                except Exception as e:
                    LOGGER.failure(e, exec_info=True)

    def get_primary_keys(self, table:str) -> list:
        with self.login() as connection:
            with connection.cursor() as cursor:
                try:
                    results = cursor.primaryKeys(table)
                    return results.fetchall()
            
                except Exception as e:
                    LOGGER.failure(e, exec_info=True)

    def get_foreign_keys(self, table:str) -> list:
        with self.login() as connection:
            with connection.cursor() as cursor:
                try:
                    results = cursor.foreignKeys(table)
                    return results.fetchall()
            
                except Exception as e:
                    LOGGER.failure(e, exec_info=True)

    def get_map(self, table:str, key_column:str, value_column:str) -> dict:
        data = self.select(table=table, columns=[key_column, value_column])
        return {row[key_column]: row[value_column] for row in data}

    def get_next_index(self, table:str, column:str):
        with self.login() as connection:
            with connection.cursor() as cursor:

                if self.get_definition(table)[column]['TYPE_NAME']  != 'int':
                    raise TypeError('Column is not an Integer')
                
                query = f"SELECT ISNULL(MAX({column}), 0)+1 FROM {table}"
                cursor.execute(query)
                return self.query(query=query, return_mode=ReturnMode.VALUE)

if __name__ == "__main__":
    db = Database(server='127.0.0.1', database='nao_budget')
