import config
import unittest
import mysql.connector
from typing import Callable
from app.db.sql_constants import TBL, TBLCol
import app.db.database as database
import app.classifier.utils as utils
from app.db.mit_courses import mit_courses


def setup():
	_cnx = mysql.connector.connect(
		host=config.SQL_HOST,
		user=config.SQL_USER,
		password=config.SQL_PASSWORD,
		database=config.SQL_TEST_DATABASE,
	)
	_cursor = _cnx.cursor()

	def sql_test_commit(method):
		def wrapper(*args, **kwargs):
			out = method(*args, **kwargs)
			_cnx.commit()
			return out

		return wrapper

	database._commit = sql_test_commit
	database.cursor = _cursor


def commit(method: Callable, db_cnx) -> Callable:
	"""
	decorator: calls cnx.commit() at the end of query in order to
	make the changes caused by the query to be permanent in the DB.
	:param method:
		method that calls an SQL query that makes changes to the data
	:param db_cnx:
		sql connection
	:return: method decorated with cnx.commit()
	"""

	def wrapper(*args, **kwargs):
		out = method(*args, **kwargs)
		db_cnx.commit()
		return out

	return wrapper


class TestDatabase(unittest.TestCase):
	# setups
	TABLES = (
		TBL.ResponseMappings,
		TBL.Responses,
		TBL.AnswerChoices,
		TBL.Questions,
		TBL.Courses,
	)

	def setUp(self):
		try:
			setup()
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			self.fail(
				"Connection to DB Error: May want to check if "
				"%s DB exists" % config.SQL_TEST_DATABASE
			)

	@staticmethod
	def drop_all_tables():
		for table in TestDatabase.TABLES:
			database.cursor.execute("DROP TABLE IF EXISTS %s" % table)
			database.cnx.commit()

		tables = TestDatabase.get_tables()
		print('[TestDatabaseLog:tables-after-drop]', tables)
		assert len(tables) == 0, \
			"some tables are still in db. see print statement"

	@staticmethod
	def get_tables():
		database.cursor.execute("SHOW TABLES")
		return [row[0].lower() for row in database.cursor.fetchall()]

	def tearDown(self):
		TestDatabase.drop_all_tables()

	# tests

	def test_initialize(self):
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		tables = TestDatabase.get_tables()
		for table in [db_table.lower() for db_table in TestDatabase.TABLES]:
			self.assertTrue(
				table in tables,
				"table %s is missing from tables" % table
			)
		# check the courses database
		database.cursor.execute("SELECT COUNT(*) FROM %s" % TBL.Courses)
		try:
			count = database.cursor.fetchall()[0][0]
		except IndexError:
			self.fail("fetching counts returned no rows")
		self.assertTrue(
			count == len(mit_courses),
			"mit courses length didn't match"
		)

	def test_initialize_twice(self):
		"""
		initialization should not throw an error if the table already exists
		because we will be making the check every time the db is ran up
		:return:
		"""
		TestDatabase.drop_all_tables()
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error the second time")

	def test_initialize_does_not_remove_existing_data(self):
		# drop all tables
		TestDatabase.drop_all_tables()
		# initialize
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		# store some dummy data
		database.cursor.execute("""
			INSERT INTO %s (%s) VALUES ('Coffee')
		""" % (TBL.Questions, TBLCol.question))
		database.cnx.commit()
		database.cursor.execute("""
			INSERT INTO %s (%s, %s, %s) VALUES (1, 'Yo', '1,4')
		""" % (TBL.AnswerChoices, TBLCol.question_id, TBLCol.choice, TBLCol.vector))
		database.cnx.commit()
		# initialize again
		database.initialize_database()
		# check that data was not removed
		database.cursor.execute("SELECT * FROM %s" % TBL.Questions)
		self.assertTrue(
			database.cursor.fetchall()[0][0] == "Coffee",
			"question 'Coffee' was not found in db"
		)
		database.cursor.execute("SELECT * FROM %s" % TBL.AnswerChoices)
		self.assertTrue(
			database.cursor.fetchall()[0] == (1, "Yo", "1,4"),
			"answer choice %s was not found in db" % str((1, "Yo", "1,4"))
		)




if __name__ == '__main__':
	unittest.main()
