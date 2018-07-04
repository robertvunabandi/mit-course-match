class TBL:
	"""
	A table class to store all table variables
	"""
	Questions = 'Questions'
	AnswerChoices = 'AnswerChoices'
	QuestionSets = 'QuestionSets'
	QuestionMappings = 'QuestionMappings'
	MappingSets = 'MappingSets'
	AnswerMappings = 'AnswerMappings'
	Courses = 'Courses'
	Responses = 'Responses'
	ResponseMappings = 'ResponseMappings'


class TBLCol:
	"""
	Table column names
	"""
	question_id = 'qid'
	question = 'question'
	answer_id = 'aid'
	choice = 'choice'
	question_set_id = 'qsid'
	question_set_name = 'qs_name'
	mapping_set_id = 'msid'
	mapping_set_name = 'ms_name'
	vector = 'vector'
	course_number = 'cn'
	course_name = 'course_name'
	response_id = 'rid'
	time_created = 'time_created'


class TableColumns:
	def get_columns(self):
		return NotImplemented


class Questions(TableColumns):
	def get_columns(self):
		return (TBLCol.question_id, TBLCol.question)


class AnswerChoices(TableColumns):
	def get_columns(self):
		return (TBLCol.answer_id, TBLCol.question_id, TBLCol.choice)


class QuestionSets(TableColumns):
	def get_columns(self):
		return (TBLCol.question_set_id, TBLCol.question_set_name)


class QuestionMappings(TableColumns):
	def get_columns(self):
		return (TBLCol.question_set_id, TBLCol.question_id)


class MappingSets(TableColumns):
	def get_columns(self):
		return (
			TBLCol.mapping_set_id,
			TBLCol.question_set_id,
			TBLCol.mapping_set_name
		)


class AnswerMappings(TableColumns):
	def get_columns(self):
		return (
			TBLCol.mapping_set_id,
			TBLCol.question_set_id,
			TBLCol.answer_id,
			TBLCol.vector
		)


class Courses(TableColumns):
	def get_columns(self):
		return (TBLCol.course_number, TBLCol.course_name)


class Responses(TableColumns):
	def get_columns(self):
		return (
			TBLCol.response_id,
			TBLCol.question_set_id,
			TBLCol.course_number,
			TBLCol.time_created
		)


class ResponseMappings(TableColumns):
	def get_columns(self):
		return (TBLCol.response_id, TBLCol.question_id, TBLCol.answer_id)