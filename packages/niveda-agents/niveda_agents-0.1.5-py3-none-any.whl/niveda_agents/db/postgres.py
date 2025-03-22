import psycopg2
import os
import logging
from dotenv import load_dotenv
from niveda_agents.utils.logger import setup_logger

load_dotenv()
logger = setup_logger()
logger.info("✅ Logger initialized successfully!")


class PostgresDB:
    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        """
        Initialize PostgreSQL connection with user-provided or default `.env` values.

        :param dbname: PostgreSQL database name (optional, if not provided, uses .env)
        :param user: PostgreSQL username (optional, if not provided, uses .env)
        :param password: PostgreSQL password (optional, if not provided, uses .env)
        :param host: PostgreSQL host (optional, if not provided, uses .env)
        :param port: PostgreSQL port (optional, if not provided, uses .env)
        """
        try:
            self.dbname = dbname or os.getenv("POSTGRES_DB", "niveda_db")
            self.user = user or os.getenv("POSTGRES_USER", "postgres")
            self.password = password or os.getenv(
                "POSTGRES_PASSWORD", "password")
            self.host = host or os.getenv("POSTGRES_HOST", "localhost")
            self.port = port or os.getenv("POSTGRES_PORT", "5432")

            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            logger.info(
                f"✅ Connected to PostgreSQL: {self.dbname} on {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"❌ Error connecting to PostgreSQL: {e}")

    def execute_query(self, query, params=None):
        """Execute a query (INSERT, UPDATE, DELETE) with error handling."""
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            logger.info("✅ Query Executed Successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error executing query: {e}")

    def fetch_results(self, query, params=None):
        """Fetch results from a SELECT query."""
        try:
            self.cursor.execute(query, params or ())
            results = self.cursor.fetchall()
            logger.info(f"✅ Data Retrieved: {results}")
            return results
        except Exception as e:
            logger.error(f"❌ Error fetching data: {e}")
            return None

    def create_table(self, table_name, columns):
        """
        Create a table dynamically.
        :param table_name: Table name.
        :param columns: Dict {column_name: "DATATYPE CONSTRAINTS"}.
        """
        column_definitions = ", ".join(
            [f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"
        self.execute_query(query)
        logger.info(f"✅ Table '{table_name}' Created.")

    def create_index(self, table_name, columns):
        """
        Create indexes dynamically on multiple columns.
        :param table_name: Name of the table.
        :param columns: List of column names to index.
        """
        for column in columns:
            index_name = f"{table_name}_{column}_idx"
            query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column});"
            self.execute_query(query)
            logger.info(
                f"✅ Index '{index_name}' created on {table_name}({column}).")

    def insert_data(self, table_name, data):
        """
        Insert data dynamically into a table.
        :param table_name: Name of the table.
        :param data: Dict {column_name: value}.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *;"
        self.execute_query(query, tuple(data.values()))
        logger.info(f"✅ Data inserted into '{table_name}'.")

    def update_data(self, table_name, update_values, condition):
        """
        Update data dynamically.
        :param table_name: Name of the table.
        :param update_values: Dict {column_name: new_value}.
        :param condition: Dict {column_name: value} (WHERE clause).
        """
        set_clause = ", ".join([f"{col} = %s" for col in update_values.keys()])
        where_clause = " AND ".join(
            [f"{col} = %s" for col in condition.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
        self.execute_query(query, tuple(
            update_values.values()) + tuple(condition.values()))
        logger.info(f"✅ Data updated in '{table_name}'.")

    def delete_data(self, table_name, condition):
        """
        Delete data dynamically.
        :param table_name: Name of the table.
        :param condition: Dict {column_name: value} (WHERE clause).
        """
        where_clause = " AND ".join(
            [f"{col} = %s" for col in condition.keys()])
        query = f"DELETE FROM {table_name} WHERE {where_clause};"
        self.execute_query(query, tuple(condition.values()))
        logger.info(f"✅ Data deleted from '{table_name}'.")

    def empty_table(self, table_name):
        """Remove all data from a table but keep the structure."""
        query = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
        self.execute_query(query)
        logger.info(f"✅ Table '{table_name}' emptied.")

    def delete_table(self, table_name):
        """Drop a table permanently."""
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        self.execute_query(query)
        logger.info(f"✅ Table '{table_name}' deleted.")

    def close_connection(self):
        """Close the database connection."""
        self.cursor.close()
        self.conn.close()
        logger.info("🔻 PostgreSQL Connection Closed")
