from typing import Union, Callable, Iterable
from app.utils.log_util import Color


EXIT_PROMPT = "<Q>"


def r_input(
	prompt: str,
	choices: Union[Callable, Iterable] = None,
	invalid_input_message: str = None,
	color_outputs: bool = True
) -> str:
	"""
	input that is restricted (thus the "r") only to the choices given
	above
	:param prompt: message to show on the prompt
	:param choices: the choices we can use
	:param invalid_input_message:
		message to show when choices don't match
	:param color_outputs:
		if set to true, this boolean will color both the prompt and
		the error if an error happens
	"""
	if isinstance(choices, Iterable):
		choice_set = set([c for c in choices])
		is_among_choices_func = lambda choice: choice in choice_set
		if invalid_input_message is None:
			invalid_input_message = \
				"Please, enter only choices in the set " \
				"{%s}." % str(choice_set)
	elif choices is None:
		is_among_choices_func = lambda choice: True
	else:
		assert isinstance(choices, Callable), \
			"choices must either be Callable or Iterable"
		is_among_choices_func = choices

	if invalid_input_message is None:
		invalid_input_message = "Invalid choice entered."
	if color_outputs:
		invalid_input_message = Color.error(invalid_input_message)
		prompt = Color.prompt(prompt)
	while True:
		response = input(prompt)
		if not is_among_choices_func(response):
			print(invalid_input_message)
			continue
		break
	return response


def r_input_yn(prompt: str) -> bool:
	""" input only yes and no """
	return r_input(
		prompt + "y/n\n",
		choices=lambda x: x in {"y", "n"},
		invalid_input_message="Please, answer with only 'y' for yes and 'n' for no.",
		color_outputs=True
	) == "y"
