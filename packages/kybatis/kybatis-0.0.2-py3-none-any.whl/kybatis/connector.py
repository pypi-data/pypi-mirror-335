import traceback
from typing import Optional, Generator
from logging import Logger, getLogger

import oracledb
from mysql.connector import pooling

from kybatis.mapper import Mapper
from kybatis.types_ import DB_INFO, DB_TYPE, BaseQuery


class Connector:
    """ MYSQL,ORACLE compatible connector class

        Attributes:
        _logger: Logger class for logging results. If not set, use root.
        _db_info: Type of database one of ["mysql", "oracle"].
        _mapper: Class that receives query ID and parameters and converts SQL query
        _session_pool: Class that Session(connection) pool of database
    """

    def __init__(self, db_type: str, ip: str, port: int, user: str, password: str, query_path: str,
                 db: str | None = None,
                 sid: str | None = None, dsn: str | None = None,
                 collation: Optional[str] = None,
                 session_pool_min: Optional[int] = 5,
                 session_pool_max: Optional[int] = 10,
                 logger: Optional[Logger] = None):
        """Inits Connector.

        Args:
            db_type: Type of database one of ["mysql", "oracle"].
            ip: Database connection IP.
            port: Database connection PORT.
            user: Database user.
            password: User's password.
            query_path: Path of mybatis style xml file where the query is stored.
            db: Database name to connect to (if mysql).
            sid: SID to connect (if oracle).
            dsn: DSN(Data Source Name) to connect (if oracle). it is given priority over connection via sid.
            collation: Collation information (if mysql).
            session_pool_min: Minimum number of connection pools.
            session_pool_max: Maximum number of connection pools.
            logger: Logger class for logging results. If not set, use root.

        Returns:

        """
        self._logger = logger
        if self._logger is None:
            self._logger = getLogger("root")

        if db_type == DB_TYPE.ORACLE:
            if sid is None:
                raise AttributeError("sid must be defined on oracle")
        if db_type == DB_TYPE.MYSQL:
            if db is None:
                raise AttributeError("db must be defined on oracle")
        self._db_info = DB_INFO(type=db_type, sid=sid, db=db, user=user,
                                password=password, ip=ip, port=port,
                                session_pool_min=session_pool_min, session_pool_max=session_pool_max)
        if query_path is not None:
            self._mapper = Mapper(path=query_path)
        else:
            self._mapper = None
        self._session_pool: oracledb.SessionPool | pooling.MySQLConnectionPool | None = None
        if db_type == DB_TYPE.ORACLE:
            if dsn in None:
                self._dsn = oracledb.makedsn(host=ip, port=port, sid=sid)
            else:
                self._dsn = dsn
            self._session_pool = oracledb.SessionPool(user=user, password=password, dsn=self._dsn,
                                                      min=session_pool_min, max=session_pool_max,
                                                      increment=1, encoding="UTF-8")
        elif db_type == DB_TYPE.MYSQL:
            mysql_kwargs = {"pool_name": "pool_mysql",
                            "pool_size": session_pool_max,
                            "pool_reset_session": True,
                            "host": ip,
                            "port": port,
                            "database": db,
                            "user": user,
                            "password": password}
            if collation is not None:
                mysql_kwargs["collation"] = collation
            self._session_pool = pooling.MySQLConnectionPool(**mysql_kwargs)

    def connection_test(self) -> None:
        """Test whether the connection is established.

        Args:

        Returns:
        """
        try:
            if self._db_info.type == DB_TYPE.MYSQL:
                test_connection = self._session_pool.get_connection()
                test_connection.close()
            elif self._db_info.type == DB_TYPE.ORACLE:
                test_connection = self._session_pool.acquire()
                self._session_pool.release(test_connection)
        except Exception as exc:
            self._logger.error(f"connection test failed by {exc.__str__()}. traceback: {traceback.format_exc()}")
        else:
            self._logger.info("connection test: success")

    def select_one(self,
                   namespace: Optional[str] = None,
                   query_id: Optional[str] = None,
                   param: Optional[dict] = None,
                   query: Optional[str] = None, ) -> tuple:
        """Returns one of the results of query execution.

        Args:
            namespace: Namespace containing the query to call.
            query_id: Query ID to call.
            param: Parameters to be configured in the query.
            query: If you do not use the query saved in the xml file, just pass the query.

        Returns:
            Query execution result(single)
        """
        if query is None:
            query = self._mapper.get_query(namespace, query_id, param)
        self._logger.info(f"execute query: {query}")
        result = None
        if self._db_info.type == DB_TYPE.MYSQL:
            with self._session_pool.get_connection() as connection_obj:
                cursor = connection_obj.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()
        elif self._db_info.type == DB_TYPE.ORACLE:
            with self._session_pool.acquire() as connection_obj:
                cursor = connection_obj.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()
        return result

    def select(self,
               namespace: Optional[str] = None,
               query_id: Optional[str] = None,
               param: Optional[dict] = None,
               query: Optional[str] = None, ) -> list[tuple]:
        """Returns the results of query execution.

        Args:
            namespace: Namespace containing the query to call.
            query_id: Query ID to call.
            param: Parameters to be configured in the query.
            query: If you do not use the query saved in the xml file, just pass the query.

        Returns:
            Query execution result
        """
        if query is None:
            query = self._mapper.get_query(namespace, query_id, param)
        result = None
        self._logger.info(f"execute query: {query}")
        if self._db_info.type == DB_TYPE.MYSQL:
            with self._session_pool.get_connection() as connection_obj:
                cursor = connection_obj.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
        elif self._db_info.type == DB_TYPE.ORACLE:
            with self._session_pool.acquire() as connection_obj:
                cursor = connection_obj.cursor()
                result = cursor.execute(query)
                result = result.fetchall()
                cursor.close()
        return result

    def select_chunk(self,
                     namespace: Optional[str] = None,
                     query_id: Optional[str] = None,
                     param: Optional[dict] = None,
                     prefetch_row: Optional[int] = 10000,
                     array_size: Optional[int] = 10000,
                     include_headers: bool = False,
                     query: Optional[str] = None) -> Generator[list[tuple], None, None]:
        """Retrieves query execution results in chunks.

        Args:
            namespace: Namespace containing the query to call.
            query_id: Query ID to call.
            param: Parameters to be configured in the query.
            prefetch_row: Number of rows to be prefetched.
            array_size: Number of chunks to read.
            include_headers: Whether to include headers when loading chunks.
            query: If you do not use the query saved in the xml file, just pass the query.

        Returns:
            Query execution result in Generator
        """
        if query is None:
            query = self._mapper.get_query(namespace, query_id, param)
        self._logger.info(f"execute query: {query}")
        if self._db_info.type == DB_TYPE.ORACLE:
            with self._session_pool.acquire() as conn:
                chunk_cursor = conn.cursor()
                if prefetch_row is not None:
                    chunk_cursor.prefetchrows = prefetch_row
                if array_size is not None:
                    chunk_cursor.arraysize = array_size
                chunk_cursor.execute(query)
                if include_headers:
                    col_names = tuple(row[0] for row in chunk_cursor.description)
                    yield col_names
                while True:
                    results = chunk_cursor.fetchmany(array_size)
                    if not results:
                        break
                    yield results
                chunk_cursor.close()
        elif self._db_info.type == DB_TYPE.MYSQL:
            with self._session_pool.get_connection() as connection_obj:
                cursor = connection_obj.cursor()
                cursor.execute(query)
                if include_headers:
                    yield cursor.column_names
                while True:
                    result = cursor.fetchmany(array_size)
                    if not result:
                        break
                    yield result
                cursor.close()

    def execute(self, namespace: str,
                query_id: str,
                param: dict = None) -> None:
        """Execute the query.

        Args:
            namespace: Namespace containing the query to call.
            query_id: Query ID to call.
            param: Parameters to be configured in the query.

        Returns:
        """
        query = self._mapper.get_query(namespace, query_id, param)
        row_count = 0
        self._logger.info(f"execute query: {query}")
        if self._db_info.type == DB_TYPE.ORACLE:
            with self._session_pool.acquire() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                row_count = cursor.rowcount
                cursor.close()
        elif self._db_info.type == DB_TYPE.MYSQL:
            with self._session_pool.get_connection() as connection_obj:
                cursor = connection_obj.cursor()
                cursor.execute(query)
                connection_obj.commit()
                row_count = cursor.rowcount
                cursor.close()
        self._logger.info(f"commit: {row_count}")
        return

    def multiple_execution(self, queries: list[BaseQuery]) -> None:
        """Execute the multiple query.

        Args:
            queries: List of BaseQuery class to execute.

        Returns:
        """
        num_queries = len(queries)
        if self._db_info.type == DB_TYPE.ORACLE:
            raise RuntimeError("ORACLE not support this currently.")
        elif self._db_info.type == DB_TYPE.MYSQL:
            with self._session_pool.get_connection() as connection_obj:
                cursor = connection_obj.cursor()
                for idx, query in enumerate(queries):
                    query = self._mapper.get_query(**query.model_dump())
                    self._logger.info(f"multiple execution: {idx + 1}/{num_queries}\n"
                                      f"{query}")
                    cursor.execute(query)
                connection_obj.commit()
                self._logger.info(f"commit: {cursor.rowcount}")
                cursor.close()
        return
