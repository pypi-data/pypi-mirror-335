import re
import io
import os
import time
import string
import getpass
import logging
import platform
import psycopg2
import subprocess
import pandas as pd
from datetime import datetime
from botpgsql.exceptions import (
    ValuesNotInitiated,
    WrongBotDatabase
)


class PostgresqlConnection:

    def __init__(self, database, prefix_env='PG', **kwargs):
        """
        Initialize a PostgreSQL database connection.

        :param database: The name of the database.
        :type database: str
        """
        self.prefix_env = prefix_env
        self.database = database
        self.conn = None
        self.cursor = None
        self.credentials = dict.fromkeys(
            'HOST DBNAME USER PASSWORD PORT'.split()
        )
        self._load_credentials()
        self.time_out_operations = kwargs.get('time_out_operations', 3)

    def _create_file_txt(
                self,
                text: str,
                name_file: str,
                path_to_save: str,
                subs: bool = False
            ):
        os.makedirs(path_to_save, exist_ok=True)
        full_path_file = os.path.abspath(f'{path_to_save}/{name_file}.txt')

        if not os.path.exists(full_path_file) or subs:
            with open(full_path_file, 'w') as f:
                f.write(text)
        else:
            with open(full_path_file, 'r') as f:
                text = f.read()
        return text

    def _load_credentials(self):
        self.credentials = {
            key: os.getenv(f"{self.prefix_env}_{key}_{self.database.upper()}")
            for key in self.credentials
        }
        if params := [key for key in self.credentials
                      if not self.credentials[key]]:
            self.ask_credentials_cli(params)

    def ask_credentials_cli(self, list_params: list) -> None:
        for param in list_params:
            if param.lower() in ("senha", "password"):
                value = getpass.getpass(
                    f"Informe a Senha para" f" ({self.prefix_env}_{self.database.upper()}): "
                )
            else:
                value = input(f"Informe o(a) {param} "
                              f"para ({self.prefix_env}_{self.database.upper()}): ")
            self.set_persistent_env_var(
                f"{self.prefix_env}_{param}_{self.database.upper()}".upper(),
                value
            )
            self.credentials[param] = value

    def set_persistent_env_var(self, var_name: str, var_value: str) -> None:
        system = platform.system()

        if system == "Windows":
            subprocess.run(["setx", var_name, var_value], check=True)
        elif system == "Linux":
            home = os.path.expanduser("~")
            bashrc_path = os.path.abspath(os.path.join(home, ".bashrc"))
            with open(bashrc_path, "a") as bashrc:
                bashrc.write(f'\nexport {var_name}="{var_value}"\n')
            logging.info(
                f"Variable added to {bashrc_path}. "
                "Please re-login or source the file."
            )
        else:
            raise NotImplementedError(
                f"Setting environment variables persistently"
                f" is not implemented for {system}"
            )

    def connect(self, encoding: str = ''):
        """
        Connect to the PostgreSQL database using the loaded credentials.
        :param encoding: The encoding to setup on the connection.
        :type encoding: str
        """
        self.conn = psycopg2.connect(
            host=self.credentials['HOST'],
            database=self.credentials['DBNAME'],
            user=self.credentials['USER'],
            password=self.credentials['PASSWORD'],
            port=self.credentials['PORT'],

        )
        if encoding != '':
            self.conn.set_client_encoding(encoding)

        self.cursor = self.conn.cursor()
        self.cursor.execute('BEGIN TRANSACTION')

    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.cursor.execute('END TRANSACTION')
            self.cursor.close()
            self.conn.close()

    class ConnectionFail(Exception):
        pass

    def test_conection(self):
        self.connect()
        self.close()

    def handle_connection(self, func, *args, **kwargs):
        """
        Handle the PostgreSQL database connection and execute a function.

        This method establishes a connection to the PostgreSQL database,
        executes the specified function,
        commits the changes, and handles any errors that occur during the
        connection.

        :param func: The function to execute.
        :type func: function
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :param time_out: The timeout duration for establishing the connection,
        defaults to 20 seconds.
        :type time_out: int, optional
        :param raise_exception: Whether to raise an exception on connection
        failure, defaults to True.
        :type raise_exception: bool, optional
        :return: The result of the executed function.
        :rtype: any
        :raises ConnectionFail: If the connection fails and raise_exception is
        True.
        """
        time_out = self.time_out_operations if 'time_out' not in kwargs else kwargs.pop('time_out')
        raise_exception = True if 'raise_exception' not in kwargs else kwargs.pop('raise_exception')
        contador_time_out = 0
        ret = False
        error = None
        while contador_time_out < time_out:
            try:
                encoding = kwargs.pop('encoding') if 'encoding' in kwargs else ''
                self.connect(encoding)
                ret = func(*args, **kwargs)
                self.conn.commit()
                break
            except (Exception, psycopg2.Error) as e:
                logging.exception(e)
                error = e
                self.cursor.execute("ROLLBACK;")
                time.sleep(1)
            finally:
                self.close()
            contador_time_out += 1
        if error and raise_exception:
            raise error
        return ret


class Postgresql(PostgresqlConnection):

    def __init__(self, database: str, **kwargs):
        """
        Initialize a PostgreSQL connection.

        :param database: The name of the database.
        :type database: str
        """
        super().__init__(database, **kwargs)

        self.time_out_conection = None

    def _show_properties_database(self):
        """
        Print the properties of the PostgreSQL database connection.
        """
        logging.info(self.conn.get_dsn_parameters())

        # Print PostgreSQL version
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        logging.info(f"You are connected to - {record}\n")

    def show_properties_database(self):
        """
        Show the properties of the PostgreSQL database connection.
        """
        self.handle_connection(self._show_properties_database)

    def set_time_out_postgres_options(self, time_out_conection):
        """
        Set the timeout option for the PostgreSQL connection.

        :param time_out_conection: The timeout duration in seconds.
        :type time_out_conection: int
        """
        self.time_out_conection = time_out_conection
        os.environ['PGOPTIONS'] = f'-c statement_timeout={self.time_out_conection}s'

    def _create_table(self, table_name, columns):
        """
        Create a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :param columns: The columns to create in the table.
        :type columns: str
        """
        sql_comand = f"""CREATE TABLE IF NOT EXISTS {table_name} ({columns});"""
        self.cursor.execute(sql_comand)

    def create_table(self, table_name, columns):
        """
        Create a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :param columns: The columns to create in the table.
        :type columns: str
        """
        self.handle_connection(self._create_table, table_name, columns)

    def _create_column(self, table_name, column, type_column):
        """
        Add a column to an existing table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :param column: The name of the column to create.
        :type column: str
        :param type_column: The data type of the column.
        :type type_column: str
        """
        sql_create_column = f'ALTER TABLE {table_name} ADD IF NOT EXISTS {column} {type_column};'
        self.cursor.execute(sql_create_column)

    def create_column(self, table_name, column, type_column):
        """
        Add a column to an existing table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :param column: The name of the column to create.
        :type column: str
        :param type_column: The data type of the column.
        :type type_column: str
        """
        self.handle_connection(self._create_column, table_name, column, type_column)

    def clear_table_columns_to_db(self, colunas):
        """
        Clear the table columns for the PostgreSQL database.

        :param colunas: The column names to clear.
        :type colunas: list
        :return: The cleared column names.
        :rtype: list
        """
        colunas = [re.sub(r'\W+', '_', coluna) for coluna in
                   colunas]
        return colunas

    def _define_column_object_type(self, table, column):
        """
        Define the object type of a column in the PostgreSQL database.

        :param table: The table containing the column.
        :type table: pandas.DataFrame
        :param column: The name of the column.
        :type column: str
        :return: The PostgreSQL data type for the column.
        :rtype: str
        """
        # get the maximum length of the col column
        max_len = table[column].astype('str').str.len().max()

        # get the minimun length of the col column
        min_len = table[column].astype('str').str.len().min()

        # if len values is the same define varchar type
        if max_len == min_len:
            postgres_type = 'TEXT'  # f'VARCHAR({max_len})'
        else:
            # else text type
            postgres_type = 'TEXT'
        return postgres_type

    def generate_columns_types(
            self,
            table,
            dtypes_columns=None,
            match_partial: bool = False,
            id_column: bool = True
            ):
        """
        Generate the column types for a PostgreSQL table based on a Pandas
        DataFrame.


        :param table: The DataFrame containing the table data.
        :type table: pandas.DataFrame
        :param dtypes_columns: Optional dictionary specifying custom column
        types for specific columns.
        :type dtypes_columns: dict, optional
        :param match_partial: A flag to enable search partial name columns to
        match dtypes_columns keys.
        :type match_partial: bool, optional
        :param id_column: A flag to create the column id.
        :type id_column: bool, optional
        :return: The PostgreSQL column definitions.
        :rtype: str
        """
        if dtypes_columns is None:
            dtypes_columns = {}

        # Define a mapping of Pandas data types to PostgreSQL data types
        type_map = {'int64': 'NUMERIC', 'float64': 'NUMERIC', 'object': 'TEXT', 'datetime64[ns]': 'TIMESTAMP'}

        # Loop through each column in the DataFrame and generate a PostgreSQL column definition
        postgres_columns = ['id serial PRIMARY KEY'] if id_column else []
        only_columns_df = list(table.columns)
        only_columns_df = ', '.join([f'"{col}"' for col in only_columns_df])
        for column in table.columns:
            dtype = str(table[column].dtype)

            if len(dtypes_columns) > 0:
                matched_column = [key for key in dtypes_columns.keys() if key.lower() in column.lower()]
                if (match_partial and len(matched_column) > 0) \
                        or column in dtypes_columns.keys():
                    postgres_columns.append(f'"{column}" {dtypes_columns[matched_column[0]]}')
                    continue

            # Verificando tipo objeto
            if dtype == 'object':
                postgres_type = self._define_column_object_type(table, column)
            else:
                postgres_type = type_map.get(dtype, 'TEXT')

            postgres_columns.append(f'"{column}" {postgres_type}')

        # Join the list of column definitions into a single string with commas between them
        postgres_columns_str = ', '.join(postgres_columns)
        logging.info(postgres_columns_str)

        return postgres_columns_str, only_columns_df

    def _insert_table_db(self, table, table_name, columns_postgre):
        """
        Insert a table into a PostgreSQL database.

        :param table: The DataFrame containing the table data.
        :type table: pandas.DataFrame
        :param table_name: The name of the table in the database.
        :type table_name: str
        :param columns_postgre: The column names in the PostgreSQL table.
        :type columns_postgre: str
        """
        # define a list of '%s' in the range columns
        lista_var_linha = ['%s' for _ in table.columns]

        # turn the list into a string
        var_linha = ' ,'.join(lista_var_linha)

        # # generate a list o list query values from the table to be inserted on database
        # table_list = list(
        #     map(lambda lista: tuple(list(
        #         map(lambda vl: str(vl).replace("'", "''") if (str(vl) != 'NULL') else None, lista))),
        #         table.values.tolist()))

        # 🔥 Otimização com `.applymap()`
        df_clean = table.map(lambda vl: None if vl == 'NULL' else str(vl).replace("'", "''"))

        # Converter para lista de tuplas rapidamente
        table_list = list(df_clean.itertuples(index=False, name=None))

        # SQL comand to insert many
        sql_insert = f"INSERT INTO {table_name}({columns_postgre}) VALUES ({var_linha});"
        logging.info(sql_insert)
        self.cursor.executemany(sql_insert, table_list)

    def insert_table_db(self, table, table_name, columns_postgre):
        """
        Insert a table into a PostgreSQL database.

        :param table: The DataFrame containing the table data.
        :type table: pandas.DataFrame
        :param table_name: The name of the table in the database.
        :type table_name: str
        :param columns_postgre: The column names in the PostgreSQL table.
        :type columns_postgre: str
        """
        self.handle_connection(self._insert_table_db, table, table_name, columns_postgre)

    def _insert_by_copy(self, buffer, table_name, columns_postgre, *args, **kwargs):
        sep = kwargs.get('sep', ';')
        columns = columns_postgre.replace('"', '').split(', ')
        self.cursor.copy_from(buffer, table_name, columns=columns, sep=sep, null='NULL')

    def insert_by_copy(self, buffer, table_name, columns_postgre, *args, **kwargs):
        self.handle_connection(self._insert_by_copy, buffer, table_name, columns_postgre, *args, **kwargs)

    def to_buffer_io(self, df: pd.DataFrame, **kwargs):
        # Criar um buffer de memória
        buffer = io.StringIO()

        # Adequando valores NULL para None
        df = df.replace('NULL', None)
        # Escrever o DataFrame no buffer como um CSV (separado por tabulação "\t" para COPY)
        sep = kwargs.get('sep',';')
        df.to_csv(buffer, index=False, header=False, sep=sep, na_rep='NULL')

        # Retornar o ponteiro do buffer para o início (necessário antes de usar no PostgreSQL)
        buffer.seek(0)
        return buffer

    def to_postgresql(
            self,
            table,
            table_name: str = '',
            call_procedure: str = '',
            dtypes_columns=None,
            match_partial: bool = False,
            id_column: bool = True,
            by_copy: bool = True,
            *args,
            **kwargs
            ):
        """
        Export a table to a PostgreSQL database.

        :param table: The DataFrame containing the table data.
        :type table: pandas.DataFrame
        :param table_name: The name of the table in the database. If not provided, the table name will be generated automatically.
        :type table_name: str
        :param call_procedure: The name of the stored procedure to call after inserting the table data (optional).
        :type call_procedure: str
        :param dtypes_columns: A dictionary specifying the desired data types for specific columns (optional).
        :type dtypes_columns: dict
        :param id_column: A flag to create the column id.
        :type id_column: bool, optional
        :return: True if the export was successful, False otherwise.
        :rtype: bool
        """
        #self.to_sharing_folder_db(table,table_name)
        table = self.fit_columns_db_on_table(table_name, table)
        postgres_columns, columns = self.generate_columns_types(
            table,
            dtypes_columns,
            match_partial,
            id_column
        )
        self.create_table(table_name, postgres_columns)
        # postgres_columns = self.select_columns(table_name, id_column)
        if by_copy:
            logging.info('...Inserting by COPY FROM BUFFER...')
            self.insert_by_copy(self.to_buffer_io(table, **kwargs), table_name, columns, *args, **kwargs)
        else:
            self.insert_table_db(table, table_name, columns)

        if call_procedure is not None and len(call_procedure) > 0:
            self.call_procedure(call_procedure)
        return True

    @staticmethod
    def get_dummy():
        # Get the current time in seconds since the epoch
        timestamp = time.time()

        # Convert the timestamp to milliseconds
        dummy = int(timestamp * 1000)

        logging.info(dummy)
        return dummy

    def to_sharing_folder_db(
            self,
            table,
            db_table_name,
            path_sharing_folder=None,
            file_name=None
            ):
        path_sharing_folder = path_sharing_folder if path_sharing_folder is not None else os.getenv('PATH_LINUX_DB')
        file_name = file_name if file_name is not None else f'{db_table_name}_{self.get_dummy()}.csv'
        folder_path = fr'{path_sharing_folder}/{db_table_name}'
        os.makedirs(folder_path, exist_ok=True)
        full_path = fr'{folder_path}/{file_name}'
        #pd.DataFrame().to_csv()
        table.to_csv(full_path, sep=';', index=False)

    def _call_procedure(self, procedure_name):
        """
        Call a stored procedure in the PostgreSQL database.

        :param procedure_name: The name of the stored procedure.
        :type procedure_name: str
        """
        sql_call_procedure = f'CALL {procedure_name}()'
        self.cursor.execute(sql_call_procedure)

    def call_procedure(self, procedure_name):
        """
        Call a stored procedure in the PostgreSQL database.

        :param procedure_name: The name of the stored procedure.
        :type procedure_name: str
        """
        self.handle_connection(self._call_procedure, procedure_name)

    def _select_columns(self, table_name, ignore_id: bool = True):
        """
        Retrieve the column names of a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :return: The column names of the table.
        :rtype: str
        """
        sql_select_column = f"""
            select "column_name"
            from INFORMATION_SCHEMA.COLUMNS
            where TABLE_NAME='{table_name}'
            ORDER BY ordinal_position
        """
        self.cursor.execute(sql_select_column)
        tabela_columns = self.cursor.fetchall()

        colnames = [f'"{desc[0]}"' for desc in tabela_columns]

        if ignore_id:
            colnames = colnames[1:]

        colunas_postgre = ' ,'.join(colnames)

        return colunas_postgre

    def select_columns(self, table_name, ignore_id: bool = True):
        """
        Retrieve the column names of a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :param ignore_id: If you want ignore the id column.
        :type ignore_id: bool
        :return: The column names of the table.
        :rtype: str
        """
        colunas_postgre = self.handle_connection(self._select_columns, table_name, ignore_id)
        return colunas_postgre

    def _get_list_columns(self, table_name):
        """
        Retrieve the column names of a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :return: The column names of the table.
        :rtype: list
        """
        sql_select_column = f"""
            select "column_name"
            from INFORMATION_SCHEMA.COLUMNS
            where TABLE_NAME='{table_name}'
            ORDER BY ordinal_position
        """
        self.cursor.execute(sql_select_column)
        tabela_columns = self.cursor.fetchall()

        colnames = [desc[0] for desc in tabela_columns]

        return colnames

    def get_list_columns(self, table_name):
        """
        Retrieve the column names of a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :return: The column names of the table.
        :rtype: list
        """
        colunas_postgre = self.handle_connection(self._get_list_columns, table_name)
        return colunas_postgre

    def _select_columns_types(self, table_name):
        """
        Retrieve the column names of a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :return: The column names of the table.
        :rtype: str
        """
        sql_select_column = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            where TABLE_NAME='{table_name}'
            ORDER BY ordinal_position
        """
        self.cursor.execute(sql_select_column)
        tabela_columns_type = self.cursor.fetchall()
        return dict(tabela_columns_type)

    def select_columns_types(self, table_name):
        """
        Retrieve the column names of a table in the PostgreSQL database.

        :param table_name: The name of the table.
        :type table_name: str
        :param ignore_id: If you want ignore the id column.
        :type ignore_id: bool
        :return: The column names as key and type as value.
        :rtype: dict
        """
        columns_type = self.handle_connection(self._select_columns_types, table_name)
        return columns_type

    def fit_columns_db_on_table(self, table_db_name, df):
        try:
            logging.info('Adequando colunas do relatorio de acordo com colunas no banco de dados')
            columns_pg = self.select_columns_types(table_db_name)
            logging.info(columns_pg)
            if columns_pg:
                for col in columns_pg.keys():
                    if col not in df.columns:
                        if columns_pg[col] in ('integer', 'numeric'):
                            df[col] = 0
                        elif 'timestamp' in columns_pg[col]:
                            df[col] = 'NULL'
                        elif columns_pg[col] in ('text', 'character varying'):
                            df[col] = ''
                _ = columns_pg.pop('id') if 'id' in columns_pg.keys() else None
                df = df[columns_pg.keys()]
        except Exception as e:
            logging.exception(e)
        return df

    def _execute_script(self, script, *args, **kwargs):
        """
        Execute a SQL script in the PostgreSQL database.

        :param script: The SQL script to execute.
        :type script: str
        :return: The result of the script execution.
        :rtype: list
        """
        #logging.info(script, *args)
        self.cursor.execute(script, *args)
        if 'select' in script.lower():
            return self.cursor.fetchall()

    def execute_script(self, script, *args, **kwargs):
        """
        Execute a SQL script in the PostgreSQL database.

        :param script: The SQL script to execute.
        :type script: str
        :return: The result of the script execution.
        :rtype: list
        """
        return self.handle_connection(self._execute_script, script, *args, **kwargs)

    def _create_procedure_to_delete_duplicateds(self, name_table, columns):
        """
        Create a procedure to delete duplicateds values from name table reference.

        :param name_table: The name of the table in database.
        :type name_table: str
        :return: The name of the created procedure.
        :rtype: str
        """
        sql = f"""
        CREATE PROCEDURE public.proc_deletar_duplicada_{name_table}(
            )
        LANGUAGE 'sql'
        AS $BODY$
        DELETE FROM
            {name_table}
        WHERE
            id IN (
                SELECT
                    id
                FROM
                    (
                        SELECT
                            id,
                            ROW_NUMBER() OVER(
                                PARTITION BY
                                {columns}
                                ORDER BY
                                    id DESC
                            ) AS row_num
                        FROM
                            {name_table}
                    ) t
                WHERE
                    t.row_num > 1
            );
        $BODY$;
        """
        try:
            self.cursor.execute(sql)
        except Exception as e:
            pass
        return f'proc_deletar_duplicada_{name_table}'

    def create_procedure_to_delete_duplicateds(self, name_table):
        """
        Create a procedure to delete duplicateds values from name table reference.

        :param name_table: The name of the table in database.
        :type name_table: str
        :return: The name of the created procedure.
        :rtype: str
        """
        columns = self.select_columns(name_table)
        if len(columns.strip()) > 0:
            return self.handle_connection(self._create_procedure_to_delete_duplicateds, name_table, columns)


class BotsDatabase:

    def __init__(self, database: str):
        """
        Initialize the BotsDatabase object.

        :param database: The name of the database.
        :type database: str
        """
        self.pg = PostgresqlConnection(database)
        self.verify_credentials(self.pg.credentials, database)

    def verify_credentials(self, credentials, database):
        """
        Verify the credentials for accessing the database.

        :param credentials: The database credentials.
        :type credentials: tuple
        :param database: The name of the database.
        :type database: str
        """
        invalid_authentication = False
        try:
            self.pg.test_conection()
        except Exception as e:
            logging.exception(e)
            invalid_authentication = True

        if credentials['DBNAME'] != database or invalid_authentication:
            raise WrongBotDatabase


class TableBots(BotsDatabase):

    def __init__(self, database: str):
        """
        Initialize the TableBots object.

        """
        super().__init__(database)
        self.bot_id = None
        self.bot_name = None
        self.bot_description = None
        self.initiated_values = False
        self.create_table_if_not_exists()

    def init_values(self, bot_name, bot_description):
        """
        Initialize the values of the TableBots object.

        :param bot_name: The name of the bot.
        :type bot_name: str
        :param bot_description: The description of the bot.
        :type bot_description: str
        """
        self.bot_name = bot_name
        self.bot_description = bot_description
        self.bot_id = self.generate_bot_id(self.bot_name)
        self.initiated_values = True

    def show_values(self):
        """
        Show the initialized values.

        """
        if self.initiated_values:
            logging.info(f"""
                bot_id:{self.bot_id},
                bot_name:{self.bot_name},
                bot_description:{self.bot_description},
            """)
        else:
            raise ValuesNotInitiated

    def _create_table_if_not_exists(self):
        """
        Create the bots table if it does not exist.

        """
        # Creating the Bots Table
        self.pg.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bots(
            bot_id NUMERIC PRIMARY KEY,
            bot_name TEXT NOT NULL,
            bot_description TEXT,
            bot_created_date TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """)

    def create_table_if_not_exists(self):
        """
        Create the bots table if it does not exist.

        """
        self.pg.handle_connection(self._create_table_if_not_exists)

    def _insert_or_update(self):
        """
        Insert or update a bot when it is registered.

        """
        self.pg.cursor.execute(f"""
        INSERT INTO bots (bot_id, bot_name, bot_description)
        VALUES ({self.bot_id}, '{self.bot_name}', '{self.bot_description}')
        ON CONFLICT (bot_id) 
        DO UPDATE SET bot_description = EXCLUDED.bot_description;
        """)

    def register_bot(self):
        """
        Register the bot.

        """
        if self.initiated_values:
            self.pg.handle_connection(self._insert_or_update)
        else:
            raise ValuesNotInitiated

    @staticmethod
    def generate_bot_id(bot_name):
        """
        Generate a unique bot ID based on the bot name.

        :param bot_name: The name of the bot.
        :type bot_name: str
        :return: The generated bot ID.
        :rtype: int
        """
        st = string.ascii_uppercase + string.ascii_lowercase
        bot_id = ''
        for i, c in enumerate(bot_name):
            index = st.find(c)
            bot_id += str(index) if index != -1 else c
        return int(bot_id)


class TaskTable(BotsDatabase):

    def __init__(self, database: str):
        """
        Initialize the TaskTable object.

        """
        super().__init__(database)
        self.task_id = None
        self.bot_id = None
        self.task_name = None
        self.task_description = None
        self.pc_path = None
        self.user_login = None
        self.bot_version = None
        self.task_end_time = None
        self.initiated_values = True
        self.create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """
        Create the tasks table if it does not exist.

        """
        # Creating the Tasks Table
        self.pg.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            task_id NUMERIC PRIMARY KEY,
            bot_id NUMERIC NOT NULL,
            task_name TEXT NOT NULL,
            task_description TEXT,
            FOREIGN KEY (bot_id) REFERENCES bots (bot_id)
        );
        """)

    def init_values(self, bot_id, task_name, task_description):
        """
        Initialize the values of the TaskTable object.

        :param bot_id: The bot ID.
        :type bot_id: int
        :param task_name: The task name.
        :type task_name: str
        :param task_description: The task description.
        :type task_description: str
        """
        self.task_id = self.generate_task_id(bot_id, task_name)
        self.bot_id = bot_id
        self.task_name = task_name
        self.task_description = task_description
        self.initiated_values = True

    def show_values(self):
        """
        Show the initialized values.

        """
        if self.initiated_values:
            logging.info(f"""
                task_id = {self.task_id}
                bot_id = {self.bot_id}
                task_name = {self.task_name}
                task_description = {self.task_description}

            """)
        else:
            raise ValuesNotInitiated

    def create_table_if_not_exists(self):
        """
        Create the tasks table if it does not exist.

        """
        self.pg.handle_connection(self._create_table_if_not_exists)

    def _insert_or_update_on_register_task(self):
        """
        Insert or update a task when it is registered.

        """
        self.pg.cursor.execute(f"""
        INSERT INTO tasks (task_id,bot_id, task_name, task_description)
        VALUES ({self.task_id},{self.bot_id}, '{self.task_name}', '{self.task_description}')
        ON CONFLICT (task_id) 
        DO UPDATE SET task_name = EXCLUDED.task_name, task_description = EXCLUDED.task_description;
        """)

    def register_task(self):
        """
        Register the task.

        """
        if self.initiated_values:
            self.pg.handle_connection(self._insert_or_update_on_register_task)
        else:
            raise ValuesNotInitiated

    @staticmethod
    def generate_task_id(bot_id, task_name):
        """
        Generate a unique task ID based on the bot ID and task name.

        :param bot_id: The bot ID.
        :type bot_id: int
        :param task_name: The task name.
        :type task_name: str
        :return: The generated task ID.
        :rtype: int
        """
        st = string.ascii_uppercase + string.ascii_lowercase
        task_id = ''
        for i, c in enumerate(task_name):
            index = st.find(c)
            task_id += str(index) if index != -1 else c
        return int(bot_id) + int(task_id)


class TaskResults(BotsDatabase):

    def __init__(self, database: str):
        """
        Initialize the TaskResults object.

        """
        super().__init__(database)
        self.result_id = None
        self.task_id = None
        self.pc_path = None
        self.user_login = None
        self.bot_version = None
        self.result_status = None
        self.result_data = None
        self.error_message = None
        self.initiated_values = False
        self.create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """
        Create the tasks_results table if it does not exist.

        """
        # Creating the Tasks_Results Table
        self.pg.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks_results(
            result_id NUMERIC PRIMARY KEY,
            task_id NUMERIC NOT NULL,
            pc_path TEXT,
            user_login TEXT,
            bot_version TEXT,
            result_status TEXT NOT NULL,
            result_data TEXT,
            error_message TEXT,
            task_start_time TIMESTAMP NOT NULL DEFAULT NOW(),
            task_end_time TIMESTAMP DEFAULT NULL,
            duration_task NUMERIC DEFAULT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (task_id)
        );
        """)

    def init_values(self, task_id, pc_path, user_login, bot_version):
        """
        Initialize the values of the TaskResults object.

        :param task_id: The task ID.
        :type task_id: int
        :param pc_path: The PC path.
        :type pc_path: str
        :param user_login: The user login.
        :type user_login: str
        :param bot_version: The bot version.
        :type bot_version: str
        """
        self.result_id = self.generate_result_id(task_id)
        self.task_id = task_id
        self.pc_path = pc_path
        self.user_login = user_login
        self.bot_version = bot_version
        self.result_status = False
        self.result_data = None
        self.error_message = None
        self.initiated_values = True

    def show_values(self):
        """
        Show the initialized values.

        """
        if self.initiated_values:
            logging.info(f"""
                result_id = {self.result_id}
                task_id = {self.task_id}
                pc_path = {self.pc_path}
                user_login = {self.user_login}
                bot_version = {self.bot_version}
                result_status = {self.result_status}
                result_data = {self.result_data}
                error_message = {self.error_message}
            """)
        else:
            raise ValuesNotInitiated

    def create_table_if_not_exists(self):
        """
        Create the tasks_results table if it does not exist.

        """
        self.pg.handle_connection(self._create_table_if_not_exists)

    def _insert_on_open_task(self):
        """
        Insert a new task result when the task is opened.

        """
        self.pg.cursor.execute(f"""
        INSERT INTO tasks_results (result_id,task_id, pc_path, user_login, bot_version, result_status, result_data,error_message)
        VALUES ({self.result_id},{self.task_id}, '{self.pc_path}', '{self.user_login}', '{self.bot_version}',
         '{self.result_status}', '{self.result_data}', '{self.error_message}');
        """)

    def _update_on_close_task_old(self):
        """
        Update the task result when the task is closed.

        """
        self.pg.cursor.execute(f"""
        UPDATE tasks_results
        SET task_end_time = NOW(), result_status = '{self.result_status}', result_data = '{self.result_data}',
        error_message = '{self.error_message}'
        WHERE result_id = {self.result_id};

        UPDATE tasks_results
        SET duration_task = CAST(EXTRACT(EPOCH FROM (task_end_time - task_start_time)) AS INTEGER);
        """)

    def _skip_locked(self):
        """
        Update the task result when the task is closed.

        """
        self.pg.cursor.execute(f"""
        SELECT * FROM tasks_results
        WHERE result_id = {self.result_id}
        FOR UPDATE SKIP LOCKED;
        """)

    def _update_duration_tasks(self):
        """
        Update the duration task for all

        """
        self.pg.cursor.execute("""
        UPDATE tasks_results
        SET duration_task = EXTRACT(EPOCH FROM (task_end_time - task_start_time)),
        WHERE task_start_time IS NOT NULL AND task_end_time IS NOT NULL
        FOR UPDATE SKIP LOCKED;
        """)

    def _update_on_close_task(self):
        """
        Update the task result when the task is closed.

        """
        self._skip_locked()
        self.pg.cursor.execute(f"""
        UPDATE tasks_results
        SET task_end_time = NOW(), result_status = '{self.result_status}', result_data = '{self.result_data}',
        error_message = '{self.error_message}'
        WHERE result_id = {self.result_id};
        """)

        self.pg.cursor.execute(f"""
        UPDATE tasks_results
        SET duration_task = CAST(EXTRACT(EPOCH FROM (task_end_time - task_start_time)) AS INTEGER)
        WHERE result_id = {self.result_id} AND task_start_time IS NOT NULL;
        """)
        # self._update_duration_tasks()

    def open_task(self):
        """
        Open the task.

        """
        if self.initiated_values:
            self.pg.handle_connection(self._insert_on_open_task)
        else:
            raise ValuesNotInitiated

    def end_task(self, result_status, result_data, error_message):
        """
        End the task with the given result status, data, and error message.

        :param result_status: The status of the task result.
        :type result_status: bool
        :param result_data: The data of the task result.
        :type result_data: str
        :param error_message: The error message of the task result.
        :type error_message: str
        """
        if self.initiated_values:
            self.result_status = result_status
            self.result_data = result_data
            self.error_message = error_message
            self.pg.handle_connection(self._update_on_close_task)
        else:
            raise ValuesNotInitiated

    @staticmethod
    def generate_result_id(task_id):
        """
        Generate a unique result ID based on the task ID and current timestamp.

        :param task_id: The task ID.
        :type task_id: int
        :return: The generated result ID.
        :rtype: int
        """
        now = datetime.now()
        timestamp = now.timestamp()
        return task_id + int(timestamp)


class BotTable:

    def __init__(self, database: str):
        """
        Initialize the BotTable object.

        """
        self.table_bot = TableBots(database)
        self.task_table = TaskTable(database)
        self.task_result = TaskResults(database)

    # register bot
    def register_bot(self, bot_name: str, bot_description: str):
        """
        Register a bot with its name and description.

        :param bot_name: The name of the bot.
        :type bot_name: str
        :param bot_description: The description of the bot.
        :type bot_description: str
        """
        self.table_bot.init_values(bot_name, bot_description)
        self.table_bot.register_bot()

    # register task
    def register_task(self, task: str, task_description: str):
        """
        Register a task with its name and description.

        :param task: The name of the task.
        :type task: str
        :param task_description: The description of the task.
        :type task_description: str
        """
        self.task_table.init_values(self.table_bot.bot_id, task, task_description)
        self.task_table.register_task()

    # initializing new result from task
    def create_new_instance_from_task(self, bot_version, user: str = ''):
        """
        Create a new instance for a task result.

        :param bot_version: The version of the bot.
        :type bot_version: str
        :param user: The name of the user.
        :type user: str
        """
        self.task_result.init_values(self.task_table.task_id, os.getcwd(), user, bot_version)

    # opening the new task result
    def open_task(self):
        """
        Open the task result.

        """
        self.task_result.open_task()

    def end_task(self, status: bool, resultado: str, if_erro: str):
        """
        End the task with the given status, result, and error message.

        :param status: The status of the task.
        :type status: bool
        :param resultado: The result of the task.
        :type resultado: str
        :param if_erro: The error message if the task failed.
        :type if_erro: str
        """
        self.task_result.end_task(status, resultado, if_erro)


def migrate_data_bots_server_bots():
    import pandas as pd
    db_from = Postgresql('Bots')
    db_to = Postgresql('BotsN')

    # Select the data from old database
    script = "select * from bots"
    data = db_from.execute_script(script)
    columns = db_from.select_columns('bots', False).replace('"', '').split(' ,')
    df = pd.DataFrame(data)
    df.columns = columns

    # Select data from new database
    script = "select * from bots"
    data = db_to.execute_script(script)
    columns2 = db_to.select_columns('bots', False).replace('"', '').split(' ,')
    df2 = pd.DataFrame(data)
    df2.columns = columns2

    # select the ids to ignore
    ignore_index = [i for i, id_ in enumerate(df[df.columns[0]]) if id_ not in df2[df2.columns[0]].tolist()]

    # delete ids to ignore from dataframe's old database
    table = df.loc[ignore_index].reset_index(drop=True)

    logging.info(table)

    # insert the different data into the new database
    db_to.to_postgresql(table, 'bots', id_column=False)


def migrate_data_bots_server_tasks():
    import pandas as pd
    db_from = Postgresql('Bots')
    db_to = Postgresql('BotsN')

    # Select the data from old database
    script = "select * from tasks"
    data = db_from.execute_script(script)
    columns = db_from.select_columns('tasks', False).replace('"', '').split(' ,')
    df = pd.DataFrame(data)
    df.columns = columns

    # Select data from new database
    script = "select * from tasks"
    data = db_to.execute_script(script)
    columns2 = db_to.select_columns('tasks', False).replace('"', '').split(' ,')
    df2 = pd.DataFrame(data)
    df2.columns = columns2

    # select the ids to ignore
    ignore_index = [i for i, id_ in enumerate(df[df.columns[0]]) if id_ not in df2[df2.columns[0]].tolist()]

    # delete ids to ignore from dataframe's old database
    table = df.loc[ignore_index].reset_index(drop=True)

    logging.info(table)

    # insert the different data into the new database
    db_to.to_postgresql(table, 'tasks', id_column=False)


def migrate_data_bots_server_tasks_results():
    import pandas as pd
    db_from = Postgresql('Bots')
    db_to = Postgresql('BotsN')

    # Select the data from old database
    script = "select * from tasks_results"
    data = db_from.execute_script(script)
    columns = db_from.select_columns('tasks_results', False).replace('"', '').split(' ,')
    df = pd.DataFrame(data)
    df.columns = columns

    # Select data from new database
    script = "select * from tasks_results"
    data = db_to.execute_script(script)
    columns2 = db_to.select_columns('tasks_results', False).replace('"', '').split(' ,')
    df2 = pd.DataFrame(data)
    df2.columns = columns2

    # select the ids to ignore
    ignore_index = [i for i, id_ in enumerate(df[df.columns[0]]) if id_ not in df2[df2.columns[0]].tolist()]

    # delete ids to ignore from dataframe's old database
    table = df.loc[ignore_index].reset_index(drop=True)

    # adjust some columns
    table['task_end_time'] = ['NULL' if str(val) == 'NaT' else val for val in table['task_end_time']]
    table['duration_task'] = ['NULL' if str(val) == 'None' else val for val in table['duration_task']]

    logging.info(table)

    # insert the different data into the new database
    db_to.to_postgresql(table, 'tasks_results', id_column=False)


if __name__ == '__main__':
    # migrate_data_bots_server_tasks()
    migrate_data_bots_server_tasks_results()
