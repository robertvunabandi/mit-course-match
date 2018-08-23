from app.db import database
from typing import List, Tuple
from app.classifier.custom_types import (
	SQuestion,
	SQuestionType,
	SQuestionAnswerType,
	SChoice,
	SVector,
	QID,
)


class QuestionStore:
	"""
	Store question and its answers and vector mapping one question
	at a time.
	"""

	@staticmethod
	def store_question(
		question: str,
		answer_choices: List[Tuple[str, List[int]]],
		q_type: SQuestionType = SQuestionType.type.quiz,
		qa_type: SQuestionAnswerType = SQuestionAnswerType.type.multiple_choice,
	) -> Tuple[QID, SQuestion, List[Tuple[SChoice, SVector]]]:
		QuestionStore.assert_valid_inputs(question, answer_choices, q_type, qa_type)
		return database.store_question(question, [
			(choice, ",".join([str(i) for i in vector]))
			for choice, vector in answer_choices
		])

	@staticmethod
	def assert_valid_inputs(
		question: str,
		answer_choices: List[Tuple[str, List[int]]],
		q_type: SQuestionType,
		qa_type: SQuestionAnswerType,
	) -> None:
		assert type(question) == str, "question must be a string"
		SQuestionType.assert_is_valid_question_type(q_type)
		SQuestionAnswerType.assert_is_valid_question_answer_type(qa_type)
		assert type(answer_choices) == list, "answer_choice must be a list"
		assert len(answer_choices) > 1, \
			"need at least 2 response_choices per question"
		vec_length = None
		for tup in answer_choices:
			assert len(tup) == 2, "each item in answer_choices must be a tuple"
			choice, vec = tup
			assert type(choice) == str, \
				"choice must a a string -> %s" % str(choice)
			assert type(vec) == list, \
				"vector must be a list -> %s" % str(vec)
			if vec_length is None:
				vec_length = len(vec)
			assert vec_length == len(vec), "vector must have same dimensions"
			for i in vec:
				assert type(i) == int or type(i) == float, \
					"items in vector must be numbers"
