from typing import Iterable, List, Tuple
import utils
import os
import database


class Question:
	"""
	question object to easily create questions
	"""

	def __init__(self, question: str, answers: Iterable = None) -> None:
		assert type(question) == str, \
			'question must be a string -> ' + str(question)
		if answers is None:
			answers = set()
		else:
			Question.assert_valid_answer_list(answers)
		self.question = question
		self.answers = set(utils.clean_string(answer) for answer in answers)

	def add_answer(self, answer: str) -> None:
		Question.assert_valid_answer(answer)
		self.answers.add(utils.clean_string(answer))

	@staticmethod
	def assert_valid_answer_list(answers: Iterable[str]) -> None:
		assert isinstance(answers, Iterable), \
			'answer must be iterable -> ' + str(answers)
		count, answer_set = 0, set()
		for answer in answers:
			Question.assert_valid_answer(answer)
			count += 1
			answer_set.add(answer)
		assert count > 1, \
			'question must have at least 2 answers choice'
		assert len(answer_set) > 1, \
			'question must have at least 2 answer choice'

	@staticmethod
	def assert_valid_answer(answer: str) -> None:
		assert type(answer) == str, \
			'each answer must be a string -> %s' % str(answer)
		assert len(answer.replace(' ', '')) > 0, \
			'cannot have an answer of empty spaces -> %s' % answer
		assert len(answer) > 0, \
			'cannot have empty string as answer -> %s' % answer

class QuestionSetCreator:
	"""
	class create questions that will be added to the data_format folder.
	todo - test if this works as expected
	"""
	def __init__(self) -> None:
		self.questions = []
		self.last_question_added = None

	def __len__(self):
		return len(self.questions)

	def add_question(self, question: str, answers: Iterable[str]) -> None:
		question_obj = Question(question, answers)
		self.questions.append(question_obj)
		self.last_question_added = question_obj

	def tolist(self) -> List[Tuple[str, List[str]]]:
		return [
			(question.question, question.answers)
			for question in self.questions
		]

	def store(self) -> None:
		database.store_question_set(self.tolist())


# todo - this is now wrong, update to using the above to store the questions
class Question:
	"""
	question object to easily create questions
	"""

	def __init__(self, id: str, question: str, answers: Iterable = None) -> None:

		assert type(id) == str, 'id must be a string'
		assert type(question) == str, 'question must be a string -> ' + str(question)
		if answers is None:
			answers = set()
		else:
			Question.assert_valid_answer_list(answers)
		self.question = question
		self.answers = set(Question.clean_answer(answer) for answer in answers)
		self.id = id

	@staticmethod
	def assert_valid_answer_list(answers: Iterable[str]) -> None:
		assert isinstance(answers, Iterable), 'answer must be iterable -> ' + str(answers)
		count, answer_set = 0, set()
		for answer in answers:
			Question.assert_valid_answer(answer)
			count += 1
			answer_set.add(answer)
		assert count > 1, 'you must have at least 2 answers choice per question'
		assert len(answer_set) == count, 'you must have unique answers'

	@staticmethod
	def assert_valid_answer(answer: str) -> None:
		assert type(answer) == str, 'each answer must be a string -> ' + str(answer)
		assert ',' not in answer, 'answer cannot contain commas -> %s' % answer
		assert len(answer.replace(' ', '')) > 0, 'cannot have an answer of empty spaces -> %s' % answer
		assert len(answer) > 0, 'cannot have empty string as answer -> %s' % answer

	def add_answer(self, answer: str) -> None:
		Question.assert_valid_answer(answer)
		self.answers.add(utils.clean_string(answer))

	def get_writable(self, ensure_count: bool = False) -> str:
		"""
		get a writable version of the question
		:param ensure_count: ensures that we have at least 2 answers
		"""
		if ensure_count:
			assert len(self.answers) > 1, 'you must have at least one answer'
		return '\n'.join([
			self.id,
			self.question,
			', '.join(self.answers)
		])



class QuestionSetCreator:
	"""
	class create questions that will be added
	to the data_format folder.
	"""

	def __init__(self) -> None:
		self.questions = []
		self.ids = set()
		self.last_question_added = None

	def __len__(self):
		return len(self.questions)

	def add_question(self, question: str, answers: Iterable[str]) -> None:
		id = utils.generate_unique_id(self.ids, utils.generate_question_id)
		question_obj = Question(id, question, answers)
		self.ids.add(id)
		self.questions.append(question_obj)
		self.last_question_added = question_obj

	@staticmethod
	def start_interactive_question_set_creation():
		"""
		this allows one to create a set of questions by just responding to
		the terminal's prompts. It's simpler to deal with.
		"""
		qsc = QuestionSetCreator()
		utils.log_prompt(
			"Creating a new question set: \nEnter as many questions as you'd "
			"like. Then, when done, you can save your question set. The id"
			"will be automatically generated. \n\n"
		)

		while utils.r_input_yn('Would you like to to add a question?'):
			question = utils.r_input('Enter your question as a string:\n')
			should_enter_answers_one_by_one = utils.r_input_yn(
				'would you like to enter the answers one by one?'
			)
			if not should_enter_answers_one_by_one:
				answers = utils.r_input(
					'enter the answers as a list of comma separated values:\n',
					choices=utils.create_asserter_to_boolean(
						Question.assert_valid_answer_list,
						parse_func=lambda ans: ans.split(',')
					)
				).split(',')
			else:
				answers = []
				while True:
					answer = utils.r_input(
						"Enter the next answer, or enter '%s' to move on. Make "
						"sure your answer has no commas:\n" % utils.EXIT_PROMPT,
						choices=utils.create_asserter_to_boolean(
							Question.assert_valid_answer
						)
					)
					if answer == utils.EXIT_PROMPT:
						break
					answers.append(answer)
			# save the question into the list
			try:
				qsc.add_question(question, answers)
				utils.log_prompt(
					'the last question you entered will appear as follows: '
				)
				utils.log_notice(qsc.last_question_added.get_writable())
			except AssertionError:
				err_msg = \
					'an error occurred! You probably entered bad formatted' \
					' answers or no answers at all. Follow all instructions.'
				utils.log_error(err_msg)

		if len(qsc) == 0:
			utils.log_error('aborting because you have no questions added!')
			return
		if utils.r_input_yn(
				'would you like to see the questions and answers so far?'
		):
			utils.log_notice(qsc.get_writable())
		if utils.r_input_yn('do you want to store this set of questions?'):
			try:
				qsc.store_into_data_format()
				utils.log_prompt('you are done!')
			except:
				utils.log_error(
					'An error occurred! Ensure all questions have 2 or '
					'more answers.'
				)

	def store_into_data_format(self) -> None:
		question_set_id = utils.generate_unique_id(
			QuestionSetCreator.get_existing_question_set_ids(),
			utils.generate_question_set_id
		)
		file_path = utils.get_data_format_path() + '/q-%s.txt' % question_set_id
		with open(file_path, 'w') as question_file:
			question_file.write(self.get_writable(ensure_count=True))
			question_file.close()
		print(
			'your question set file has been stored as '
			'q-%s.txt' % utils.Color.underline(question_set_id)
		)

	def get_writable(self, ensure_count: bool = False) -> str:
		"""
		:param ensure_count:
			ensures there's at least 2 answers for all questions
		"""
		return '\n'.join([
			question.get_writable(ensure_count) for question in self.questions
		])

	@staticmethod
	def get_existing_question_set_ids():
		return set([
			file_name[2:].strip('.txt')
			for file_name in os.listdir(utils.get_data_format_path())
			if file_name[:2] == 'q-'
		])


if __name__ == '__main__':
	QuestionSetCreator.start_interactive_question_set_creation()
