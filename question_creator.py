import utils
import os
import database
from typing import Iterable, List, Tuple
from custom_types import QID, SQuestion, SChoice


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
		self.question = SQuestion(question)
		self.choices = set(
			SChoice(utils.clean_string(answer)) for answer in answers
		)

	def add_answer(self, answer: str) -> None:
		Question.assert_valid_answer(answer)
		self.choices.add(SChoice(utils.clean_string(answer)))

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
			'question must have at least 2 choices choice'
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

	def get_writable(self, ensure_count: bool = False) -> str:
		"""
		get a writable version of the question
		:param ensure_count: ensures that we have at least 2 choices
		"""
		if ensure_count:
			assert len(self.choices) > 1, 'you must have at least one answer'
		return '\n'.join([
			'Question: ' + self.question,
			'Answer choices: ' + ', '.join(self.choices)
		])


class QuestionSetCreator:
	"""
	class to create questions that will be added to the set of questions
	to the database. These questions will be mapped under a question set id.
	However, questions are created independent of the question set, which
	means that if a question set is deleted, the questions in the question
	set will stay in the database.
	"""

	def __init__(self, name: str = None) -> None:
		if name is not None:
			assert type(name) == str, 'name must be a string'
			name = None if len(name) == 0 else name
		self.name = name
		self.questions = []
		self.last_question_added = None

	def __len__(self):
		return len(self.questions)

	def add_question(self, question: str, answers: Iterable[str]) -> None:
		question_obj = Question(question, answers)
		self.questions.append(question_obj)
		self.last_question_added = question_obj

	def tolist(self) -> List[Tuple[SQuestion, List[SChoice]]]:
		return [
			(question.question, list(question.choices))
			for question in self.questions
		]

	def store(self) -> None:
		database.store_question_set(self.tolist(), self.name)

	def get_writable(self, ensure_count: bool = False) -> str:
		"""
		:param ensure_count:
			ensures there's at least 2 choices for all questions
		"""
		return '\n---\n'.join([
			question.get_writable(ensure_count) for question in self.questions
		])


def start_interactive_question_set_creation() -> None:
	"""
	this allows one to create a set of questions by just responding to
	the terminal's prompts. It's simpler to deal with.
	"""
	qs_name = utils.r_input(
		"Please enter a name for this question set of leave it blank for "
		"a randomly generated name.",
		choices=lambda x: x is None or type(x) == str
	)
	qsc = QuestionSetCreator(qs_name)
	utils.log_prompt(
		"Creating a new question set: \nEnter as many questions as you'd "
		"like. Then, when done, you can save your question set.\n\n"
	)
	# enter loop prompting to add questions until the
	# person added all questions
	while utils.r_input_yn('Would you like to to add a question?'):
		question = utils.r_input('Enter your question as a string:\n')
		utils.log_prompt("now, enter the choices to your question one by one.")
		answers = []
		while True:
			answer = utils.r_input(
				"Enter the next answer, or enter '%s' to move on. Make "
				"sure to have at least 2 choices:\n" % utils.EXIT_PROMPT,
				choices=utils.create_asserter_to_boolean(
					Question.assert_valid_answer
				)
			)
			if answer == utils.EXIT_PROMPT:
				break
			answers.append(answer)
		try:
			qsc.add_question(question, answers)
			utils.log_prompt(
				'the last question you entered is: '
			)
			utils.log_notice(qsc.last_question_added.get_writable())
		except AssertionError:
			err_msg = \
				'an error occurred! You probably entered bad formatted ' \
				'choices or not enough choices. Please follow all instructions.'
			utils.log_error(err_msg)
	# when done adding the question, do a last confirmation, then
	# store the question in the database
	if len(qsc) == 0:
		utils.log_error('aborting because you have no questions added!')
		return
	if utils.r_input_yn(
			'would you like to see the questions and choices so far?'
	):
		utils.log_notice(qsc.get_writable())
	if utils.r_input_yn('do you want to store this set of questions?'):
		qsc.store()
		utils.log_prompt('you are done!')
	else:
		utils.log_prompt("your questions weren't saved as you wished.")


if __name__ == '__main__':
	start_interactive_question_set_creation()
