"""
these represent the questions asked during the quiz. these questions
can be updated, but they can't be removed. all questions are eternal
(as of Aug 20, 2018).
"""
from typing import List, Tuple
from app.classifier.custom_types import SQuestion, SChoice, SVector


class QuestionTypes:
	# most questions will be of type multiple choice
	MultipleChoice = "MultipleChoice"

	# for some questions, the user should be able to enter a number
	IntegerInput = "IntegerInput"

	# same as IntegerInput but with float
	FloatInput = "FloatInput"


QUESTIONS: List[Tuple[SQuestion, List[Tuple[SChoice, SVector]]]] = []

LEARNING_QUESTION = (
	"If you are an MIT student and have declared your major, what course did "
	"you choose? We will not use this information in calculating the "
	"prediction, but we will use this to make our predictor more accurate "
	"based on your answers to the questionnaire. Leave black if you have not "
	"declared your major at MIT."
)
# [ENSURE HAS ANSWER DURING TRAINING PHASE FOR TRAINING]
# Have a drop-down menu with all the COURSES."
