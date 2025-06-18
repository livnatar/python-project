import psycopg2
from psycopg2.extras import RealDictCursor
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# consts for connecting to db
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "dbname"
DB_USER = "admin"
DB_PASSWORD = "Aa123456"


def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def execute_query(query, params=None, fetch=False):
    """Execute a query with error handling"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)

        if fetch:
            result = cursor.fetchall()
            conn.commit()
            return result
        else:
            conn.commit()
            return cursor.rowcount

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Query execution error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_single_query(query, params=None):
    """Execute a query and return single result"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        return result
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Single query execution error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def test_connection():
    """Test database connection with detailed error reporting"""
    try:
        print(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info(f"Connected to PostgreSQL: {version[0]}")
        return True
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        logger.error(f"Connection details: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
        return False
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Read and execute SQL file
    try:
        with open('init_tables.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        print("Tables created successfully!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")