"""
Database connection management for PostgreSQL.
"""
import logging
import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections with connection pooling."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            connection_string: PostgreSQL connection string. If None, reads from environment.
        """
        self.connection_string = connection_string or os.getenv(
            'DATABASE_URL',
            #change ifport database or placement of database is different
            'postgresql://postgres:Zappanoel1229!@localhost:5432/developer_skills'
        )
        self._pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize the connection pool."""
        try:
            self._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.connection_string
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            Database connection with RealDictCursor
        """
        if not self._pool:
            self._initialize_pool()
        
        conn = self._pool.getconn()
        conn.cursor_factory = RealDictCursor
        return conn
    
    def return_connection(self, conn) -> None:
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        if self._pool:
            self._pool.putconn(conn)
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, None otherwise
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                results = cursor.fetchall()
                conn.commit()  # Commit even when fetching (for stored procedures)
                return results
            else:
                conn.commit()
                return None
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database query error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def execute_many(self, query: str, params_list: list) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database executemany error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def call_procedure(self, procedure_name: str, params: tuple = None):
        """
        Call a stored procedure.
        
        Args:
            procedure_name: Name of the stored procedure
            params: Procedure parameters
            
        Returns:
            Procedure results
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.callproc(procedure_name, params or ())
            
            # Try to fetch results if available
            try:
                results = cursor.fetchall()
                conn.commit()
                return results
            except psycopg2.ProgrammingError:
                # No results to fetch
                conn.commit()
                return None
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Stored procedure error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def execute_transaction(self, queries: list) -> None:
        """
        Execute multiple queries in a single transaction.
        
        Args:
            queries: List of (query, params) tuples
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for query, params in queries:
                cursor.execute(query, params)
            
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Transaction error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 as health")
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
