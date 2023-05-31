import os
import unittest

from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from src.db import DB


class ConnectionDB(unittest.TestCase):

    def test_credentials_defined(self) -> None:
        self.assertIn('DB_HOST', os.environ,
                      "Environment variable DB_HOST is undefined")
        self.assertIn('DB_DATABASE', os.environ,
                      "Environment variable DB_DATABASE is undefined")
        self.assertIn('DB_USER', os.environ,
                      "Environment variable DB_USER is undefined")
        self.assertIn('DB_PASS', os.environ,
                      "Environment variable DB_PASS is undefined")
        self.assertIn('DB_PORT', os.environ,
                      "Environment variable DB_PORT is undefined")

    def test_credentials_not_empty(self) -> None:
        self.assertNotEqual(
            os.environ['DB_HOST'], '', "Environment variable DB_HOST is empty")
        self.assertNotEqual(
            os.environ['DB_DATABASE'], '', "Environment variable DB_DATABASE is empty")
        self.assertNotEqual(
            os.environ['DB_USER'], '', "Environment variable DB_USER is empty")
        # self.assertNotEqual(
        #     os.environ['DB_PASS'], '', "Environment variable DB_PASS is empty")
        self.assertNotEqual(
            os.environ['DB_PORT'], '', "Environment variable DB_PORT is empty")

    def test_credentials_type(self) -> None:
        try:
            str(os.environ['DB_HOST'])
        except ValueError as e:
            self.fail("DB_HOST type raised ValueError {}".format(e))

        try:
            str(os.environ['DB_DATABASE'])
        except ValueError as e:
            self.fail("DB_DATABASE type raised ValueError {}".format(e))

        try:
            str(os.environ['DB_USER'])
        except ValueError as e:
            self.fail("DB_USER type raised ValueError {}".format(e))

        try:
            str(os.environ['DB_PASS'])
        except ValueError as e:
            self.fail("DB_PASS type raised ValueError {}".format(e))

        try:
            int(os.environ['DB_PORT'])
        except ValueError as e:
            self.fail("DB_PORT type raised ValueError {}".format(e))

    def test_connection_to_db(self) -> None:
        db = DB()
        self.assertIsInstance(db._conn, MySQLConnection)
        self.assertIsInstance(db._stmt, MySQLCursor)

        self.assertIsNone(db.execute("SELECT 1 AS ok FROM DUAL", fields=True))
        self.assertListEqual(db.results, [{'ok': 1}])

        db.close()
        self.assertNotIsInstance(db._conn, MySQLConnection)
        self.assertNotIsInstance(db._stmt, MySQLCursor)

    def test_filter_by_number_of_elements(self):
        self.assertEqual(DB.filter_by_number_of_elements(['1']), '= %s')
        self.assertEqual(DB.filter_by_number_of_elements(
            list(range(3))), 'IN (%s, %s, %s)')


if __name__ == '__main__':
    unittest.main()
