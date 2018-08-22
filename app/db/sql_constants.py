from typing import Set

class TBL:
	"""
	A table class to store all table variables
	"""
	Questions = "Questions"
	AnswerChoices = "AnswerChoices"
	Courses = "Courses"
	Responses = "Responses"
	ResponseMappings = "ResponseMappings"


class TBLCol:
	"""
	Table column names
	"""
	question_id = "qid"
	question = "question"
	question_type = "question_type"
	question_answer_type = "answer_type"
	answer_id = "aid"
	choice = "choice"
	vector = "vector"
	course_number = "cn"
	course_name = "course_name"
	response_id = "rid"
	time_created = "time_created"
	course_id = "cid"
	response_salt = "salt"


class TableColumns:
	def get_columns(self):
		return NotImplemented


class Questions(TableColumns):
	def get_columns(self):
		return (
			TBLCol.question_id,
			TBLCol.question,
			TBLCol.question_type,
			TBLCol.question_answer_type,
		)


class AnswerChoices(TableColumns):
	def get_columns(self):
		return (
			TBLCol.answer_id,
			TBLCol.question_id,
			TBLCol.choice,
			TBLCol.vector,
		)


class Courses(TableColumns):
	def get_columns(self):
		return TBLCol.course_id, TBLCol.course_number, TBLCol.course_name


class Responses(TableColumns):
	def get_columns(self):
		return (
			TBLCol.response_id,
			TBLCol.course_number,
			TBLCol.time_created,
			TBLCol.response_salt,
		)


class ResponseMappings(TableColumns):
	def get_columns(self):
		return TBLCol.response_id, TBLCol.question_id, TBLCol.answer_id


class DBType:
	@staticmethod
	def get_types() -> Set[str]:
		return NotImplemented

	@classmethod
	def is_valid(cls, s: str) -> bool:
		if not isinstance(s, str):
			return False
		return s in cls.get_types()


class QuestionTypes(DBType):
	"""
	in this model, we have different types of questions to answer to
	different needs. this class helps shed light into those types.
	"""

	# this type of question serves to identify a given user's place
	# in society. the solutions to these questions are used to match
	# a set of answer with a type of person. when the analyzing phase
	# starts, this will be used to figure draw some conclusions.
	# NOT USED WHEN PREDICTING
	Identification = "identification"

	# the regularizing questions is to help the ML model solve
	# unavoidable types of people. for instance, people of a given
	# age will tend to answer in a specific way. these questions
	# will help the model making that difference. they are similar
	# to identification questions except they group people into
	# unavoidable types of people.
	# USED WHEN PREDICTING
	Regularizing = "regularizing"

	# these questions are the ones asked in the asked in the quiz
	# portion. see question criteria for more details on these.
	# USED WHEN PREDICTING
	Quiz = "quiz"

	@staticmethod
	def get_types() -> Set[str]:
		return {
			QuestionTypes.Identification,
			QuestionTypes.Regularizing,
			QuestionTypes.Quiz,
		}


class QuestionAnswerTypes(DBType):
	"""
	different types of answers can be used for various questions.
	this class helps with setting the correct type of question.
	"""

	# most questions will be multiple choice. their answers thus will
	# be represented with specific vectors using the vector column
	# in the AnswerChoices table
	MultipleChoice = "MultipleChoice"

	# some questions will ask for an input value that can only be an
	# integer. this type is for those questions.
	IntegerInput = "IntegerInput"

	# it could be possible that the answer to some questions is a
	# floating number. this type is for those questions.
	FloatInput = "FloatInput"

	@staticmethod
	def get_types() -> Set[str]:
		return {
			QuestionAnswerTypes.MultipleChoice,
			QuestionAnswerTypes.IntegerInput,
			QuestionAnswerTypes.FloatInput,
		}
