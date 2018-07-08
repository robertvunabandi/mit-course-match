import utils
from sql.sql import cursor, cnx
from sql.sql_constants import TBL, TBLCol
from typing import List, Callable, Tuple, Set
from custom_types import SChoice, SQuestion, QID, AID


# todo - add ways to prevent sql injections
# todo - add method to create the tables from scratch (if not exists)
# 		 so that online migration is easy
def _commit(method: Callable) -> Callable:
	"""
	decorator: calls cnx._commit() at the end of query in order to make the
	changes caused by the query to be permanent in the DB.
	:param method:
		method that calls an SQL query that makes changes to the data
	:return: method decorated with cnx.commit()
	"""

	def wrapper(*args, **kwargs):
		out = method(*args, **kwargs)
		cnx.commit()
		return out

	return wrapper


class _DB:
	"""
	DB provides ways to interact with the database without having to write
	sql queries. This abstracts away how the database works and what queries
	are called from the caller.
	"""

	@staticmethod
	@_commit
	def store_question_set(
			question_set: List[Tuple[str, List[str]]],
			qs_name: str = None) -> None:
		qs_name = _DB.create_or_make_qs_name_unique(qs_name)
		# create the question set
		data = (TBL.QuestionSets, TBLCol.question_set_name, qs_name)

		cursor.execute("INSERT INTO %s (%s) VALUES ('%s')" % data)
		# add the questions into the db
		# todo - this may throw an error in case the question exists, so handle that
		for question, choices in question_set:
			_DB.add_question(question, choices)
		# link the questions to the question set
		qsid = _DB.question_set_id(qs_name)
		data = (
			TBL.QuestionMappings,
			TBLCol.question_set_id,
			TBLCol.question_id,
			', '.join([
				"(%d, %d)" % (qsid, _DB.question_id(question))
				for question, _ in question_set
			])
		)
		cursor.execute("INSERT INTO %s (%s, %s) VALUES %s;" % data)

	@staticmethod
	def create_or_make_qs_name_unique(qs_name: str = None) -> str:
		"""
		fix the qs_name such that it's unique when stored in the db
		:param qs_name: the assigned name of the question set
		:return: updated qs_name such that it's unique
		"""
		qs_name_set = _DB.get_all_question_set_names()
		if qs_name is None or len(qs_name) == 0:
			return utils.generate_unique_id(
				qs_name_set, utils.generate_question_set_name
			)
		qs_extension = ""
		while qs_name + qs_extension in qs_name_set or len(qs_name) < 4:
			qs_extension = '-' + utils.generate_question_set_extension()
		return qs_name + qs_extension

	@staticmethod
	def get_all_question_set_names() -> Set[str]:
		data = (TBLCol.question_set_name, TBL.QuestionSets)
		cursor.execute('SELECT %s FROM %s' % data)
		return set(el[0] for el in cursor.fetchall())

	@staticmethod
	def question_set_id(qs_name: str) -> int or None:
		return _DB.get_unique_field(
			tbl=TBL.QuestionSets,
			id_col_name=TBLCol.question_set_id,
			target_col_name=TBLCol.question_set_name,
			target_value="'" + qs_name + "'"
		)

	@staticmethod
	def question_set_name(qsid: int) -> str or None:
		return _DB.get_unique_field(
			tbl=TBL.QuestionSets,
			id_col_name=TBLCol.question_set_name,
			target_col_name=TBLCol.question_set_id,
			target_value=str(qsid)
		)

	@staticmethod
	def question_id(question: str) -> int or None:
		return _DB.get_unique_field(
			tbl=TBL.Questions,
			id_col_name=TBLCol.question_id,
			target_col_name=TBLCol.question,
			target_value="'" + question + "'"
		)

	@staticmethod
	def get_unique_field(
			tbl: str,
			id_col_name: str,
			target_col_name: str,
			target_value: str) -> int or None:
		"""
		this method expects that the column target_col_name column has unique
		values such that the id_col_name column only has one id that can match
		the given target_value. Given that, this returns that unique id.
		:param tbl: table where this is coming from
		:param id_col_name: the column name of the id
		:param target_col_name: the target column name
		:param target_value: the target column value
		:return:
			integer id from the database for the row with the unique
			target_col_name equal to the target value
		"""
		data = (id_col_name, tbl, target_col_name, target_value)
		cursor.execute("SELECT %s FROM %s WHERE %s = %s" % data)
		row = cursor.fetchall()
		if len(row) == 0:
			return None
		return row[0][0]

	@staticmethod
	@_commit
	def add_question(question: str, choices: List[str]) -> None:
		if _DB.question_exists_in_db(question):
			raise ValueError('this question already exists in the database')
		data = (TBL.Questions, TBLCol.question, question)
		cursor.execute("INSERT INTO %s (%s) VALUES ('%s')" % data)

		question_id = _DB.question_id(question)
		data = (
			TBL.AnswerChoices,
			TBLCol.question_id,
			TBLCol.choice,
			', '.join([
				"(" + str(question_id) + ", '" + str(choice) + "')"
				for choice in choices
			])
		)
		cursor.execute("INSERT INTO %s (%s, %s) VALUES %s;" % data)

	@staticmethod
	def question_exists_in_db(question: str) -> bool:
		return _DB.question_id(question) is not None

	@staticmethod
	def answer_choices_for_question(question: str) -> List[str]:
		question_id = _DB.question_id(question)
		if question_id is None:
			raise ValueError('the question given does not exists')
		return _DB.answer_choices_for_question_id(question_id)

	@staticmethod
	def answer_choices_for_question_id(question_id: int) -> List[str]:
		data = (
			TBLCol.choice,
			TBL.AnswerChoices,
			TBLCol.question_id,
			question_id
		)
		cursor.execute("SELECT %s FROM %s WHERE %s = '%s'" % data)
		return [row[0] for row in cursor.fetchall()]

	@staticmethod
	def load_question_set(
			qsid: int
	) -> List[Tuple[QID, SQuestion, List[Tuple[AID, SChoice]]]]:
		data = (
			TBLCol.question_id,
			TBL.QuestionMappings,
			TBLCol.question_set_id,
			qsid,
		)
		assert _DB.question_set_name(qsid) is not None, \
			"there doesn't exist a question set with " \
			"this qsid -> %s" % str(qsid)
		cursor.execute("SELECT %s FROM %s WHERE %s = %s" % data)
		question_id_list = [row[0] for row in cursor.fetchall()]
		question_set_result = []
		for qid in question_id_list:
			data = (
				TBLCol.answer_id, TBLCol.choice, TBLCol.question,
				TBL.AnswerChoices, TBL.Questions,
				TBLCol.question_id, TBLCol.question_id,
				TBLCol.question_id, qid
			)
			cursor.execute("""
				SELECT a.%s, a.%s, b.%s 
				FROM %s a LEFT JOIN %s b 
				ON a.%s = b.%s 
				WHERE a.%s = %s
				""" % data)
			rows = cursor.fetchall()
			question = SQuestion(rows[0][2])
			question_set_result.append(
				(
					QID(qid),
					question,
					[(AID(aid), SChoice(choice)) for aid, choice, _ in rows],
				)
			)
		return question_set_result


if __name__ == '__main__':
	# cursor.execute('SELECT * FROM Questions WHERE question = \'coffee?\';')
	# print(cursor.fetchall())
	# DB.add_question('Ice Cream?', ['nah', 'YEAH', 'hell no'])
	# cursor.execute('SELECT aid, qid, choice FROM AnswerChoices;')
	# print(cursor.fetchall())
	print(_DB.answer_choices_for_question('coffee?'))

# todo - need to learn about cascade deletes and alter tables to allow it then implement it
# this may be unsustainable to build before moving on. These methods should be built as needed!
# todo - Methods to build:
# method to store a question set
# method to store a question set mapping
# get a list of courses
# get stored responses from the db, add count parameter
# questions from a question set by qsid or qs_name
# get the number of labelled responses
# get the number of responses in the db
# get all responses from a given question set
# get all the choices to a given question or data about it
# deleting methods: question, question_set, answer_mapping, responses
# todo - add a response token, which the owner can use to delete their response

# Exposing functions that will be used publicly
store_question_set = _DB.store_question_set
load_question_set = _DB.load_question_set
