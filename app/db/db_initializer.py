from app.db.sql_constants import TBL, TBLCol
from app.utils.string_util import quote
from app.db.mit_courses import mit_courses
import mysql.connector.errors
from mysql.connector.cursor import CursorBase


class _DBInitializer:
	@staticmethod
	def initialize_database(cursor: CursorBase) -> None:
		"""
		when the database is just loaded, we need to make sure that
		all the tables are created in the db. with this method, we
		will not need to manually create tables every time we change
		db: it will just create them at initialization.
		:return: void
		"""
		_DBInitializer.create_courses_table(cursor)
		_DBInitializer.create_questions_table(cursor)
		_DBInitializer.create_answer_choice_table(cursor)
		_DBInitializer.create_response_table(cursor)
		_DBInitializer.create_response_mapping_table(cursor)
		_DBInitializer.add_delete_constraints_if_needed(cursor)
		_DBInitializer.populate_courses_table_with_new_courses(cursor)

	@staticmethod
	def create_courses_table(cursor: CursorBase) -> None:
		courses_data = (
			TBL.Courses,
			TBLCol.course_id,
			TBLCol.course_number,
			TBLCol.course_name,
		)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS %s (
				%s SERIAL,
				%s TINYTEXT NOT NULL,
				%s TINYTEXT NOT NULL
			);
		""" % courses_data)

	@staticmethod
	def create_questions_table(cursor: CursorBase) -> None:
		cursor.execute(
			"CREATE TABLE IF NOT EXISTS %s ( %s SERIAL, %s TEXT NOT NULL)" %
			(TBL.Questions, TBLCol.question_id, TBLCol.question)
		)

	@staticmethod
	def create_answer_choice_table(cursor: CursorBase) -> None:
		answer_choices_query_data = (
			TBL.AnswerChoices,
			TBLCol.answer_id,
			TBLCol.question_id,
			TBLCol.choice,
			TBLCol.vector,
		)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS %s (
				%s SERIAL,
				%s BIGINT UNSIGNED NOT NULL,
				%s TEXT NOT NULL, 
				%s TEXT NOT NULL
			);
		""" % answer_choices_query_data)

	@staticmethod
	def create_response_table(cursor: CursorBase) -> None:
		responses_data = (
			TBL.Responses,
			TBLCol.response_id,
			TBLCol.course_name,
			TBLCol.response_salt,
			TBLCol.time_created,
		)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS %s (
				%s SERIAL,
				-- the course name is extremely unlikely to change 
				-- over a long time. so having that as a safe key 
				-- reference for the course is needed whereas course  
				-- ids are arbitrary. so we retrieve courses with 
				-- course names
				%s TINYTEXT,
				-- response salts are just random strings that are 
				-- generated at creation time in order to fetch the
				-- response id (since ids are incremented 
				-- automatically). 
				%s VARCHAR(10),
				%s DATETIME(6)
			);
		""" % responses_data)

	@staticmethod
	def create_response_mapping_table(cursor: CursorBase) -> None:
		response_mappings_query_data = (
			TBL.ResponseMappings,
			TBLCol.response_id,
			TBLCol.question_id,
			TBLCol.answer_id,
		)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS %s (
				%s BIGINT UNSIGNED NOT NULL,
				%s BIGINT UNSIGNED NOT NULL,
				%s BIGINT UNSIGNED NOT NULL
			);
		""" % response_mappings_query_data)

	@staticmethod
	def add_delete_constraints_if_needed(cursor: CursorBase) -> None:
		fk_insertion_data = [
			(
				TBL.AnswerChoices,
				"fk_answer_choices_to_question_id",
				TBLCol.question_id,
				TBL.Questions,
				TBLCol.question_id,
			),
			(
				TBL.ResponseMappings,
				"fk_response_mappings_to_response_id",
				TBLCol.response_id,
				TBL.Responses,
				TBLCol.response_id,
			),
			(
				TBL.ResponseMappings,
				"fk_response_mappings_to_question_id",
				TBLCol.question_id,
				TBL.Questions,
				TBLCol.question_id,
			),
			(
				TBL.ResponseMappings,
				"fk_response_mappings_to_answer_id",
				TBLCol.answer_id,
				TBL.AnswerChoices,
				TBLCol.answer_id,
			),
		]
		for query_data in fk_insertion_data:
			try:
				cursor.execute("""
					ALTER TABLE %s
					ADD CONSTRAINT %s FOREIGN KEY (%s)
					REFERENCES %s (%s)
					ON DELETE CASCADE;
				""" % query_data)
			except mysql.connector.errors.IntegrityError:
				# integrity error means we ran into the duplicate key,
				# so table already had it
				pass

	@staticmethod
	def populate_courses_table_with_new_courses(cursor: CursorBase) -> None:
		cursor.execute(
			"SELECT %s, %s FROM %s" %
			(TBLCol.course_number, TBLCol.course_name, TBL.Courses)
		)
		courses_already_in_db = cursor.fetchall()
		course_to_add_list = [
			course for course in mit_courses
			if course not in courses_already_in_db
		]
		if len(course_to_add_list) > 0:
			course_population_data = (
				TBL.Courses,
				TBLCol.course_number,
				TBLCol.course_name,
				",".join(
					["(" + ",".join(
						[quote(s) for s in course_row]
					) + ")" for course_row in course_to_add_list]
				),
			)
			cursor.execute(
				"INSERT INTO %s (%s, %s) VALUES %s;" %
				course_population_data
			)


initialize_database = _DBInitializer.initialize_database
