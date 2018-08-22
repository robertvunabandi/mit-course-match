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
		return TBLCol.question_id, TBLCol.question


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
