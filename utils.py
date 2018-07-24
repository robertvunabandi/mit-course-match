"""
utilities used for dealing with data format managements
and anything else needed
"""
from typing import Callable, List, Set, Iterable, Union, Any
import random

ALPHANUMERIC_ALPHABET = list('0123456789abcdefghijklmnopqrstuvwxyz')
DIGITS_ALPHABET = list('0123456789')
LETTERS_ALPHABET = list('abcdefghijklmnopqrstuvwxyz')
EXIT_PROMPT = '<Q>'


def depreciated(func: Callable) -> Callable:
	def method(*args, **kwargs):
		print('Warning: this method is utilsdepreciated. Please, do not use it.')
		return func(*args, **kwargs)

	return method


def _random_character(alphabet: List[str]) -> str:
	return random.choice(alphabet)


def _generate_id(alphabet: List[str], length: int) -> str:
	return "".join([_random_character(alphabet) for _ in range(length)])


def generate_response_salt() -> str:
	return _generate_id(ALPHANUMERIC_ALPHABET, 10)


def generate_question_set_name() -> str:
	return _generate_id(ALPHANUMERIC_ALPHABET, 12)


def generate_mapping_set_name() -> str:
	return _generate_id(ALPHANUMERIC_ALPHABET, 8)


def generate_question_set_extension() -> str:
	return _generate_id(ALPHANUMERIC_ALPHABET, 4)


def generate_mapping_set_extension() -> str:
	return _generate_id(ALPHANUMERIC_ALPHABET, 4)


def generate_unique_id(
		existing_id_set: Set[str],
		generator_method: Callable) -> str:
	new_id = generator_method()
	while new_id in existing_id_set:
		new_id = generator_method()
	return new_id


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


def r_input(prompt: str,
			choices: Union[Callable, Iterable] = None,
			invalid_input_message: str = None,
			color: bool = True) -> str:
	"""
	input that is restricted (thus the 'r') only to the choices given above
	:param prompt: message to show on the prompt
	:param choices: the choices we can use
	:param invalid_input_message: message to show when choices don't match
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
	if color:
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
		color=True
	) == 'y'


def log_prompt(text: Union[str, List[str]]) -> None:
	if type(text) == list:
		for t in text:
			print(Color.prompt(t))
	else:
		print(Color.prompt(text))


def log_error(text: Union[str, List[str]]) -> None:
	if type(text) == list:
		for t in text:
			print(Color.error(t))
	else:
		print(Color.error(text))


def log_notice(text: Union[str, List[str]]) -> None:
	if type(text) == list:
		for t in text:
			print(Color.yellow(text))
	else:
		print(Color.yellow(text))


def isinteger(s: Any) -> bool:
	try:
		int(s)
		return True
	except ValueError:
		return False


def is_csv_string_vector(s: str, dimension: int = None) -> bool:
	if not isinstance(s, str):
		return False
	vector = s.split(',')
	for el in vector:
		if not isinteger(el):
			return False
	if dimension is None:
		return True
	return len(vector) == dimension


def create_asserter_to_boolean(
		asserter_func: Callable,
		parse_func: Callable = None) -> Callable:
	"""
	this creates a method for which when the asserter_function, which takes
	in just one element, passes, this returns true. Otherwise, it returns false.
	Before calling the asserter_function, we first parse using the parse_func
	when it's not none.
	:param asserter_func:
		a function that returns None and only asserts one element
	:param parse_func:
		a function that parses the input into something to be asserted
	"""
	assert isinstance(asserter_func, Callable)
	parse = parse_func
	if parse is None:
		parse = lambda x: x

	def func(elem: Any):
		try:
			asserter_func(parse(elem))
			return True
		except:
			return False

	return func


def clean_string(string: str) -> str:
	"""
	remove white spaces at beginning and end
	"""
	if len(string) == 0:
		return string
	if string[0] == ' ':
		return clean_string(string[1:])
	if string[-1] == ' ':
		return clean_string(string[:-1])
	return string


def quote(string: str) -> str:
	return "\"" + string + "\""


def assert_valid_db_id(id: int, idtype: str = None) -> None:
	idtype = 'id' if idtype is None else str(idtype)
	assert isinstance(id, int), \
		'%s must be an instance of integer got -> %s' % (idtype, id)
