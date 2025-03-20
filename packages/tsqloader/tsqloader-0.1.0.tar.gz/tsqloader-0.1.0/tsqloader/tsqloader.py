from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """
    This class provides a wrapper for interacting with a SQL database using SQLAlchemy. 
    It offers utilities to connect to the database, write data from Pandas DataFrames, 
    handle primary key conflicts, and check table existence.

    Attributes:
    -----------
    - server (str): The address of the database server.
    - database (str): The name of the database.
    - username (str): The username for database authentication.
    - password (str): The password for database authentication.
    - driver (str): The ODBC driver for the database connection (default: "ODBC Driver 17 for SQL Server").
    - engine (SQLAlchemy Engine): The SQLAlchemy engine for managing database connections.
    """
    
    def __init__(self, server, database, username, password, driver="ODBC Driver 17 for SQL Server"):
        """
        Initialize the DatabaseHandler with connection details.
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.engine = self._create_engine()

    def _create_engine(self):
        """
        This is an internal function!

        Create a SQLAlchemy engine.
        
        Returns:
        --------
        An SQLAlchemy engine object for managing connections.
        """
        connection_string = f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver={self.driver}"
        return create_engine(connection_string)

    def write_to_db(self, df, table_name, primary_keys):
        """
        Write a Pandas DataFrame to a SQL table, replacing rows with matching primary keys.

        Parameters:
        -----------
        - df (Pandas DataFrame): The data to write to the database.
        - table_name (str): The name of the target SQL table.
        - primary_keys (list of str): Column names serving as primary keys for conflict resolution.

        Raises:
        -------
        - ValueError: If no primary keys are provided or the target table does not exist.
        - SQLAlchemyError: For database-related errors.
        """
        if not primary_keys:
            raise ValueError("Primary keys must be provided for conflict resolution.")

        if df.empty:
            logger.warning("The DataFrame is empty. Nothing to write.")
            return

        if not self._table_exists(table_name):
            raise ValueError(f"Table '{table_name}' does not exist in the database.")

        try:
            with self.engine.begin() as connection:
                # Delete conflicting rows
                self._delete_conflicting_rows(df, table_name, primary_keys, connection)

                # Insert new rows
                df.to_sql(table_name, con=connection, if_exists='append', index=False)

                logger.info(f"Data successfully written to table '{table_name}'.")
        except SQLAlchemyError as e:
            logger.error(f"Error uploading logs to the database: {e}")
            raise

    def _delete_conflicting_rows(self, df, table_name, primary_keys, connection):
        """
        This is an internal function!

        Delete rows in the database that match the primary keys in the DataFrame.

        Parameters:
        -----------
        - df (Pandas DataFrame): The DataFrame containing rows to check for conflicts.
        - table_name (str): The target SQL table.
        - primary_keys (list of str): The primary key columns.
        - connection (SQLAlchemy Connection): The active database connection.
        """
        where_clause = " AND ".join([f"{key} = :{key}" for key in primary_keys])
        delete_query = f"DELETE FROM {table_name} WHERE {where_clause}"

        for _, row in df.iterrows():
            params = {key: row[key] for key in primary_keys}
            connection.execute(text(delete_query), params)

    def _table_exists(self, table_name):
        """
        This is an internal function!

        Checks if a table exists in the database.

        Parameters:
        -----------
        - table_name (str): The name of the table.

        Returns:
        --------
        - True if the table exists, False otherwise.
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
