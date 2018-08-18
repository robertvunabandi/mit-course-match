from typing import Callable, List, Set
from random import choice


ALPHANUMERIC_ALPHABET = list('0123456789abcdefghijklmnopqrstuvwxyz')
DIGITS_ALPHABET = list('0123456789')
LETTERS_ALPHABET = list('abcdefghijklmnopqrstuvwxyz')


def _random_character(alphabet: List[str]) -> str:
	return choice(alphabet)


def _generate_id(alphabet: List[str], length: int) -> str:
	return "".join([_random_character(alphabet) for _ in range(length)])


def generate_response_salt() -> str:
	return _generate_id(ALPHANUMERIC_ALPHABET, 10)


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
