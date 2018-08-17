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


def deprecated(func: Callable) -> Callable:
	def method(*args, **kwargs):
		print('Warning: this method is deprecated.')
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


def quote(string: str, use_single=False) -> str:
	q = "\""
	if use_single:
		q = "'"
	return q + string + q


def assert_valid_db_id(id: int, idtype: str = None) -> None:
	idtype = 'id' if idtype is None else str(idtype)
	assert isinstance(id, int), \
		'%s must be an instance of integer got -> %s' % (idtype, id)
