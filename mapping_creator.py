import utils
import os
import database
from typing import List, Tuple, Dict
from custom_types import SQuestion, SChoice, QID, AID, QSID


class QuestionAnswersToVectorMap:
	"""
	for a given question, map each of its choices to a vector and ensure
	all the vectors have the same dimensions.
	"""

	def __init__(
			self,
			qid: QID,
			answers: List[Tuple[AID, SChoice]],
			dimension: int = 1) -> None:
		utils.assert_valid_db_id(qid, 'question_id')
		QuestionAnswersToVectorMap.assert_valid_answer_input(answers)
		QuestionAnswersToVectorMap.assert_valid_dimension(dimension)
		self.qid = qid
		self.dimension = dimension
		self.answer_set = set(answer for _, answer in answers)
		self.answer_id_to_answer_map = {aid: answer for aid, answer in answers}
		self.map = {aid: None for aid in self.answer_id_to_answer_map}

	def is_fully_mapped(self) -> bool:
		return any([self.map[answer] is None for answer in self.map])

	def map(self, answer: str, vector: List[int]) -> None:
		assert answer in self.answer_set, 'the answer must be in the map'
		QuestionAnswersToVectorMap.assert_valid_vector(vector, self.dimension)
		aid = self.answer_id_to_answer_map[answer]
		self.map[aid] = vector

	def reset_dimension(self, dimension: int) -> None:
		QuestionAnswersToVectorMap.assert_valid_dimension(dimension)
		if self.dimension == dimension: return
		self.dimension = dimension
		self.map = {aid: None for aid in self.answer_id_to_answer_map}

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
			assert type(aid) == int, \
				'the aid must be an integer. %s' % fail_str
			assert type(choice) == str, \
				'choice must be a string. %s' % fail_str

	@staticmethod
	def assert_valid_dimension(dimension: int) -> None:
		assert type(dimension) == int, 'dimension must be an integer'

	@staticmethod
	def assert_valid_vector(vector: List[int], dimension: int) -> None:
		assert type(vector) == list, 'vector must be a list'
		for el in vector:
			assert type(el) == int, \
				'vector must be a list of integers. failing at -> %s' % str(el)
		assert len(vector) == dimension, 'vector must match the dimension'

	def get_writable(self) -> str:
		# todo
		pass


class MappingSetCreator:
	"""
	class to create mappings for question sets that are already created.
	essentially, for each question in the question set, we map each of the
	choices to that questions to its own specific vector, which will
	eventually be used in the classifier.
	"""

	def __init__(self, qsid: int, ms_name: str = None):
		self.qsid = QSID(qsid)
		self.name = ms_name
		self.question_map, self._resolver_map, self.qid_to_question_map = \
			MappingSetCreator.parse_qs(database.load_question_set(qsid))

	@staticmethod
	def parse_qs(
			qs: List[Tuple[QID, SQuestion, List[Tuple[AID, SChoice]]]]
	) -> Tuple[
		Dict[QID, QuestionAnswersToVectorMap],
		Dict[QID or SQuestion, QID],
		Dict[QID, SQuestion]
	]:
		question_map, resolver_map, qid_to_question_map = {}, {}, {}
		for qid, question, answers in qs:
			resolver_map[qid] = qid
			resolver_map[question] = qid
			qid_to_question_map[qid] = question
			# creator is expected to reset the dimension and populate mapping
			question_map[qid] = QuestionAnswersToVectorMap(qid, answers)
		return question_map, resolver_map, qid_to_question_map

	def __getitem__(self, item):
		return self.question_map[self._resolver_map[item]]

	def __iter__(self):
		for qid in self.question_map:
			yield qid, self.qid_to_question_map[qid]

	def get_writable(self) -> str:
		# todo
		pass


class QuestionToVectorAnswersMap:
	"""
	Allow to create a mapping for a given question
	A QMapping contains:
	- question_id
	- choices
	- dimensions
	- map

	The map is a dictionary that maps each answer to a given
	vector representation. This vector has the dimensions
	given when calling the __init__ method. Eventually, there
	will be a way to generate a string that can be stored into
	the text format.
	"""

	def __init__(
			self,
			question_id: str,
			answers: List[str],
			dimension: int = 1) -> None:
		"""
		map the question id to a set of vector as response. we
		detach the Mapping object from knowing what the true
		of the question is.
		:param answer_count: the number of choices for this question
		:param question_id: the id of the question
		:param dimension: how many dimension the vector for each answer will be
		"""
		assert isinstance(question_id, int), 'question_id must be a string'
		assert type(answers) == list, 'choices must be a list'
		assert type(dimension) == int, 'dimension must be an integer'
		self.question_id = question_id
		self.answers = answers
		self.dimension = dimension
		self.map = {}

	def __setitem__(self, answer: str, vector: List[int]) -> None:
		"""
		map the question to this vector, which must be a list of length dimension
		"""
		assert type(answer) == str, 'the answer must be a string'
		assert type(vector) == list, 'vector must be a list'
		assert len(vector) == self.dimension, 'the vector must match the mapping\'s dimension'
		assert all([type(n) == int for n in vector]), 'the elements in the vector must be integers'
		self.map[answer] = vector

	def is_fully_mapped(self) -> bool:
		"""
		check if every answer has been mapped to a vector
		"""
		return None not in [
			self.map.get(answer, None) for answer in self.answers
		]

	def get_writable(self):
		err_msg = 'cannot generate the writable without being fully mapped'
		assert self.is_fully_mapped(), err_msg
		return self.question_id + '\n' + ';'.join([
			','.join([str(i) for i in self.map[answer]])
			for answer in self.answers
		])


class QuestionSetMapper:
	"""
	mapping question_ids to questions and vector choices

	this is simply to convert the questions that we read
	from the question file into a format that can be easily
	parsed (i.e. vectors)
	"""

	def __init__(self, q_file_lines: List[str]) -> None:
		# each set of 3 lines must be a question
		self.map = {}
		for i in range(0, len(q_file_lines), 3):
			self.create_map_for_question(q_file_lines[i:i + 3])

	def create_map_for_question(self, row: List[str]) -> None:
		assert len(row) == 3, 'each question must have 3 components'
		id, question, answers = row
		self.map[id] = {'question': question, 'choices': answers.split(',')}

	def get_mapped_question_and_answer(self, question_id: str):
		return self.map[question_id]['question'], self.map[question_id]['choices']

	def __iter__(self):
		for question_id in self.map:
			yield question_id


class QuestionSetMapCreator:
	"""
	create mappings that will be added to
	the data_format folder for a question set

	this class helps with the creation questions, which will
	eventually be stored in the data_format folder.
	"""

	def __init__(self, question_set_id: str) -> None:
		self.question_set_id = question_set_id
		self.questions_mapper = QuestionSetMapCreator.load_questions(question_set_id)
		# map question_id's to a QuestionToVectorAnswersMap in self.mappings
		self.mappings = {}

	@staticmethod
	def load_questions(question_set_id: str) -> QuestionSetMapper:
		file_path = utils.get_data_format_path() + '/q-%s.txt' % question_set_id
		with open(file_path, 'r', encoding='utf-8') as question_file:
			question_set = QuestionSetMapper([
				line.strip('\n') for line in question_file.readlines()
			])
			question_file.close()
			return question_set

	@staticmethod
	def start_interactive_mapping_set_creation():
		"""
			this allows one to create a mapping set of questions by just responding to
			the terminal's prompts. It makes creating mappings a lot easier.
			"""
		while True:
			utils.log_prompt(
				'Please enter the question set id for which you want to create'
				' mappings or enter "%s" to quit:' % utils.EXIT_PROMPT
			)
			question_set_id = input()
			if question_set_id == utils.EXIT_PROMPT:
				utils.log_notice('quitting...!')
				return False
			try:
				msc = QuestionSetMapCreator(question_set_id)
			except FileNotFoundError:
				utils.log_error('Your question set was not found. Try again.')
				continue
			break
		msc.set_mappings_interactively()
		# once done with setting the mappings for all questions, we ensure
		# the user is able to see everything one more time and then confirm
		if utils.r_input_yn(
				'would you like to see the mappings before saving?'
		):
			utils.log_notice(msc.get_writable())
		if utils.r_input_yn(
				'do you want to store this set of mapping?'
		):
			msc.store_into_data_format()
		utils.log_prompt('you are done!')

	def set_mappings_interactively(self) -> None:
		for question_id in self.questions_mapper:
			question, answers = self.questions_mapper.get_mapped_question_and_answer(question_id)
			mapping = QuestionSetMapCreator.create_mapping_interactively(
				question_id,
				question,
				answers
			)
			self.mappings[question_id] = mapping

	@staticmethod
	def create_mapping_interactively(
			question_id: str,
			question: str,
			answers: List[str]) -> QuestionToVectorAnswersMap:
		"""
		set the mapping for one question interactively by answering
		to the terminal
		todo - there should also be a way to just set the mapping programmatically
		"""
		utils.log_prompt('The current question is:')
		utils.log_notice(utils.Color.yellow(question))
		utils.log_prompt('and the current set of choices are ')
		utils.log_notice(str(answers))
		if utils.r_input_yn(
				'would you like to use a one-hot encoding here?'
		):
			dimension = len(answers)
			qmap = QuestionToVectorAnswersMap(question_id, answers, dimension)
			for i in range(dimension):
				qmap[answers[i]] = [1 if j == i else 0 for j in range(dimension)]
			utils.log_prompt('You are now done with this question!\n')
			return qmap

		dimension = int(utils.r_input(
			'Choose a dimension. This must be an integer!\n',
			choices=utils.isinteger,
			invalid_input_message='Invalid answer. You must enter an integer.'))
		utils.log_prompt([
			'Ensure that each of your responses have %d numbers.' % dimension,
			'In the following section, enter vectors as a comma separated ',
			'list of integers. For 1 dimension, just enter an integer.',
		])
		qmap = QuestionToVectorAnswersMap(question_id, answers, dimension)
		for answer in answers:
			qmap[answer] = QuestionSetMapCreator.generate_mapping_for_answer(answer, dimension)
		utils.log_prompt('You are now done with this question!\n')
		return qmap

	@staticmethod
	def generate_mapping_for_answer(answer: str, dimension: int):
		prompt_reminder, remind = utils.Color.prompt(
			'remember to enter only numbers in comma separated value '
			'to match the dimension %d. ' % dimension
		), False
		text = \
			utils.Color.prompt('Enter the mapping for answer "') + \
			utils.Color.yellow(answer) + \
			utils.Color.prompt('":\n')
		while True:
			prompt_text = prompt_reminder if remind else '' + text
			mapping, remind = input(prompt_text), True
			try:
				mapping = [int(el) for el in mapping.split(',')]
				assert len(mapping) == dimension, 'answer must match dimension'
			except ValueError:
				utils.log_error(
					'please, enter only numbers in comma separated format'
				)
				continue
			except AssertionError:
				utils.log_error(
					'please, ensure that the numbers match the dimension'
				)
				continue
			except:
				utils.log_error(
					'an unknown error occurred, ensure the inputs are correct'
				)
				continue
			break
		return mapping

	def store_into_data_format(self) -> None:
		mapping_id = utils.generate_unique_id(
			QuestionSetMapCreator.get_existing_mapping_set_ids(self.question_set_id),
			utils.generate_mapping_id
		)
		file_name = 'm-%s-%s.txt' % (self.question_set_id, mapping_id)
		file_path = utils.get_data_format_path() + '/%s' % file_name
		with open(file_path, 'w') as question_file:
			question_file.write(self.get_writable())
			question_file.close()
		utils.log_prompt('your question mapping set file has been stored as:')
		utils.log_notice(file_name)

	@staticmethod
	def get_existing_mapping_set_ids(question_set_id: str):
		return set([
			file_name[6:].strip('.txt')
			for file_name in os.listdir(utils.get_data_format_path())
			if file_name[:5] == 'm-%s' % question_set_id
		])

	def get_writable(self) -> str:
		return '\n'.join([
			self.mappings[question_id].get_writable()
			for question_id in self.questions_mapper
		])


if __name__ == '__main__':
	QuestionSetMapCreator.start_interactive_mapping_set_creation()
