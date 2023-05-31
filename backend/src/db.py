import os
from typing import Any, LiteralString

from mysql.connector import Error, MySQLConnection, errorcode
from mysql.connector.cursor import MySQLCursor
from mysql.connector.types import ParamsSequenceOrDictType


class DB(object):

    _conn: MySQLConnection | None = None
    """Connection to the database"""

    _stmt: MySQLCursor | None = None
    """Database connection cursor"""

    results: list[dict[str, Any]] = []
    """Data obtained from the query"""

    def __init__(self) -> None:
        """Create database connection"""

        try:
            self._conn = MySQLConnection(
                host=str(os.environ['DB_HOST']),
                database=str(os.environ['DB_DATABASE']),
                user=str(os.environ['DB_USER']),
                password=str(os.environ['DB_PASS']),
                port=int(os.environ['DB_PORT']),
                use_unicode=True,
                charset='utf8',
            )
        except Error as err:
            msg_error = {
                errorcode.ER_ACCESS_DENIED_ERROR: "🔥 Something is wrong with your user name or password",
                errorcode.ER_BAD_DB_ERROR: "🔥 Database '%s' does not exist" % str(os.environ['DB_DATABASE']),
            }
            msg_error_default = f"🔥 Database connection error: {err}"

            err.add_note(
                msg_error[err.errno] if err.errno in msg_error else msg_error_default)

            raise
        else:
            self._stmt = self._conn.cursor(buffered=True)

    def _get_data(self) -> None:
        """Store the data obtained from the query"""
        if self._stmt is None:
            raise Exception("Error, no active database connection cursor")

        self.results = []
        for row in self._stmt.fetchall():
            data = {}
            for i, column in enumerate(self._stmt.column_names):
                data[column] = row[i]
            self.results.append(data)

    @staticmethod
    def filter_by_number_of_elements(status_show: list) -> LiteralString:

        if len(status_show) == 1:
            return '= %s'

        return 'IN (' + ('%s, ' * len(status_show)).rstrip(', ') + ')'

    def execute(self, sql: LiteralString = '', data: ParamsSequenceOrDictType | None = None, fields: bool = False) -> int | None:
        """Execute Prepared Statements"""

        if self._stmt is None:
            raise Exception("Error, no active cursor to database")

        try:
            self._stmt.execute(sql, params=data, multi=False)
        except Error as err:
            err.add_note(f"🔥 Error executing the query:\n{err}\n{sql}")
            raise
        else:
            if self._conn is None:
                raise Exception("Error, no connection active to database")
            # COMMIT SQL
            self._conn.commit()
            # Obtener los datos de la consulta
            if fields:
                self._get_data()
            elif 'INSERT' in sql.upper():
                return self._stmt.lastrowid

        return None

    def close(self) -> None:
        """Close cursor and database connections"""

        if self._stmt is not None:
            self._stmt.close()
            self._stmt = None

        if self._conn is not None:
            self._conn.commit()
            self._conn.close()
            self._conn = None

    def __del__(self):
        self.close()
