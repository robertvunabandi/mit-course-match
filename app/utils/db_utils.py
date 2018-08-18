from typing import List, Iterable, Hashable, Callable


def convert_to_query_values(
	array: List[Iterable[Hashable]],
	component_fxn: Callable = None,
) -> str:
	"""
	given a list of lists (ideally tuples) of hashable, this method
	converts them in a string such that the string can be used after
	an "INSERT INTO tbl VALUES {output} ..." ({output} is the output
	of this method).
	:param array: a list of iterables of hashable
	:param component_fxn:
		a function that is called on every values in the sub-iterables
	:return: str
	"""
	if component_fxn is None:
		component_fxn = lambda arg: arg
	return ", ".join([
		"(" + ", ".join([str(component_fxn(el)) for el in item]) + ")"
		for item in array
	])
