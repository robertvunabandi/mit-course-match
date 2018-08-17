from typing import Union, Callable, Iterable, List, Any


class Color:
	"""
	color inputs to print on the console.
	note that these aren't the true colors. These namings are aliases.
	"""
	PURPLE = '\033[95m'
	BLUE = '\033[94m'
	RED = '\033[91m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	ENDC = '\033[0m'

	@staticmethod
	def c(text: str, color: str):
		return color + text + Color.ENDC

	@staticmethod
	def purple(text: str):
		return Color.c(text, color=Color.PURPLE)

	@staticmethod
	def blue(text: str):
		return Color.c(text, color=Color.BLUE)

	@staticmethod
	def red(text: str):
		return Color.c(text, color=Color.RED)

	@staticmethod
	def green(text: str):
		return Color.c(text, color=Color.GREEN)

	@staticmethod
	def yellow(text: str):
		return Color.c(text, color=Color.YELLOW)

	@staticmethod
	def bold(text: str):
		return Color.c(text, color=Color.BOLD)

	@staticmethod
	def underline(text: str):
		return Color.c(text, color=Color.UNDERLINE)

	@staticmethod
	def prompt(text: str):
		return Color.blue(text)

	@staticmethod
	def error(text: str):
		return Color.red(text)

	@staticmethod
	def notice(text: str):
		return Color.yellow(text)


def r_input(
	prompt: str,
	choices: Union[Callable, Iterable] = None,
	invalid_input_message: str = None,
	color_outputs: bool = True
) -> str:
	"""
	input that is restricted (thus the 'r') only to the choices given
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
			invalid_input_message = 'Please, enter only choices in the set {%s}.' % str(choice_set)
	elif choices is None:
		is_among_choices_func = lambda choice: True
	else:
		assert isinstance(choices, Callable), 'choices must either be Callable or Iterable'
		is_among_choices_func = choices

	if invalid_input_message is None:
		invalid_input_message = 'Invalid choice entered.'
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
		prompt + ' y/n\n',
		choices=lambda x: x in {"y", "n"},
		invalid_input_message="Please, answer with only 'y' for yes and 'n' for no.",
		color_outputs=True
	) == 'y'


def log(arg: Union[Any, List[Any]], tag: str = None) -> None:
	color_func = {
		'error': Color.error,
		'prompt': Color.prompt,
		'notice': Color.notice
	}.get(tag, lambda el: el)
	if isinstance(arg, Iterable):
		for sub_arg in arg:
			log(sub_arg, tag)
	else:
		print(color_func(str(arg)))


def log_prompt(text: Union[Any, List[Any]]) -> None:
	log(text, 'prompt')


def log_error(text: Union[str, List[str]]) -> None:
	log(text, 'error')


def log_notice(text: Union[str, List[str]]) -> None:
	log(text, 'notice')
