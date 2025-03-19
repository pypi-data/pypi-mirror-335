from collections.abc import Mapping
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Callable, Dict, Tuple, Type, List
import inspect

import logging
import traceback



Key = TypeVar("Key")
Value = TypeVar("Value")



class Extractor(ABC):
	@abstractmethod
	def __call__(self, mapping: Mapping[Key, Value]) -> Any:
		pass



class Returner(Extractor, Generic[Value]):
	def __init__(self, value: Value) -> None:
		self.__value = value

	
	def __call__(self, _: Mapping[Key, Value]) -> Value:
		return self.__value



class KeyExtractor(Extractor, Generic[Key]):
	def __init__(self, key: Key) -> None:
		self.__key: Key = key


	def __call__(self, mapping: Mapping[Key, Value]) -> Value:
		return mapping[self.__key]



class FuncExtractor(Extractor):
	def __init__(self, func: Callable[..., Any]) -> None:
		self.__func = func


	def __call__(self, mapping: Mapping[str, Value]) -> Any:
		requiredParams = self.__getRequiredParams(mapping)
		return self.__func(**requiredParams)

	
	def __getRequiredParams(
		self, mapping: Mapping[str, Value]
	) -> Dict[str, Value]:
		signature = inspect.signature(self.__func)
		requiredArgNames = signature.parameters.keys()
		return {name: mapping[name] for name in requiredArgNames}



class PlainFuncExtractor(Extractor, Generic[Key, Value]):
	def __init__(self, func: Callable[[Mapping[Key, Value]], Any]) -> None:
		self.__func = func

	
	def __call__(self, mapping: Mapping[Key, Value]) -> Any:
		return self.__func(mapping)



class ExtractorWithDefault(Extractor):
	def __init__(self, main: Extractor, default: Extractor | Any) -> None:
		self.__main = main
		self.__default = default


	def __call__(self, mapping: Mapping[Key, Value]) -> Any:
		result = self.__main(mapping)
		if result:
			return result
		if isinstance(self.__default, Extractor):
			return self.__default(mapping)
		return self.__default



class ExtractorWithErrDefault(Extractor):
	def __init__(
		self,
		main: Extractor,
		default: Any | None = None,
		errorsToExcept: Tuple[Type[BaseException]] = (Exception,)
	) -> None:
		self.__main = main
		self.__default = default
		self.__errorsToExcept = errorsToExcept


	def __call__(self, mapping: Mapping[Key, Value]) -> Any | None:
		try:
			return self.__main(mapping)
		except self.__errorsToExcept as err:
			logging.debug(traceback.format_exc())
			logging.error(err)
			
			if isinstance(self.__default, Extractor):
				return self.__default(mapping)
			return self.__default

		

class TransformExtractor(Extractor):
	def __init__(
		self, main: Extractor, transformer: Callable[[Value], Any]
	) -> None:
		self.__main = main
		self.__transformer = transformer


	def __call__(self, mapping: Mapping[Key, Value]) -> Any:
		extracted = self.__main(mapping)
		return self.__transformer(extracted)



class MassExtractor(Extractor, Dict[str, Extractor]):
	def __init__(self, **kwargs: Extractor) -> None:
		super().__init__(**kwargs)


	def __call__(self, mapping: Mapping[Key, Value]) -> Dict[str, Value]:
		return {key: extractor(mapping) for key, extractor in self.items()}



class ExtractorChain(Extractor, List[Extractor]):
	def __init__(self, *args: Extractor) -> None:
		super().__init__(args)

	
	def __call__(self, mapping: Mapping[Key, Value]) -> Any:
		extracted = mapping
		for extractor in self:
			extracted = extractor(extracted)
		return extracted