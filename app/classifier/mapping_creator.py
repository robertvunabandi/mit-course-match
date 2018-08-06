from app.classifier import utils
from app.db import database
from typing import List, Tuple, Dict
from app.classifier.custom_types import SQuestion, SChoice, QID, AID, QSID


class QuestionAnswersToVectorMap:
	"""
	for a given question, map each of its choices to a vector and ensure
	all the vectors have the same dimensions.
	"""

	def __init__(
			self,
			qid: QID,
			question: SQuestion,
			answers: List[Tuple[AID, SChoice]],
			dimension: int = 1) -> None:
		utils.assert_valid_db_id(qid, QID.__name__)
		QuestionAnswersToVectorMap.assert_valid_answer_input(answers)
		QuestionAnswersToVectorMap.assert_valid_dimension(dimension)
		self.qid = qid
		self.question = question
		self.dimension = dimension
		self.answer_set = set(answer for _, answer in answers)
		self.aid_to_answer_map = {aid: answer for aid, answer in answers}
		self.map = {aid: None for aid in self.aid_to_answer_map}

	@staticmethod
	def assert_valid_answer_input(answers: List[Tuple[AID, SChoice]]):
		"""
		this must be a list of tuple of integers (aid) and strings (choice)
		"""
		assert type(answers) == list, 'choices must be a list'
		for el in answers:
			fail_str = 'Failing at -> %s' % str(el)
			assert type(el) == tuple, \
				'each element in choices must be a tuple. %s' % fail_str
			assert len(el) == 2, \
				'each element must contain 2 element: ' \
				'(aid, choice). %s' % fail_str
			aid, choice = el
			assert isinstance(aid, int), \
				'the aid must be an integer. %s' % fail_str
			assert isinstance(choice, str), \
				'choice must be a string. %s' % fail_str

	@staticmethod
	def assert_valid_dimension(dimension: int) -> None:
		assert type(dimension) == int, 'dimension must be an integer'

	def is_fully_mapped(self) -> bool:
		return any([self.map[answer] is None for answer in self.map])

	def get_unmapped_choices(self):
		return list(filter(lambda answer_tup: not self.is_mapped(answer_tup[0]), list(self)))

	def is_mapped(self, answer: SChoice or AID) -> bool:
		return self[self.aid_from_aid_or_choice(answer)] is not None

	def __iter__(self) -> Tuple[AID, SChoice]:
		for aid in self.aid_to_answer_map:
			yield aid, self.aid_to_answer_map[aid]

	def __setitem__(self, answer: SChoice or AID, vector: List[int]) -> None:
		aid = self.aid_from_aid_or_choice(answer)
		QuestionAnswersToVectorMap.assert_valid_vector(vector, self.dimension)
		self.map[aid] = vector

	def __getitem__(self, answer: SChoice or AID) -> List[int]:
		return self.map[self.aid_from_aid_or_choice(answer)]

	def aid_from_aid_or_choice(
			self,
			answer: SChoice or AID) -> AID:
		if isinstance(answer, str):
			assert answer in self.answer_set, 'the answer must be in the map'
			return self.aid_to_answer_map[answer]
		elif isinstance(answer, int):
			assert answer in self.map, \
				'aid must be in the answer set -> %s' % str(answer)
			return AID(answer)
		raise TypeError('Expecting %s or %s, instead got %s' % (
			SChoice.__name__, AID.__name__, str(type(answer))
		))

	@staticmethod
	def assert_valid_vector(vector: List[int], dimension: int) -> None:
		assert type(vector) == list, 'vector must be a list'
		for el in vector:
			assert type(el) == int, \
				'vector must be a list of integers. failing at -> %s' % str(el)
		assert len(vector) == dimension, 'vector must match the dimension'

	def reset_dimension(self, dimension: int) -> None:
		QuestionAnswersToVectorMap.assert_valid_dimension(dimension)
		if self.dimension == dimension: return
		self.dimension = dimension
		self.reset_mapping()

	def reset_mapping(self):
		self.map = {aid: None for aid in self.aid_to_answer_map}

	def get_writable(self) -> str:
		return '\n'.join([
			repr(self.qid) + ' (' + self.question + ')',
			'\n'.join([
				''.join([
					repr(aid),
					' (',
					str(self.aid_to_answer_map[aid]),
					')',
					' -> ',
					str(self.map[aid])
				]) for aid in self.map
			]),
		])

	def tolist(self) -> List[Tuple[AID, List[int]]]:
		return [(aid, self[aid]) for aid in self.aid_to_answer_map]


class MappingSetCreator:
	"""
	class to create mappings for question sets that are already created.
	essentially, for each question in the question set, we map each of the
	choices to that questions to its own specific vector, which will
	eventually be used in the _classifier.
	"""

	def __init__(self, qsid: int, ms_name: str = None) -> None:
		utils.assert_valid_db_id(qsid, QSID.__name__)
		self.qsid = QSID(qsid)
		self.name = None
		self.set_name(ms_name)
		self.qatv_map, self._to_qid, self.qid_to_question_map = \
			MappingSetCreator.parse_qs(database.load_question_set(qsid))

	def set_name(self, ms_name: str = None):
		if ms_name is None:
			self.name = ms_name
			return
		assert isinstance(ms_name, str), 'name must be a string'
		self.name = None if len(ms_name) == 0 else ms_name

	@staticmethod
	def parse_qs(
			qs: List[Tuple[QID, SQuestion, List[Tuple[AID, SChoice]]]]
	) -> Tuple[
		Dict[QID, QuestionAnswersToVectorMap],
		Dict[QID or SQuestion, QID],
		Dict[QID, SQuestion]
	]:
		qatv_map, map_to_qid, qid_to_question_map = {}, {}, {}
		for qid, question, answers in qs:
			map_to_qid[qid] = qid
			map_to_qid[question] = qid
			qid_to_question_map[qid] = question
			# creator is expected to reset the dimension and populate mapping
			qatv_map[qid] = QuestionAnswersToVectorMap(qid, question, answers)
		return qatv_map, map_to_qid, qid_to_question_map

	def __setitem__(
			self,
			question_identifier: Tuple[QID or SQuestion, AID or SChoice],
			vector: List[int]) -> None:
		assert type(question_identifier) == tuple, \
			'question_identifier must be a ' \
			'tuple -> %s' % str(question_identifier)
		question, choice = question_identifier
		self.qatv_map[self._to_qid[question]][choice] = vector

	def __getitem__(
			self,
			identifier: QID or SQuestion) -> QuestionAnswersToVectorMap:
		return self.qatv_map[self._to_qid[identifier]]

	def get_uncompleted_questions(self):
		return list(filter(
			lambda question_tup: len(question_tup[2]) > 0,
			[
				(qid, question, self[qid].get_unmapped_choices())
				for qid, question in self
			]
		))

	def __iter__(self) -> Tuple[QID, SQuestion]:
		for qid in self.qatv_map:
			yield qid, self.qid_to_question_map[qid]

	def reset_dimension_for_question(
			self,
			question_identifier: QID or SQuestion,
			dimension: int) -> None:
		self[question_identifier].reset_dimension(dimension)

	def get_writable(self) -> str:
		return '\n---\n'.join([
			self.qatv_map[qid].get_writable() for qid in self.qatv_map
		])

	def store(self):
		database.store_mapping_set(self.tolist(), self.qsid, self.name)

	def tolist(self) -> List[Tuple[QID, SQuestion, List[Tuple[AID, List[int]]]]]:
		return [
			(qid, question, self[qid].tolist())
			for qid, question in self
		]


def start_interactive_mapping_set_creation():
	"""
	this allows one to create a mapping set of questions by just responding to
	the terminal's prompts. It makes creating mappings a lot easier.
	"""

	question_set_id = utils.r_input(
		'Please enter the question set id for which you want to create'
		' mappings, or enter "%s" to quit: ' % utils.EXIT_PROMPT,
		choices=lambda s: utils.isinteger(s) or s == utils.EXIT_PROMPT
	)
	if question_set_id == utils.EXIT_PROMPT:
		utils.log_notice('quitting...!')
		return
	try:
		msc = MappingSetCreator(int(question_set_id))
	except AssertionError:
		utils.log_error('Your question set was not found.')
		utils.log_notice('quitting...!')
		return
	ms_name = utils.r_input(
		'Enter a name for your new mapping set, or leave '
		'it blank for something random: '
	)
	msc.set_name(ms_name)
	for qid, question, choice_list in msc.get_uncompleted_questions():
		utils.log_prompt(
			"\nYou will now create vector mappings for the "
			"question '%s'." % question
		)
		dimension = int(utils.r_input(
			'now, enter a dimension for the vectors in this question: ',
			choices=lambda s: utils.isinteger(s),
			invalid_input_message='you must enter an integer'
		))
		msc.reset_dimension_for_question(qid, dimension)
		example = ','.join(['0' for _ in range(dimension)])
		should_map_choices = True
		while should_map_choices:
			for aid, choice in choice_list:
				vector = utils.r_input(
					"Enter a vector in csv format for the choice '%s'. Make "
					"sure that you have the dimensions %s. You may enter "
					"'%s' for example: " % (choice, str(dimension), example)
				)
				msc[(qid, aid)] = [int(el) for el in vector.split(',')]
			utils.log_prompt("here is a summary of the mappings you just did.")
			utils.log_notice("-\n%s\n-" % msc[qid].get_writable())
			should_map_choices = utils.r_input_yn('"Would you like to redo it?')
		utils.log_prompt('moving on...')
	if utils.r_input_yn('would you like to review all mappings?'):
		utils.log_notice(msc.get_writable())
	if utils.r_input_yn('would you like to store this mapping?'):
		msc.store()
	utils.log_prompt('you are done!')


if __name__ == '__main__':
	start_interactive_mapping_set_creation()
