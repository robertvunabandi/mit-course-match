from typing import Union, Iterable, List, Any


class Color:
	"""
	color inputs to print on the console.
	note that these aren't the true colors. These namings are aliases.
	"""
	PURPLE = "\033[95m"
	BLUE = "\033[94m"
	RED = "\033[91m"
	GREEN = "\033[92m"
	YELLOW = "\033[93m"
	BOLD = "\033[1m"
	UNDERLINE = "\033[4m"
	ENDC = "\033[0m"

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


def log(arg: Union[Any, List[Any]], tag: str = None) -> None:
	color_func = {
		"error": Color.error,
		"prompt": Color.prompt,
		"notice": Color.notice
	}.get(tag, lambda el: el)
	if isinstance(arg, Iterable):
		for sub_arg in arg:
			log(sub_arg, tag)
	else:
		print(color_func(str(arg)))


def log_prompt(text: Union[Any, List[Any]]) -> None:
	log(text, "prompt")


def log_error(text: Union[str, List[str]]) -> None:
	log(text, "error")


def log_notice(text: Union[str, List[str]]) -> None:
	log(text, "notice")
