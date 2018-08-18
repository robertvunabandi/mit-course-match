from typing import Dict, Iterable, Any, Generic, TypeVar

# I had to create this just to be able to inherit the generic type,
# inheriting from te generic type allows one to be able to use
# ValueResolver[Stuffs] in type hints (i.e. the brackets)
T = TypeVar('T')


class ValueResolver(Generic[T]):
	"""
	this is a dictionary that has many keys pointing to the same values
	this makes it easy to assign values to it and fetch those values
	"""

	def __init__(self):
		self.d: Dict[Any, Any] = {}

	def __setitem__(self, key, value):
		if isinstance(key, Iterable):
			for item in key:
				self.d[item] = value
		else:
			self.d[key] = value

	def __getitem__(self, item) -> Any:
		return self.d[item]


if __name__ == '__main__':
	a = ValueResolver()
	a[[1, 4, 3]] = -1
	print(a[1])
	print(a[3])
	print(a[4])
